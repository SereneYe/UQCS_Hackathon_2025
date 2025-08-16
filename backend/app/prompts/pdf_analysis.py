"""
OpenAI prompts for PDF content analysis and video generation
"""

def get_pdf_analysis_system_prompt(category_context: str) -> str:
    """
    Get PDF analysis system prompt with category context
    
    Args:
        category_context: Category-specific context for video creation
        
    Returns:
        Formatted system prompt string
    """
    return f"""You are a professional creative content analyst and prompt engineer specializing in document-based video creation. {category_context}

Your task is to:
1. Analyze the provided PDF content and user instructions
2. Extract key information, themes, and important details from the documents
3. Generate two specialized prompts based on this analysis:
   - Video generation prompt: For AI video generation models (VEO3), describing visual scenes, actions, styles
   - Audio generation prompt: Natural narrative text suitable for text-to-speech

Please return results in the following JSON format:
{{
    "analysis": {{
        "main_theme": "Primary theme from PDF content",
        "key_elements": ["Key element 1", "Key element 2", "Key element 3"],
        "important_details": ["Detail 1", "Detail 2"],
        "style_preference": "Recommended visual style",
        "mood": "Emotional atmosphere",
        "pdf_summary": "Brief summary of PDF content"
    }},
    "video_prompt": "Detailed video generation prompt incorporating PDF insights and user requirements",
    "audio_prompt": "Natural narrative script based on PDF content and user instructions",
    "enhanced_user_prompt": "Enhanced version of user prompt with PDF-specific details"
}}

Guidelines:
- Video prompts should describe specific visual elements from the PDF content
- Audio prompts should tell a coherent story using information from the documents
- Both prompts should align with the user's specific requirements
- Include specific names, dates, facts, and details from the PDF content"""

def get_pdf_analysis_user_message(user_prompt: str, pdf_content: str) -> str:
    """
    Format user message for PDF analysis
    
    Args:
        user_prompt: User's instructions for video creation
        pdf_content: Combined PDF content to analyze
        
    Returns:
        Formatted user message string
    """
    return f"""User Instructions: {user_prompt}

PDF Content to Analyze:
{pdf_content}

Please analyze this content and generate appropriate video and audio prompts that incorporate the key information from the documents while following the user's instructions."""