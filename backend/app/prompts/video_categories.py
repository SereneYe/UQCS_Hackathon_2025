"""
Video category context prompts for different types of videos
"""

import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import models
from typing import Optional

def get_video_category_context(category: Optional[models.VideoCategory]) -> str:
    """
    Get context-specific information based on video category
    
    Args:
        category: Video category enum
        
    Returns:
        Category-specific context string
    """
    if category == models.VideoCategory.CONGRATULATION_VIDEO:
        return CONGRATULATION_VIDEO_CONTEXT
    elif category == models.VideoCategory.EVENT_PROPAGATION_VIDEO:
        return EVENT_PROPAGATION_VIDEO_CONTEXT
    else:
        return GENERAL_VIDEO_CONTEXT

# Category-specific contexts
CONGRATULATION_VIDEO_CONTEXT = """
You are creating a congratulation video. This should be:
- Celebratory and positive in tone
- Highlighting achievements and milestones
- Including warm, encouraging messages
- Suitable for occasions like graduations, promotions, anniversaries, or personal achievements
- Professional yet heartfelt
"""

EVENT_PROPAGATION_VIDEO_CONTEXT = """
You are creating an event propagation/promotional video. This should be:
- Informative and engaging
- Highlighting key event details (date, time, location, purpose)
- Creating excitement and encouraging attendance
- Clear call-to-action for registration or participation
- Professional and persuasive tone
"""

GENERAL_VIDEO_CONTEXT = "You are creating a general purpose video based on the provided content."