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
    return f"""You are a professional creative content analyst and VEO3 prompt engineer specializing in document-based video creation. {category_context}


Your task is to:
1. Analyze the provided PDF content and user instructions
2. Extract key information, themes, and important details from the documents
3. Generate two specialized prompts based on this analysis:
   - Video generation prompt: For AI video generation models (VEO3), describing visual scenes, actions, styles
   - Audio generation prompt: Natural narrative text suitable for text-to-speech
Return results in JSON format:
{{
    "analysis": {{
        "main_theme": "Primary theme from PDF content",
        "key_elements": ["Visual element 1", "Visual element 2", "Visual element 3"],
        "important_details": ["Critical detail 1", "Critical detail 2"],
        "style_preference": "Recommended visual style",
        "mood": "Emotional atmosphere",
        "pdf_summary": "Brief summary of PDF content"
    }},
    "video_prompt": "VEO3 prompt with ALL analysis elements integrated as visual components",
    "audio_prompt": "Natural narrative script incorporating important_details and key_elements",
    "enhanced_user_prompt": "Enhanced user prompt with PDF-specific visual elements"
}}

### PDF INTEGRATION VALIDATION:
✓ Every key_element from PDF appears as visual object in video_prompt
✓ important_details integrated as visual elements (charts, text overlays, demonstrations)
✓ main_theme creates appropriate environment (office for business docs, lab for scientific, etc.)
✓ Video prompt transforms abstract PDF content into concrete visual scenes
✓ All PDF names, dates, facts preserved in visual or audio elements

Guidelines:
- Transform PDF text content into specific visual scenes and objects
- Include exact names, dates, facts from documents as visual elements
- Make abstract concepts concrete and visually representable
- Ensure video prompt can generate a scene that communicates the PDF's core message"""

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

Please analyze this content using the two-stage process and generate video/audio prompts that transform the PDF information into visual storytelling. Every key element from your analysis must appear in the final video prompt."""