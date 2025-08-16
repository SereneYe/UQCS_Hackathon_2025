"""
Prompts for refining video and audio prompts based on user feedback
"""

def get_video_refinement_user_message(original_prompt: str, user_feedback: str) -> str:
    """
    Format user message for video prompt refinement
    
    Args:
        original_prompt: The original video prompt
        user_feedback: User's feedback or modification requests
        
    Returns:
        Formatted user message string
    """
    return f"""Original prompt: {original_prompt}

User feedback: {user_feedback}

Please provide the optimized video generation prompt."""

def get_audio_refinement_user_message(original_prompt: str, user_feedback: str) -> str:
    """
    Format user message for audio prompt refinement
    
    Args:
        original_prompt: The original audio prompt
        user_feedback: User's feedback or modification requests
        
    Returns:
        Formatted user message string
    """
    return f"""Original audio text: {original_prompt}

User feedback: {user_feedback}

Please provide the optimized audio generation text."""