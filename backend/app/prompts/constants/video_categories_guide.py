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
    elif category == models.VideoCategory.COMPANY_INTRODUCTION_VIDEO:
        return COMPANY_INTRODUCTION_VIDEO_CONTEXT
    else:
        return GENERAL_VIDEO_CONTEXT

# Category-specific contexts
CONGRATULATION_VIDEO_CONTEXT = """
You are creating a dynamic congratulation video card designed for VEO3 generation. This video should function as an animated greeting card with the following VEO3-optimized specifications:

**VISUAL STYLE & COMPOSITION:**
- Medium to close-up shots with warm, celebratory lighting
- Bright, cheerful color palette with golden hour warmth or soft studio lighting
- Shallow depth of field with bokeh effects for elegant background blur
- Style: Cinematic realism with enhanced saturation and warm tones

**SUBJECT & CHARACTERS:**
- Animated elements: floating confetti, balloons, sparkles, or paper streamers
- Optional: Friendly cartoon characters or mascots celebrating
- Elegant typography animation for congratulatory text
- Preset congratulatory messages that should appear on screen:
  * "Happy Birthday!" for birthday celebrations
  * "Congratulations!" for achievements and promotions
  * "Happy Anniversary!" for milestone anniversaries
  * "Well Done!" for personal accomplishments
  * "You Did It!" for graduations and completions

**CAMERA MOVEMENT & SCENES:**
- Gentle camera movements: slow dolly-in, soft pans, or subtle rotate
- Tracking shots following celebratory elements (confetti falling, balloons rising)
- Eye-level to slightly high angle for inclusive, warm perspective
- Smooth transitions between celebration elements

**BACKGROUND & ATMOSPHERE:**
- Celebration-themed backgrounds:
  * Birthday: Pastel balloons, cake, gift boxes with ribbon
  * Achievement: Office setting with awards, certificates, applause gesture
  * Anniversary: Elegant flowers, champagne glasses, heart motifs
  * Graduation: Academic caps, diplomas, university colors
- Warm ambient lighting with subtle particle effects (sparkles, light rays)
- Audio: Uplifting background music, gentle chimes, or celebratory sounds

**TECHNICAL SPECIFICATIONS:**
- 50mm lens for natural perspective
- High color saturation for vibrant celebration feel
- Smooth motion blur on animated elements
- Clean typography overlay with elegant font animations
- 8-second duration optimized for social media sharing

**PRESET ELEMENTS COMBINATIONS:**
- Birthday: Colorful balloons + "Happy Birthday!" text + confetti shower
- Promotion: Professional background + "Congratulations!" + achievement symbols
- Anniversary: Romantic elements + "Happy Anniversary!" + elegant transitions
- Personal Achievement: Success symbols + "Well Done!" + triumphant gestures
"""


EVENT_PROPAGATION_VIDEO_CONTEXT = """
You are creating a dynamic event promotional video optimized for VEO3 generation, designed to transform static event materials (PPT covers, posters, flyers) into engaging animated promotional content. This video should function as a motion poster with the following VEO3-optimized specifications:

**VISUAL STYLE & COMPOSITION:**
- Wide shot establishing the event poster/slide as main subject, then dynamic zoom-in to key details
- High-contrast cinematic lighting with dramatic shadows and highlights
- Style: Motion graphics realism with enhanced saturation and modern design aesthetics
- Color palette: Vibrant, eye-catching colors that amplify the original design elements
- Sharp focus on text elements with subtle motion blur on background graphics

**SUBJECT & ANIMATED ELEMENTS:**
- Primary Subject: Event poster, PPT slide, or promotional material as central focus
- Animated Typography: Event titles with kinetic text effects (sliding, fading, scaling)
- Dynamic Design Elements: Logos spinning, icons pulsing, decorative elements floating
- Particle Effects: Light rays, sparkles, or geometric shapes enhancing visual impact
- Layer Separation: Different design elements moving at varying depths for parallax effect

**ESSENTIAL INFORMATION DISPLAY (Must be clearly visible and animated):**
- **EVENT NAME**: Large, bold typography with dramatic entrance animation
- **DATE & TIME**: Prominently displayed with calendar flip or digital countdown effects
- **LOCATION**: Clear venue information with map pin or location icon animation
- **PURPOSE/THEME**: Core event message with emphasis through scaling or glow effects
- **CALL-TO-ACTION**: "Register Now", "Get Tickets", "Join Us" with pulsing or button-press animation

**CAMERA MOVEMENT & DYNAMICS:**
- Opening: Wide shot showing full poster/slide in elegant frame or modern display
- Primary Movement: Smooth dolly zoom-in focusing on key information hierarchy
- Secondary Movements: Gentle pan across different poster sections (left-to-right, top-to-bottom)
- Detail Shots: Close-up zoom-ins on date, location, and registration details
- Finale: Pull-back to wide shot with enhanced poster floating in dynamic space

**ANIMATION SEQUENCE STRUCTURE:**
1. **Establishing Shot** (0-1s): Full poster reveal with subtle entrance animation
2. **Title Sequence** (1-3s): Event name animation with dramatic typography effects
3. **Information Cascade** (3-5s): Date, time, location appearing in sequence
4. **Visual Enhancement** (5-7s): Design elements coming to life with motion
5. **Call-to-Action** (7-8s): Final registration/ticket information with urgency

**LIGHTING & ATMOSPHERE:**
- Studio lighting with soft key light eliminating harsh shadows on text
- Accent lighting: Neon glows, spotlights, or colored rim lighting matching event theme
- Background: Gradient transitions or subtle particle systems enhancing poster depth
- Mood: Energetic and anticipatory with professional polish
- Color Temperature: Adjust to event type (warm for social, cool for tech, vibrant for entertainment)

**TECHNICAL SPECIFICATIONS FOR MOTION POSTER EFFECT:**
- Lens: 50mm for natural perspective, wide-angle for full poster shots
- Depth of Field: Sharp focus on text, slight blur on decorative background elements
- Motion: Smooth easing on all animations (no jarring cuts or sudden movements)
- Typography: High contrast text with drop shadows or outlines for readability
- Resolution: Crisp text rendering with anti-aliasing for social media optimization

**EVENT TYPE PRESETS:**
- **Conference/Seminar**: Professional blue/gray palette, clean typography, corporate lighting
- **Music/Entertainment**: Dynamic colors, rhythm-based animations, concert-style lighting
- **Sports Event**: High-energy colors, bold typography, stadium lighting effects
- **Community/Social**: Warm colors, friendly animations, inviting soft lighting
- **Tech/Innovation**: Futuristic blues/whites, geometric animations, LED-style lighting

**AUDIO INTEGRATION:**
- Background: Event-appropriate music (corporate, upbeat, electronic, classical)
- Sound Effects: Whoosh sounds for text animations, chimes for information reveals
- Audio Sync: Animation beats aligned with music rhythm for professional feel
- Volume: Subtle background audio that doesn't overpower the visual message

**POSTER ENHANCEMENT TECHNIQUES:**
- **Layer Animation**: Separate foreground text from background graphics for depth
- **Element Isolation**: Individual design components (logos, icons, shapes) with independent motion
- **Text Hierarchy**: Primary information (event name) gets strongest animation emphasis
- **Color Boost**: Selective color enhancement to make key information pop
- **Edge Definition**: Subtle glows or outlines to separate text from complex backgrounds

**CALL-TO-ACTION OPTIMIZATION:**
- Registration/ticket information with urgency indicators (limited time, early bird, etc.)
- Contact details with phone/email icons that pulse or glow
- Website URLs with typing animation or QR code generation
- Social media handles with platform icon animations
- Physical location with map integration or GPS pin effects

**PROPAGATION & SHARING OPTIMIZATION:**
- Square (1:1) and vertical (9:16) format considerations for social media
- Duration: 8-15 seconds for optimal social media engagement
- Loop-friendly ending that connects smoothly to beginning
- High contrast and large text for mobile viewing
- Platform-specific optimizations (Instagram, TikTok, LinkedIn appropriate styling)

Remember: The goal is to take a static event material and breathe life into it while maintaining all critical information legibility and impact. Every animation should serve the purpose of drawing attention to key event details and driving registration/attendance action.
"""


COMPANY_INTRODUCTION_VIDEO_CONTEXT = """
You are creating an animated company introduction video optimized for VEO3 generation with image-to-video capability. This video transforms static company images (containing people, mascots, cartoon characters, or animals) into vivid, animated company presentations within 8 seconds. Follow these VEO3-optimized specifications:

**PRIMARY SUBJECT ANIMATION (Based on Input Image):**
- **Human Characters**: Corporate professionals, team members, or company representatives
  * Actions: Friendly waving, welcoming gestures, thumbs up, handshake motions
  * Facial Expressions: Warm smiles, professional confidence, approachable demeanor
  * Body Language: Open postures, pointing to company elements, presenting gestures
- **Mascot/Cartoon Characters**: Company mascots, branded characters, or animated representatives  
  * Actions: Energetic movements, logo presentations, playful interactions with company elements
  * Personality: Enthusiastic, friendly, memorable character-specific animations
  * Brand Integration: Holding or interacting with company logos, products, or services
- **Animals**: If company uses animal mascots or symbols
  * Actions: Species-appropriate movements (dog wagging, bird flying, cat stretching)
  * Company Connection: Wearing company colors, interacting with brand elements

**VISUAL STYLE & COMPOSITION:**
- Medium shot transitioning to close-up for personal connection
- Professional corporate lighting with warm, welcoming tone
- Style: Polished corporate realism with enhanced character animation
- Color Palette: Company brand colors prominently featured throughout
- Sharp focus on animated character with subtle corporate background elements

**8-SECOND ANIMATION SEQUENCE STRUCTURE:**
1. **Character Activation** (0-1s): Static image comes to life with gentle character movement
2. **Welcome Gesture** (1-2s): Character performs greeting (wave, smile, or welcoming pose)
3. **Company Introduction** (2-4s): Character gestures toward or presents company logo/name
4. **Key Message Delivery** (4-6s): Character emphasizes main company value or service
5. **Call-to-Action** (6-8s): Character points toward contact info or invites engagement

**COMPANY BRANDING INTEGRATION:**
- **Logo Animation**: Company logo appears dynamically (fade-in, scale, or slide)
- **Company Name**: Typography animation synchronized with character presentation
- **Welcome Messages** (Choose based on context):
  * "Welcome to [Company Name]!"
  * "Hi, I'm [Character/Mascot Name] from [Company]!"
  * "Discover [Company Name] - Your trusted partner!"
  * "Welcome to the [Company Name] family!"
  * "Let [Company Name] help you succeed!"
- **Tagline Integration**: Company slogan or mission statement with elegant text animation

**CAMERA MOVEMENT & DYNAMICS:**
- Opening: Static establishing shot matching input image composition
- Primary Movement: Gentle push-in (dolly forward) toward animated character
- Secondary: Slight tilt or pan following character gestures and movements
- Character Focus: Maintain eye-level perspective for personal connection
- Logo Reveal: Smooth transition to show company branding elements

**LIGHTING & ATMOSPHERE:**
- Corporate Studio Lighting: Clean, professional, shadow-controlled illumination
- Character Enhancement: Soft key lighting on character faces/features for warmth
- Brand Color Integration: Accent lighting matching company color scheme
- Background: Subtle gradient or corporate environment (office, branded space)
- Mood: Professional confidence combined with approachable friendliness

**CHARACTER-SPECIFIC ANIMATION PRESETS:**
- **Professional Humans**: 
  * Gentle head nods, confident smiles, business-appropriate gestures
  * Clothing: Slight fabric movement, professional posture adjustments
- **Cartoon Mascots**:
  * Exaggerated expressions, bouncy movements, character-specific quirks
  * Props: Logo juggling, magic appearance effects, playful interactions
- **Animal Characters**:
  * Natural species movements enhanced for personality
  * Accessories: Company-branded items (collars, hats, scarfs) with subtle animation

**TECHNICAL SPECIFICATIONS FOR IMAGE-TO-VIDEO:**
- Lens: 50mm for natural perspective maintaining image composition integrity
- Motion: Subtle but noticeable - avoid overwhelming the original image aesthetics
- Character Isolation: Focus animation on main character while preserving background
- Seamless Integration: Ensure animated elements feel natural within original image context
- Resolution: Maintain crisp image quality throughout animation process

**CORPORATE MESSAGE DELIVERY METHODS:**
- **Text Overlay**: Company name and tagline with professional typography animation
- **Character Speech**: If applicable, mouth movements synced with welcome message
- **Logo Interaction**: Character holding, pointing to, or magically revealing company logo
- **Service Highlight**: Character demonstrating or presenting key company offerings
- **Contact Integration**: Phone numbers, websites, or social media handles elegantly displayed

**AUDIO INTEGRATION (8-Second Optimization):**
- Background: Corporate-appropriate music (upbeat but professional)
- Character Sounds: Appropriate to character type (human voice, mascot sounds, animal noises)
- Brand Audio: Logo sound effects, chimes, or signature company audio elements
- Welcome Message Examples (15-20 words max):
  * "Welcome to TechCorp - where innovation meets reliability. Let's build the future together!"
  * "Hi! I'm Buddy from StartupPlus. We're here to make your business dreams come true!"
  * "Discover excellence with ProServices - your success is our mission. Welcome aboard!"

**COMPANY TYPE ADAPTATIONS:**
- **Tech Companies**: Modern, clean aesthetics with digital elements and futuristic touches
- **Creative Agencies**: Vibrant colors, artistic movements, creative flair in animations  
- **Professional Services**: Conservative, trustworthy presentation with confident character actions
- **Retail/Consumer**: Friendly, approachable characters with product-focused interactions
- **Healthcare**: Caring, professional demeanor with health-focused visual elements
- **Education**: Encouraging, knowledgeable character presentation with learning themes

**IMAGE-TO-VIDEO OPTIMIZATION GUIDELINES:**
- **Respect Original Composition**: Maintain the visual balance and framing of input image
- **Selective Animation**: Focus on bringing the main character to life while preserving image integrity
- **Brand Consistency**: Ensure animated elements align with existing brand elements in image
- **Natural Integration**: Make character movements feel organic within the original scene context
- **Quality Preservation**: Maintain or enhance the visual quality of the original image

**ENGAGEMENT & CONVERSION FOCUS:**
- **Immediate Impact**: Character animation captures attention within first 2 seconds  
- **Trust Building**: Professional character presentation establishes credibility
- **Memorable Branding**: Company logo and name prominently featured and animated
- **Clear Value Proposition**: Brief but compelling company benefit communication
- **Action Invitation**: Character gesture toward next steps (website visit, contact, etc.)

Remember: The goal is to transform a static company image into a dynamic, engaging 8-second introduction that brings characters to life while maintaining professional corporate standards and clear brand messaging. Every animation should serve the purpose of making the company more approachable and memorable while preserving the essence of the original image.
"""


GENERAL_VIDEO_CONTEXT = """
You are creating a general purpose video optimized for VEO3 generation with maximum fidelity to user input. Your primary objective is to faithfully translate the user's description into a technically optimized VEO3 prompt without adding creative elements not specified by the user. Follow these VEO3-optimized specifications:

**CORE PRINCIPLE - USER FIDELITY:**
- **Preserve User Intent**: Maintain exactly what the user describes without creative embellishment
- **No Unauthorized Additions**: Do not add characters, objects, or scenes not mentioned by the user
- **Respect User Vision**: Stay true to the user's creative direction and description
- **Technical Enhancement Only**: Add only VEO3 technical specifications to improve execution quality

**VEO3 STRUCTURAL OPTIMIZATION (Applied to User Content):**

**SUBJECT ANALYSIS & PRESERVATION:**
- **Extract Main Subject**: Identify the primary focus from user description (person, object, landscape, concept)
- **Maintain Character Integrity**: If user mentions specific people, preserve their described characteristics exactly
- **Object Accuracy**: Keep all mentioned objects, props, or elements as described
- **Scene Fidelity**: Use only the locations and environments specified by the user

**SHOT COMPOSITION ENHANCEMENT (Based on User Content):**
- **Wide Shot**: When user describes expansive scenes, environments, or multiple elements
- **Medium Shot**: For balanced subject-environment focus as described by user
- **Close-up**: When user emphasizes details, emotions, or specific object focus
- **Tracking Shot**: If user describes movement or following action
- **Static Shot**: For contemplative or focused scenes as indicated by user

**CAMERA MOVEMENT OPTIMIZATION (Guided by User Intent):**
- **Dolly Movement**: Smooth forward/backward movement for emphasis user describes
- **Pan Movement**: Horizontal rotation to reveal elements user mentions
- **Tilt Movement**: Vertical camera adjustment for user-specified perspectives
- **Handheld**: For dynamic, energetic scenes if user suggests movement
- **Steady/Static**: For calm, focused content as user indicates

**LIGHTING ADAPTATION (Matching User's Mood):**
- **Golden Hour**: Warm, cinematic lighting for positive/romantic user descriptions
- **Blue Hour**: Cool, dramatic lighting for evening/mysterious user content
- **Natural Daylight**: Clear, bright illumination for straightforward user scenes
- **Soft Studio**: Professional, even lighting for clean user presentations
- **Dramatic/High Contrast**: Strong shadows and highlights for intense user content
- **Ambient/Mood**: Atmospheric lighting matching user's described tone

**STYLE PRESERVATION & TECHNICAL ENHANCEMENT:**
- **Cinematic Realism**: Default professional style unless user specifies otherwise
- **User-Specified Styles**: Honor any style requests (animation, vintage, artistic, etc.)
- **Lens Selection**: 50mm for natural perspective, wide-angle for expansive scenes, macro for details
- **Depth of Field**: Shallow focus for subject isolation, deep focus for environmental scenes
- **Color Grading**: Adjust saturation and tone to match user's described mood

**AUDIO INTEGRATION (Supporting User Vision):**
- **Ambient Sounds**: Match the environment user describes (city sounds, nature, interior)
- **Action Audio**: Sound effects that naturally accompany user-described actions
- **Dialogue Preservation**: If user mentions speech, maintain exact wording
- **Music Atmosphere**: Background audio that supports but doesn't override user's vision
- **Audio Controls**: "(no subtitles)" or other technical specifications as needed

**USER DESCRIPTION ANALYSIS FRAMEWORK:**

**Content Type Recognition:**
- **Narrative Scenes**: Story-driven content with characters and plot
- **Documentary Style**: Informational or educational content
- **Abstract/Artistic**: Creative or conceptual visual content
- **Product/Object Focus**: Commercial or demonstration content
- **Nature/Landscape**: Environmental or scenic content
- **Portrait/Character**: People-focused content

**Mood & Atmosphere Matching:**
- **Energetic**: Fast-paced camera work, bright lighting, dynamic movement
- **Calm/Peaceful**: Smooth, gentle movements, soft lighting, steady shots
- **Dramatic**: High contrast lighting, purposeful camera movement, tension-building composition
- **Professional**: Clean, well-lit, stable shots with clear subject focus
- **Artistic/Creative**: Flexible composition allowing for creative expression within user's vision
- **Intimate/Personal**: Close shots, warm lighting, natural feel

**TECHNICAL SPECIFICATIONS (Applied Transparently):**
- **Resolution Optimization**: Ensure crisp, high-quality output
- **Motion Smoothness**: Eliminate jerky movements with proper easing
- **Focus Accuracy**: Sharp focus on user-specified subjects
- **Color Accuracy**: Maintain natural or user-preferred color representation
- **Audio Clarity**: Clean sound that supports the visual content

**STYLE ADAPTATION PRESETS (When User Specifies):**
- **Documentary**: "In documentary style: [user content]" - handheld feel, natural lighting
- **Cinematic**: "In cinematic style: [user content]" - dramatic lighting, composed shots
- **Vintage/Retro**: "In vintage style: [user content]" - period-appropriate visual treatment
- **Minimalist**: "In minimalist style: [user content]" - clean, simple composition
- **Artistic**: "In artistic style: [user content]" - creative visual interpretation
- **Commercial**: "In commercial style: [user content]" - polished, professional presentation

**USER INPUT PROCESSING METHODOLOGY:**

**Step 1: Content Extraction**
- Identify all subjects, objects, locations mentioned by user
- Note any specific actions or movements described
- Recognize user's intended mood or atmosphere

**Step 2: Technical Translation**
- Convert user's scene description into VEO3-compatible shot composition
- Determine appropriate camera movement based on user's described action
- Select lighting that matches user's indicated mood or setting

**Step 3: Quality Enhancement**
- Add technical specifications (lens, focus, color) that improve execution
- Include audio elements that naturally support user's scene
- Ensure smooth motion and professional polish without changing content

**Step 4: Prompt Assembly**
- Structure as single, detailed paragraph
- Lead with shot composition and camera angle
- Include user's subjects and actions exactly as described
- Add setting and lighting that matches user's vision
- Conclude with technical specs for optimal VEO3 execution

**EXAMPLE USER CONTENT TRANSFORMATIONS:**

**User Input**: "A person reading a book in a coffee shop"
**VEO3 Optimized**: "Medium shot, eye-level. A person sits comfortably at a wooden table reading an open book in a cozy coffee shop. Soft natural light streams through large windows, creating warm highlights on the pages. Gentle camera tilt toward the book, shallow depth of field with café atmosphere blurred in background. Audio: quiet café ambiance, soft page turning, distant coffee machine hum. Shot on 50mm lens, warm color palette."

**User Input**: "Waves crashing on rocks during sunset"
**VEO3 Optimized**: "Wide establishing shot transitioning to medium shot. Ocean waves crash dramatically against dark rocky coastline during golden hour sunset. Camera pans slowly left to right following wave action, then gentle tilt up to capture orange-pink sky. Golden hour lighting with high contrast between warm sky and dark rocks. Audio: powerful wave crashes, wind over rocks, distant seabird calls. Shot on wide-angle lens, enhanced warm color grading."

Remember: Your role is to be a faithful technical translator, converting user descriptions into VEO3-optimized prompts while preserving every aspect of their creative vision. Add technical excellence, never creative content.
"""
