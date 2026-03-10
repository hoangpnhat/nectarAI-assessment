from typing import Dict, Any
from openai import OpenAI
from app.core.config import settings


class PromptEngineer:
    """
    Converts LLM chat context into high-quality natural language prompts

    For Z-Turbo workflow: Uses LLM to generate detailed, descriptive 100-300 word prompts
    """

    def __init__(self):
        """Initialize OpenAI client for prompt generation"""
        self.client = OpenAI(api_key=settings.openai_api_key)

    # Base negative prompt for Z-Turbo workflow
    BASE_NEGATIVE = """Shiny skin, bad tone, overexposed, static, blurry details, bad style, bad composition, grayish overall look, worst quality, low quality, jpeg artifacts, unfinished, extra fingers, poorly drawn hands, poorly drawn face, deformed, ugly, distorted limbs, fused fingers, messy background, three legs, three arms, plastic skin, flat, low detail, low resolution, overweight, old, chubby, bad anatomy, unnatural lighting, washed out image, pixelation, oversaturation, inconsistent shadows, asymmetrical face, unrealistic proportions, disfigured, grainy texture, oversharpened, color banding, distorted perspective, poor depth, unbalanced cropping"""

    @staticmethod
    def extract_scene_context(chat_history: list) -> Dict[str, Any]:
        """
        Extract scene information from chat history

        Returns:
            Dict with: location, activity, clothing, mood, nsfw_level
        """
        context = {
            "location": None,
            "activity": None,
            "clothing": None,
            "mood": "neutral",
            "nsfw_level": 0  # 0=SFW, 1=suggestive, 2=NSFW
        }

        # Simple keyword extraction (can be enhanced with LLM)
        recent_messages = " ".join([msg.get("content", "") for msg in chat_history[-5:]])
        recent_lower = recent_messages.lower()

        # Location detection
        locations = {
            "coffee shop": "in a cozy coffee shop, sitting at a wooden table",
            "cafe": "in a modern cafe, soft ambient lighting",
            "bedroom": "in a bedroom, soft window lighting",
            "gym": "at the gym, athletic environment",
            "beach": "at the beach, natural outdoor lighting",
            "park": "in a park, outdoor natural setting",
            "office": "in an office, professional setting",
            "restaurant": "in an elegant restaurant",
            "home": "at home, comfortable indoor setting",
            "outdoors": "outdoors, natural lighting",
            "studio": "in a photo studio, professional lighting"
        }

        for loc_key, loc_desc in locations.items():
            if loc_key in recent_lower:
                context["location"] = loc_desc
                break

        # Default location if none found
        if not context["location"]:
            context["location"] = "in a well-lit room, natural lighting"

        # Clothing/appearance detection
        clothing_keywords = {
            "dress": "wearing an elegant dress",
            "lingerie": "wearing lingerie",
            "bikini": "wearing a bikini",
            "swimsuit": "wearing a swimsuit",
            "workout": "wearing workout clothes",
            "casual": "wearing casual clothes",
            "formal": "wearing formal attire",
            "nude": "nude",
            "naked": "nude"
        }

        for cloth_key, cloth_desc in clothing_keywords.items():
            if cloth_key in recent_lower:
                context["clothing"] = cloth_desc
                if cloth_key in ["nude", "naked", "lingerie"]:
                    context["nsfw_level"] = 2
                elif cloth_key in ["bikini", "swimsuit"]:
                    context["nsfw_level"] = 1
                break

        # Activity detection
        activities = {
            "sitting": "sitting naturally",
            "standing": "standing confidently",
            "lying": "lying down comfortably",
            "exercising": "exercising, in motion",
            "reading": "reading a book",
            "drinking": "holding a drink",
            "looking at camera": "looking directly at camera",
            "mirror": "in front of a mirror"
        }

        for act_key, act_desc in activities.items():
            if act_key in recent_lower:
                context["activity"] = act_desc
                break

        return context

    def build_prompt(
        self,
        scene_context: Dict[str, Any],
        character_gender: str = "woman",
        style: str = "natural_photo",
        reference_features: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Build detailed natural language prompt using LLM (100-300 words for Z-Turbo)

        Args:
            scene_context: Context from extract_scene_context
            character_gender: "man" or "woman"
            style: "natural_photo", "portrait", "full_body"
            reference_features: Extracted features from reference image (optional)

        Returns:
            Dict with "positive" and "negative" keys
        """
        # Use LLM to generate detailed, descriptive prompt
        location = scene_context.get("location", "in a well-lit room")
        activity = scene_context.get("activity", "standing naturally")
        clothing = scene_context.get("clothing", "casual attire")
        mood = scene_context.get("mood", "relaxed")
        nsfw_level = scene_context.get("nsfw_level", 0)

        # Get NSFW-enhanced details if present
        nsfw_details = scene_context.get("nsfw_details", "")
        nsfw_focus = scene_context.get("nsfw_focus", "")

        # Build context description
        nsfw_guidance = ""
        if nsfw_level >= 1:
            nsfw_guidance = f"\n- NSFW Details: {nsfw_details}\n- Focus: {nsfw_focus}"

        # Build character features description if available
        character_features = ""
        if reference_features:
            features = []

            # Physical features
            if reference_features.get('ethnicity'):
                features.append(f"Ethnicity: {reference_features['ethnicity']}")
            if reference_features.get('skin_tone'):
                features.append(f"Skin: {reference_features['skin_tone']}")
            if reference_features.get('age_range'):
                features.append(f"Age: {reference_features['age_range']}")

            # Hair
            hair_parts = []
            if reference_features.get('hair_length'):
                hair_parts.append(reference_features['hair_length'])
            if reference_features.get('hair_style'):
                hair_parts.append(reference_features['hair_style'])
            if reference_features.get('hair_color'):
                hair_parts.append(reference_features['hair_color'])
            if hair_parts:
                features.append(f"Hair: {' '.join(hair_parts)}")

            # Face
            if reference_features.get('eye_color'):
                features.append(f"Eyes: {reference_features['eye_color']}")
            if reference_features.get('face_shape'):
                features.append(f"Face shape: {reference_features['face_shape']}")

            # Body
            if reference_features.get('body_type'):
                features.append(f"Build: {reference_features['body_type']}")

            # Facial hair (for men)
            if reference_features.get('facial_hair') and reference_features['facial_hair'] != 'none':
                features.append(f"Facial hair: {reference_features['facial_hair']}")

            # Distinctive features
            distinctive = reference_features.get('distinctive_features', [])
            if distinctive:
                features.append(f"Distinctive: {', '.join(distinctive[:3])}")

            if features:
                character_features = "\n\nCHARACTER FEATURES (MUST INCLUDE IN DESCRIPTION):\n" + "\n".join([f"- {f}" for f in features])

        # Create detailed prompt generation request
        prompt_instruction = f"""Generate a detailed, natural language image prompt (100-300 words) for a photorealistic portrait.

Context:
- Subject: A young {character_gender}
- Location: {location}
- Activity/Pose: {activity}
- Clothing: {clothing}
- Mood: {mood}
- Style: {style}
- NSFW Level: {nsfw_level} (0=SFW, 1=suggestive, 2=explicit){nsfw_guidance}{character_features}

Requirements:
1. Write in natural, flowing paragraphs (NOT comma-separated keywords)
2. **CRITICAL**: If CHARACTER FEATURES are provided above, you MUST incorporate ALL of them naturally into the description:
   - Mention ethnicity/race naturally (e.g., "a young Asian woman", "a Caucasian man")
   - Describe skin tone accurately (e.g., "fair complexion", "tan skin")
   - Specify hair details exactly (e.g., "long straight black hair", "short curly brown hair")
   - Include eye color (e.g., "brown eyes", "piercing blue eyes")
   - Mention body type (e.g., "athletic build", "slim figure")
   - Incorporate facial hair if mentioned (e.g., "with short stubble", "clean-shaven")
   - Include distinctive features naturally (e.g., "with high cheekbones and delicate features")
3. Include specific details about:
   - Physical appearance matching CHARACTER FEATURES
   - Clothing and accessories (or lack thereof for nude scenes)
   - Pose, body language, and positioning
   - Lighting (direction, quality, atmosphere, how it plays on skin/surfaces)
   - Environment and background elements with depth
   - Camera angle, perspective, and framing
   - Mood and emotional atmosphere
4. Use descriptive, cinematic language: "soft afternoon sunlight filters through the window, creating delicate highlights along her shoulder..."
5. For NSFW content (level 1-2):
   - Level 1: Describe sensual elements tastefully - body curves, intimate clothing, suggestive poses
   - Level 2: Be explicit and detailed - mention breasts, nipples, intimate body parts naturally visible, nude anatomy, sensual details
6. Include technical photography terms naturally woven into description
7. Aim for 150-250 words total
8. End with: "High resolution, hyperrealistic detailing, photorealistic skin texture, natural color palette with [warm/cool] tones."

Generate ONLY the prompt text as one continuous description, no section labels or explanations."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at writing detailed image generation prompts for professional photography."},
                    {"role": "user", "content": prompt_instruction}
                ],
                temperature=0.8,
                max_tokens=500
            )

            positive_prompt = response.choices[0].message.content.strip()
            print(f"[PromptEngineer] Generated {len(positive_prompt.split())} word prompt")

        except Exception as e:
            print(f"[PromptEngineer] Error generating prompt with LLM: {e}, using fallback")
            # Fallback to simple template
            positive_prompt = self._generate_fallback_prompt(scene_context, character_gender, style, reference_features)

        # Negative prompt
        negative_prompt = self.BASE_NEGATIVE

        return {
            "positive": positive_prompt,
            "negative": negative_prompt
        }

    def _generate_fallback_prompt(
        self,
        scene_context: Dict[str, Any],
        character_gender: str,
        style: str,
        reference_features: Dict[str, Any] = None
    ) -> str:
        """Fallback prompt generator if LLM fails"""
        location = scene_context.get("location", "in a well-lit room")
        activity = scene_context.get("activity", "standing naturally")
        clothing = scene_context.get("clothing", "casual attire")
        mood = scene_context.get("mood", "relaxed")
        nsfw_level = scene_context.get("nsfw_level", 0)
        nsfw_details = scene_context.get("nsfw_details", "")
        nsfw_focus = scene_context.get("nsfw_focus", "")

        # Build character description from reference features
        character_desc = f"young {character_gender}"
        physical_features = []

        if reference_features:
            # Add ethnicity
            if reference_features.get('ethnicity') and reference_features['ethnicity'] != 'unknown':
                character_desc = f"young {reference_features['ethnicity']} {character_gender}"

            # Add skin tone
            if reference_features.get('skin_tone'):
                physical_features.append(f"{reference_features['skin_tone']} complexion")

            # Add hair description
            hair_parts = []
            if reference_features.get('hair_length'):
                hair_parts.append(reference_features['hair_length'])
            if reference_features.get('hair_style'):
                hair_parts.append(reference_features['hair_style'])
            if reference_features.get('hair_color'):
                hair_parts.append(reference_features['hair_color'])
            if hair_parts:
                physical_features.append(f"{' '.join(hair_parts)} hair")

            # Add eye color
            if reference_features.get('eye_color'):
                physical_features.append(f"{reference_features['eye_color']} eyes")

            # Add body type
            if reference_features.get('body_type') and reference_features['body_type'] != 'average':
                physical_features.append(f"{reference_features['body_type']} build")

            # Add distinctive features
            distinctive = reference_features.get('distinctive_features', [])
            if distinctive:
                physical_features.extend(distinctive[:2])

        physical_desc = ", ".join(physical_features) if physical_features else "warm, natural complexion with soft features"

        # Base description
        base = f"""A natural portrait photograph of a {character_desc} {activity}. {location.capitalize()}. They are {clothing}, with a {mood} expression. The subject has {physical_desc}."""

        # Add NSFW details if present
        if nsfw_level >= 1 and nsfw_details:
            base += f" {nsfw_details}."

        # Add lighting and technical details
        technical = f""" Soft lighting creates gentle highlights and shadows, emphasizing natural skin texture and body definition. The background is softly blurred with shallow depth of field, maintaining focus on the subject."""

        # Add NSFW focus if present
        if nsfw_level >= 1 and nsfw_focus:
            technical += f" {nsfw_focus}."

        # Quality tags
        quality = """ Shot with professional camera equipment, natural color grading, high resolution, hyperrealistic detailing, photorealistic skin texture, film grain aesthetic."""

        return base + technical + quality

    @staticmethod
    def enhance_prompt_with_details(base_prompt: str, details: Dict[str, Any]) -> str:
        """
        Add extra details to prompt

        Args:
            base_prompt: Base positive prompt
            details: Dict with optional keys: pose, expression, hair, etc.
        """
        enhancements = []

        if details.get("pose"):
            enhancements.append(f"pose: {details['pose']}")

        if details.get("expression"):
            enhancements.append(f"{details['expression']} expression")

        if details.get("hair"):
            enhancements.append(f"{details['hair']} hair")

        if details.get("lighting"):
            enhancements.append(f"{details['lighting']} lighting")

        if enhancements:
            return base_prompt + ",\n" + ", ".join(enhancements)

        return base_prompt


# Example usage
if __name__ == "__main__":
    engineer = PromptEngineer()

    # Simulate chat history
    chat_history = [
        {"role": "user", "content": "What are you wearing right now?"},
        {"role": "assistant", "content": "I'm wearing a comfortable dress, sitting in a coffee shop"}
    ]

    # Extract context
    context = engineer.extract_scene_context(chat_history)
    print("Context:", context)

    # Build prompt
    prompts = engineer.build_prompt(context, character_gender="woman")
    print("\nPositive:", prompts["positive"])
    print("\nNegative:", prompts["negative"])
