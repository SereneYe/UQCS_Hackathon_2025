import os
import json
import sys
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import models

from app.prompts.constants.content_analysis_guide import (
    CONTENT_ANALYSIS_SYSTEM_PROMPT
)
from app.prompts.constants.video_generation_guide import (
    VIDEO_PROMPT_REFINEMENT_SYSTEM_PROMPT
)
from app.prompts.constants.audio_generation_guide import (
    AUDIO_PROMPT_REFINEMENT_SYSTEM_PROMPT
)

from app.prompts.pdf_analysis import (
    get_pdf_analysis_system_prompt,
    get_pdf_analysis_user_message
)
from app.prompts.constants.video_categories_guide import get_video_category_context
from app.prompts.refinement import (
    get_video_refinement_user_message,
    get_audio_refinement_user_message
)


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

            # Use the imported system prompt for dual prompt generation
            system_prompt = CONTENT_ANALYSIS_SYSTEM_PROMPT

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
                        "analysis": {"main_theme": "Parse failed", "key_elements": [], "style_preference": "Unknown",
                                     "mood": "Unknown"},
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
            system_prompt = VIDEO_PROMPT_REFINEMENT_SYSTEM_PROMPT
            user_message = get_video_refinement_user_message(original_prompt, user_feedback)

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
            system_prompt = AUDIO_PROMPT_REFINEMENT_SYSTEM_PROMPT
            user_message = get_audio_refinement_user_message(original_prompt, user_feedback)

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

    def _get_video_category_context(self, category: Optional[models.VideoCategory]) -> str:
        """Get context-specific information based on video category"""
        return get_video_category_context(category)

    async def analyze_pdf_content_and_generate_prompts(
            self,
            user_prompt: str,
            pdf_content: str,
            category: Optional[models.VideoCategory] = None
    ) -> Dict[str, Any]:
        """
        Analyze PDF content and user prompt to generate video and audio prompts

        Args:
            user_prompt: User's specific instructions for the video
            pdf_content: Combined text content from PDF files
            category: Video category for context

        Returns:
            Dictionary containing analysis results and generated prompts
        """
        try:
            # Get category-specific context
            category_context = self._get_video_category_context(category)

            # Use the imported system prompt for PDF-based prompt generation
            system_prompt = get_pdf_analysis_system_prompt(category_context)

            # Limit PDF content to avoid token limits
            limited_pdf_content = pdf_content[:6000] if len(pdf_content) > 6000 else pdf_content

            # Use the imported user message formatter
            user_message = get_pdf_analysis_user_message(user_prompt, limited_pdf_content)

            # Call OpenAI API
            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000
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
                    "category": category.value if category else "general",
                    "pdf_processed": True,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured fallback
                return {
                    "success": True,
                    "data": {
                        "analysis": {
                            "main_theme": "Document-based content",
                            "key_elements": ["PDF content analysis"],
                            "important_details": ["Content extracted from uploaded documents"],
                            "style_preference": "Professional",
                            "mood": "Informative",
                            "pdf_summary": "PDF content processed"
                        },
                        "video_prompt": content,
                        "audio_prompt": content,
                        "enhanced_user_prompt": user_prompt
                    },
                    "raw_response": content,
                    "category": category.value if category else "general",
                    "pdf_processed": True,
                    "warning": "Response was not in expected JSON format"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "pdf_processed": False
            }

# Create a global OpenAI service instance with lazy loading
def get_openai_service():
    """Get OpenAI service instance"""
    if not hasattr(get_openai_service, '_instance'):
        get_openai_service._instance = OpenAIService()
    return get_openai_service._instance

openai_service = get_openai_service()
