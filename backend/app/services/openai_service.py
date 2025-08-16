import os
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIService:
    """
    OpenAI GPT service for content analysis and prompt generation
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4"  # Using GPT-4 for compatibility
        self.client = None  # Will be initialized when needed
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        await self.close()
    
    async def close(self):
        """Properly close the OpenAI client"""
        if self.client is not None:
            try:
                await self.client.close()
            except Exception:
                # Ignore cleanup errors
                pass
            finally:
                self.client = None
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
                )
            # Create client with minimal config
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=30.0,
                max_retries=2
            )
        return self.client
    
    async def analyze_and_generate_prompts(
        self,
        user_input: str,
        user_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze user input and generate video and audio prompts
        
        Args:
            user_input: The user's input text/prompt
            user_context: Optional additional context
            
        Returns:
            Dictionary containing analysis results and generated prompts
        """
        try:
            
            # Construct the system prompt for dual prompt generation
            system_prompt = """You are a professional creative content analyst and prompt engineer. Your task is to:

1. Deeply understand the user's input content and intent
2. Generate two specialized prompts:
   - Video generation prompt: For AI video generation models **VEO3**, specifically describe visual scenes, actions, styles, etc.
   - Audio generation prompt: For text-to-speech, should be natural and fluent narrative text

Please return results in the following JSON format:
{
    "analysis": {
        "main_theme": "Content theme",
        "key_elements": ["Key element 1", "Key element 2"],
        "style_preference": "Style preference",
        "mood": "Emotional atmosphere"
    },
    "video_prompt": "Detailed video generation prompt, including scenes, actions, visual styles, etc.",
    "audio_prompt": "Natural narrative text suitable for speech conversion"
}

Note:
- Video prompts should specifically describe visual elements, avoid abstract concepts
- Audio prompts should be complete sentences suitable for reading aloud
- Both prompts should work together to form a complete content experience"""

            # Construct user message
            user_message = f"""User input: {user_input}"""
            if user_context:
                user_message += f"\n\nAdditional context: {user_context}"
            
            # Call OpenAI API
            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return {
                    "success": True,
                    "data": result,
                    "raw_response": content,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw content
                return {
                    "success": True,
                    "data": {
                        "analysis": {"main_theme": "Parse failed", "key_elements": [], "style_preference": "Unknown", "mood": "Unknown"},
                        "video_prompt": content,
                        "audio_prompt": content
                    },
                    "raw_response": content,
                    "warning": "Response was not in expected JSON format"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def refine_video_prompt(
        self,
        original_prompt: str,
        user_feedback: str
    ) -> Dict[str, Any]:
        """
        Refine video prompt based on user feedback
        
        Args:
            original_prompt: The original video prompt
            user_feedback: User's feedback or modification requests
            
        Returns:
            Dictionary containing refined prompt
        """
        try:
            system_prompt = """You are a video generation prompt expert. Based on user feedback, optimize and improve video generation prompts.
            
Requirements:
1. Maintain the core content of the original prompt
2. Make adjustments based on user feedback
3. Ensure the prompt is specific, clear, and suitable for AI video generation
4. Return the optimized prompt"""

            user_message = f"""Original prompt: {original_prompt}

User feedback: {user_feedback}

Please provide the optimized video generation prompt."""

            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            refined_prompt = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "refined_prompt": refined_prompt,
                "original_prompt": original_prompt,
                "user_feedback": user_feedback
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "refined_prompt": original_prompt  # Return original if refinement fails
            }
    
    async def refine_audio_prompt(
        self,
        original_prompt: str,
        user_feedback: str
    ) -> Dict[str, Any]:
        """
        Refine audio prompt based on user feedback
        
        Args:
            original_prompt: The original audio prompt
            user_feedback: User's feedback or modification requests
            
        Returns:
            Dictionary containing refined prompt
        """
        try:
            system_prompt = """You are an audio generation text expert. Based on user feedback, optimize and improve audio generation text.
            
Requirements:
1. Maintain the core content of the original text
2. Make adjustments based on user feedback
3. Ensure the text is natural and fluent, suitable for reading aloud
4. Return the optimized audio text"""

            user_message = f"""Original audio text: {original_prompt}

User feedback: {user_feedback}

Please provide the optimized audio generation text."""

            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            refined_prompt = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "refined_prompt": refined_prompt,
                "original_prompt": original_prompt,
                "user_feedback": user_feedback
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "refined_prompt": original_prompt  # Return original if refinement fails
            }

# Create a global OpenAI service instance with lazy loading
def get_openai_service():
    """Get OpenAI service instance"""
    if not hasattr(get_openai_service, '_instance'):
        get_openai_service._instance = OpenAIService()
    return get_openai_service._instance

openai_service = get_openai_service()
