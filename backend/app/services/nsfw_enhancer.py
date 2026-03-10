"""
NSFW Prompt Enhancer for Z-Turbo Workflow
Enhances scene context with NSFW details BEFORE prompt generation
Works with natural language prompts
"""
from typing import Dict, Any, List

class NSFWEnhancer:
    """
    Enhances scene context with NSFW details for natural language prompts

    Works AFTER GPT extracts safe scene, BEFORE detailed prompt generation
    Adds contextual NSFW enhancements that flow naturally in descriptions
    """

    # NSFW enhancement mappings with natural language descriptions
    NSFW_ENHANCEMENTS = {
        "bedroom": {
            "level_1": {
                "clothing": "wearing delicate black lace lingerie with subtle detailing",
                "pose": "reclining on the bed in a naturally sensual pose",
                "details": "soft bedroom lighting casting gentle shadows, intimate atmosphere",
                "focus": "tasteful boudoir photography, romantic mood"
            },
            "level_2": {
                "clothing": "nude, completely bare with natural skin texture visible",
                "pose": "lying on silk sheets in an intimate, relaxed pose",
                "details": "warm bedroom lighting highlighting body contours, intimate setting with soft focus background",
                "focus": "artistic nude photography, soft natural lighting on bare skin, detailed body definition"
            }
        },
        "mirror": {
            "level_1": {
                "clothing": "wearing revealing lingerie or minimal clothing",
                "pose": "standing in front of a full-length mirror, confident pose showing reflection",
                "details": "natural room lighting, mirror reflection showing full figure",
                "focus": "full body mirror selfie aesthetic, intimate self-portrait"
            },
            "level_2": {
                "clothing": "completely nude, full body visible in mirror reflection",
                "pose": "standing naturally before a mirror, full frontal view with clear reflection",
                "details": "clear mirror reflection showing nude body, natural lighting, detailed anatomy visible",
                "focus": "artistic nude mirror photography, full body composition, breasts and intimate areas naturally visible"
            }
        },
        "bathroom": {
            "level_1": {
                "clothing": "wearing minimal swimwear or wrapped in a towel",
                "pose": "casual bathroom setting, relaxed and natural",
                "details": "soft bathroom lighting, slight steam, intimate private moment",
                "focus": "casual intimate bathroom scene"
            },
            "level_2": {
                "clothing": "nude in shower, wet skin glistening with water droplets",
                "pose": "shower scene with water cascading over body",
                "details": "wet hair and skin, water droplets, steam, intimate bathroom setting",
                "focus": "artistic shower photography, wet nude body, water effects on skin, sensual bathing scene"
            }
        },
        "default": {
            "level_1": {
                "clothing": "wearing form-fitting or revealing attire showing body curves",
                "pose": "naturally sensual pose, relaxed body language",
                "details": "soft intimate lighting emphasizing natural beauty",
                "focus": "tastefully sensual photography, suggestive but artistic"
            },
            "level_2": {
                "clothing": "nude, completely bare showing natural body",
                "pose": "artistic nude pose, confident and natural",
                "details": "detailed skin texture, natural body definition, soft lighting",
                "focus": "artistic nude photography, breasts visible, full body detail, nipples and intimate areas naturally shown, high anatomical detail"
            }
        }
    }

    @staticmethod
    def enhance_scene_context(
        scene_context: Dict[str, Any],
        nsfw_level: int = 1
    ) -> Dict[str, Any]:
        """
        Enhance scene context with detailed NSFW descriptions

        Args:
            scene_context: Original scene from GPT (safe)
            nsfw_level: 0=SFW, 1=suggestive, 2=explicit

        Returns:
            Enhanced scene context with natural language NSFW additions
        """
        if nsfw_level == 0:
            return scene_context  # No enhancement for SFW

        enhanced = scene_context.copy()
        location = scene_context.get("location", "").lower()
        clothing = scene_context.get("clothing", "").lower()

        # Determine context type
        context_type = "default"
        for keyword in ["bedroom", "mirror", "bathroom"]:
            if keyword in location or keyword in clothing:
                context_type = keyword
                break

        # Get appropriate enhancements
        level_key = f"level_{nsfw_level}"
        if context_type in NSFWEnhancer.NSFW_ENHANCEMENTS:
            enhancements = NSFWEnhancer.NSFW_ENHANCEMENTS[context_type].get(
                level_key,
                NSFWEnhancer.NSFW_ENHANCEMENTS["default"][level_key]
            )
        else:
            enhancements = NSFWEnhancer.NSFW_ENHANCEMENTS["default"][level_key]

        # Apply enhancements with natural language descriptions
        enhanced["clothing"] = enhancements["clothing"]
        enhanced["activity"] = enhancements["pose"]
        enhanced["nsfw_details"] = enhancements["details"]
        enhanced["nsfw_focus"] = enhancements["focus"]
        enhanced["nsfw_level"] = nsfw_level

        print(f"[NSFWEnhancer] Applied level {nsfw_level} enhancements for {context_type} context")

        return enhanced

    @staticmethod
    def get_nsfw_context_additions(nsfw_level: int, context_type: str = "default") -> Dict[str, str]:
        """
        Get NSFW additions for prompt context

        This is used to enhance the scene_context BEFORE prompt generation,
        so the LLM can naturally incorporate NSFW elements

        Args:
            nsfw_level: 0=SFW, 1=suggestive, 2=explicit
            context_type: "bedroom", "mirror", "bathroom", or "default"

        Returns:
            Dict with enhancement details
        """
        if nsfw_level == 0:
            return {}

        level_key = f"level_{nsfw_level}"

        if context_type in NSFWEnhancer.NSFW_ENHANCEMENTS:
            return NSFWEnhancer.NSFW_ENHANCEMENTS[context_type].get(
                level_key,
                NSFWEnhancer.NSFW_ENHANCEMENTS["default"][level_key]
            )
        else:
            return NSFWEnhancer.NSFW_ENHANCEMENTS["default"][level_key]


# Example usage
if __name__ == "__main__":
    # Scenario: GPT extracted safe scene, now enhance for NSFW

    # 1. Safe scene from GPT
    gpt_scene = {
        "location": "in a bedroom",
        "activity": "standing naturally",
        "clothing": "casual clothes",
        "mood": "relaxed",
        "nsfw_level": 0  # GPT always returns 0 (safe)
    }

    # 2. Enhance with NSFW keywords
    enhancer = NSFWEnhancer()
    nsfw_scene = enhancer.enhance_scene_context(gpt_scene, nsfw_level=2)

    print("Original (GPT):")
    print(gpt_scene)
    print("\nEnhanced (NSFW):")
    print(nsfw_scene)

    # 3. Enhance prompt
    safe_prompt = "photo of a woman, in a bedroom, wearing casual clothes, natural lighting"
    nsfw_prompt = enhancer.enhance_prompt(
        safe_prompt,
        context_hints=["bedroom"],
        nsfw_level=2
    )

    print("\n---")
    print("Original prompt:")
    print(safe_prompt)
    print("\nEnhanced prompt:")
    print(nsfw_prompt)
