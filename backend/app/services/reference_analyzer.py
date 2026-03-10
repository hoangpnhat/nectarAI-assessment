"""
Reference Image Analyzer
Uses GPT-4 Vision to extract detailed character features from reference images
"""
from openai import OpenAI
from pathlib import Path
from typing import Dict, Optional
import base64
import json
from app.core.config import settings


class ReferenceAnalyzer:
    """
    Analyzes reference images to extract character features
    Features are used to enhance prompt generation for better consistency
    """

    def __init__(self):
        """Initialize OpenAI client with Vision support"""
        self.client = OpenAI(api_key=settings.openai_api_key)

    def analyze_reference_image(self, image_path: str) -> Dict[str, any]:
        """
        Analyze reference image using GPT-4 Vision

        Args:
            image_path: Path to reference image (in ComfyUI/input/)

        Returns:
            Dict with extracted features:
            {
                "gender": "woman/man",
                "age_range": "20-25",
                "ethnicity": "Asian/Caucasian/African/Hispanic/Middle Eastern/Mixed",
                "skin_tone": "fair/light/medium/olive/tan/brown/dark",
                "body_type": "slim/athletic/average/curvy/plus-size",
                "hair_color": "black/brown/blonde/red/gray/white",
                "hair_style": "short/medium/long/curly/straight/wavy",
                "hair_length": "short/shoulder-length/long",
                "facial_hair": "none/stubble/beard/mustache/goatee" (for men),
                "eye_color": "brown/blue/green/hazel/gray",
                "distinctive_features": ["high cheekbones", "freckles", etc.],
                "face_shape": "oval/round/square/heart/diamond",
                "overall_description": "Natural language summary"
            }
        """
        try:
            # Read and encode image
            full_path = Path("../ComfyUI/input") / image_path
            if not full_path.exists():
                raise FileNotFoundError(f"Reference image not found: {full_path}")

            with open(full_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            # Analyze with GPT-4o (has vision capabilities)
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at analyzing human faces and physical features for character description.
Provide detailed, objective analysis of physical characteristics.
Be specific and accurate - these details will be used for AI image generation."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this reference image and extract the following features in JSON format:

{
  "gender": "woman or man",
  "age_range": "estimated age range (e.g., 20-25, 30-35)",
  "ethnicity": "Asian/Caucasian/African/Hispanic/Middle Eastern/Mixed (be specific)",
  "skin_tone": "fair/light/medium/olive/tan/brown/dark",
  "body_type": "slim/athletic/average/curvy/muscular/plus-size",
  "hair_color": "specific color (black/brown/blonde/red/auburn/gray/white/dyed)",
  "hair_style": "straight/wavy/curly/coily",
  "hair_length": "very short/short/medium/shoulder-length/long/very long",
  "facial_hair": "none/stubble/short beard/full beard/mustache/goatee (for men only)",
  "eye_color": "brown/blue/green/hazel/gray/amber",
  "face_shape": "oval/round/square/heart/diamond/oblong",
  "distinctive_features": ["list notable features like: high cheekbones, freckles, dimples, strong jawline, full lips, etc."],
  "overall_description": "A concise 2-3 sentence natural language description focusing on their appearance"
}

Important:
- Be specific and accurate
- Use descriptive terms that work well for AI image generation
- Include any unique or distinctive features
- Focus on permanent features, not clothing or accessories
- For ethnicity, consider facial structure, features, skin tone
- Describe exactly what you see

Return ONLY valid JSON, no other text."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for more consistent analysis
            )

            # Parse JSON response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            features = json.loads(content)

            print(f"[ReferenceAnalyzer] Successfully analyzed reference image")
            print(f"   Gender: {features.get('gender', 'N/A')}")
            print(f"   Ethnicity: {features.get('ethnicity', 'N/A')}")
            print(f"   Skin Tone: {features.get('skin_tone', 'N/A')}")
            print(f"   Hair: {features.get('hair_color', 'N/A')} {features.get('hair_style', 'N/A')}")
            print(f"   Distinctive: {', '.join(features.get('distinctive_features', [])[:3])}")

            return features

        except FileNotFoundError as e:
            print(f"[ReferenceAnalyzer] Error: {e}")
            raise

        except json.JSONDecodeError as e:
            print(f"[ReferenceAnalyzer] Failed to parse JSON response: {e}")
            print(f"   Raw response: {content[:200]}...")
            # Return minimal features as fallback
            return self._get_fallback_features()

        except Exception as e:
            print(f"[ReferenceAnalyzer] Error analyzing reference: {e}")
            return self._get_fallback_features()

    def _get_fallback_features(self) -> Dict[str, any]:
        """Fallback features if analysis fails"""
        return {
            "gender": "unknown",
            "age_range": "20-30",
            "ethnicity": "unknown",
            "skin_tone": "medium",
            "body_type": "average",
            "hair_color": "brown",
            "hair_style": "straight",
            "hair_length": "medium",
            "facial_hair": "none",
            "eye_color": "brown",
            "face_shape": "oval",
            "distinctive_features": [],
            "overall_description": "A person with natural features."
        }

    def format_features_for_prompt(self, features: Dict[str, any]) -> str:
        """
        Format extracted features into a natural language description for prompts

        Args:
            features: Features dict from analyze_reference_image()

        Returns:
            Natural language description suitable for image generation prompts
        """
        parts = []

        # Gender and age
        gender = features.get('gender', 'person')
        age_range = features.get('age_range', '')
        if age_range:
            parts.append(f"a young {gender} in their {age_range}")
        else:
            parts.append(f"a young {gender}")

        # Ethnicity and skin tone
        ethnicity = features.get('ethnicity', '')
        skin_tone = features.get('skin_tone', '')
        if ethnicity and ethnicity != "unknown":
            parts.append(f"of {ethnicity} descent")
        if skin_tone:
            parts.append(f"with {skin_tone} skin")

        # Body type
        body_type = features.get('body_type', '')
        if body_type and body_type != "average":
            parts.append(f"{body_type} build")

        # Hair
        hair_color = features.get('hair_color', '')
        hair_style = features.get('hair_style', '')
        hair_length = features.get('hair_length', '')

        hair_desc = []
        if hair_length:
            hair_desc.append(hair_length)
        if hair_style:
            hair_desc.append(hair_style)
        if hair_color:
            hair_desc.append(hair_color)
        if hair_desc:
            parts.append(f"{' '.join(hair_desc)} hair")

        # Facial hair (for men)
        facial_hair = features.get('facial_hair', '')
        if facial_hair and facial_hair != "none":
            parts.append(f"with {facial_hair}")

        # Eye color
        eye_color = features.get('eye_color', '')
        if eye_color:
            parts.append(f"{eye_color} eyes")

        # Face shape
        face_shape = features.get('face_shape', '')
        if face_shape:
            parts.append(f"{face_shape} face shape")

        # Distinctive features
        distinctive = features.get('distinctive_features', [])
        if distinctive:
            # Add top 3 most distinctive features
            parts.extend(distinctive[:3])

        # Join with natural connectors
        description = parts[0] if parts else "a person"

        # Add remaining parts with commas
        if len(parts) > 1:
            description += ", " + ", ".join(parts[1:])

        return description

    def get_compact_features(self, features: Dict[str, any]) -> Dict[str, str]:
        """
        Get compact feature summary for prompt injection

        Returns dict optimized for adding to prompts:
        {
            "subject": "young Asian woman",
            "appearance": "fair skin, long straight black hair, brown eyes",
            "distinctive": "high cheekbones, delicate features"
        }
        """
        # Subject
        gender = features.get('gender', 'person')
        ethnicity = features.get('ethnicity', '')
        age = features.get('age_range', '').split('-')[0] if features.get('age_range') else ''

        subject_parts = []
        if age:
            subject_parts.append("young")
        if ethnicity and ethnicity != "unknown":
            subject_parts.append(ethnicity)
        subject_parts.append(gender)
        subject = " ".join(subject_parts)

        # Appearance
        appearance_parts = []

        skin = features.get('skin_tone', '')
        if skin:
            appearance_parts.append(f"{skin} skin")

        hair_len = features.get('hair_length', '')
        hair_style = features.get('hair_style', '')
        hair_color = features.get('hair_color', '')
        if hair_len or hair_style or hair_color:
            hair = " ".join(filter(None, [hair_len, hair_style, hair_color]))
            appearance_parts.append(f"{hair} hair")

        eyes = features.get('eye_color', '')
        if eyes:
            appearance_parts.append(f"{eyes} eyes")

        appearance = ", ".join(appearance_parts)

        # Distinctive features
        distinctive_list = features.get('distinctive_features', [])
        distinctive = ", ".join(distinctive_list[:3]) if distinctive_list else ""

        return {
            "subject": subject,
            "appearance": appearance,
            "distinctive": distinctive
        }
