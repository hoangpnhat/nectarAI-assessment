"""
Prompt Engineering Service
Converts LLM intent context into high-quality Stable Diffusion prompts
"""
from typing import Dict, Any

class PromptEngineeringService:
    def __init__(self):
        self.quality_tags = "highly detailed, 8k uhd, high quality, professional photography, sharp focus"
        self.style_tags = "photorealistic, cinematic lighting, dslr, detailed skin texture"

        # Base negative prompts
        self.base_negative = """
ugly, deformed, noisy, blurry, distorted, grainy, low quality, bad anatomy,
bad proportions, extra limbs, extra fingers, mutated hands, fused fingers,
long neck, cross-eyed, cartoon, anime, drawing, painting, sketch,
text, watermark, signature, username, logo
""".strip()

        self.nsfw_negative_additional = """
bad anatomy, bad hands, missing fingers, extra fingers, three hands, three legs,
bad arms, missing legs, missing arms, poorly drawn face, poorly drawn hands,
poorly drawn feet, fat, disfigured, out of frame, long neck, poor art,
tiling, watermark, grainy, blurry, mutation, mutated, ugly
""".strip()

    def create_prompt(
        self,
        character_description: str,
        context: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Engineer high-quality prompts from context

        Formula: Subject + Action/Pose + Setting + Outfit + Lighting + Style + Quality
        """
        scene = context.get("scene", "portrait")
        pose = context.get("pose", "natural pose")
        outfit = context.get("outfit", "casual clothes")
        lighting = context.get("lighting", "natural lighting")
        mood = context.get("mood", "confident")
        is_nsfw = context.get("is_nsfw", False)
        additional = context.get("additional_details", "")

        # Build subject description
        subject = f"photograph of {character_description}"

        # Build scene/action
        action_scene = f"{pose}, {scene}"

        # Build outfit description
        outfit_desc = f"wearing {outfit}"

        # Build lighting and mood
        lighting_mood = f"{lighting}, {mood} expression"

        # Compose final prompt
        prompt_parts = [
            subject,
            action_scene,
            outfit_desc,
            lighting_mood,
            self.style_tags,
            self.quality_tags
        ]

        if additional:
            prompt_parts.insert(-2, additional)

        # Add NSFW specific tags if needed
        if is_nsfw:
            nsfw_tags = "realistic skin texture, detailed body, natural proportions, anatomically correct"
            prompt_parts.insert(-2, nsfw_tags)

        final_prompt = ", ".join(prompt_parts)

        # Build negative prompt
        negative_prompt = self.base_negative
        if is_nsfw:
            negative_prompt = f"{self.base_negative}, {self.nsfw_negative_additional}"

        # Generation settings
        settings = {
            "steps": 35 if is_nsfw else 30,
            "cfg_scale": 7.5,
            "instantid_strength": 0.85,
            "width": 1024,
            "height": 1024,
            "is_nsfw": is_nsfw
        }

        return {
            "prompt": final_prompt,
            "negative_prompt": negative_prompt,
            "settings": settings
        }

    def enhance_prompt_for_scene(self, prompt: str, scene_type: str) -> str:
        """
        Add scene-specific enhancements
        """
        scene_enhancements = {
            "coffee shop": "indoor cafe setting, wooden tables, ambient lighting, coffee cups, cozy atmosphere",
            "bedroom": "bedroom interior, bed with pillows, soft bedding, intimate setting, warm lighting",
            "beach": "beach background, sand, ocean waves, blue sky, sunset or sunrise, outdoor",
            "gym": "gym equipment, weights, exercise machines, athletic setting, dramatic lighting",
            "outdoor": "natural outdoor environment, trees, sky, natural daylight",
            "studio": "studio background, seamless backdrop, professional lighting setup",
        }

        enhancement = scene_enhancements.get(scene_type.lower(), "")
        if enhancement:
            return f"{prompt}, {enhancement}"
        return prompt

    def create_character_specific_prompt(
        self,
        gender: str,
        features: Dict[str, str],
        context: Dict[str, str]
    ) -> str:
        """
        Create prompts with specific character features
        """
        # Build detailed character description
        char_parts = []

        if gender:
            char_parts.append(gender)

        if features.get("age"):
            char_parts.append(f"{features['age']} years old")

        if features.get("ethnicity"):
            char_parts.append(features["ethnicity"])

        if features.get("hair"):
            char_parts.append(f"{features['hair']} hair")

        if features.get("eyes"):
            char_parts.append(f"{features['eyes']} eyes")

        if features.get("build"):
            char_parts.append(f"{features['build']} build")

        character_description = " ".join(char_parts) if char_parts else "person"

        return self.create_prompt(character_description, context)
