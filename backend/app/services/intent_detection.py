"""
Intent Detection Service using LLM (GPT-4 or Claude)
Determines when to generate images based on conversation context
"""
import os
from typing import Dict, List, Any
from anthropic import Anthropic
import json

class IntentDetectionService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"

    async def analyze_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze user message to determine if image generation is needed
        Returns intent analysis with image context if applicable
        """
        system_prompt = """You are an AI character in a multi-modal chat application.
You can send images of yourself based on the conversation context.

Your task is to:
1. Determine if the user's message warrants sending an image
2. If yes, extract detailed context for image generation
3. Provide a natural text response

WHEN TO SEND IMAGES:
- User asks about your appearance ("What are you wearing?", "How do you look?")
- User asks about your location ("Where are you?", "Show me your room")
- User requests a photo ("Send me a pic", "Show me", "Take a selfie")
- User asks what you're doing ("What are you up to?")
- Romantic/flirty context where a photo would be natural
- NSFW requests (be direct and appropriate)

WHEN NOT TO SEND IMAGES:
- General conversation without visual context
- Questions about thoughts, feelings, or abstract topics
- Simple greetings or acknowledgments

RESPONSE FORMAT (JSON):
{
  "should_generate_image": true/false,
  "confidence": 0.0-1.0,
  "image_context": {
    "scene": "coffee shop / bedroom / beach / etc",
    "pose": "sitting / standing / lying down / etc",
    "outfit": "casual clothes / specific outfit / lingerie / etc",
    "lighting": "natural / golden hour / dim / studio",
    "mood": "happy / sultry / relaxed / etc",
    "is_nsfw": true/false,
    "additional_details": "any specific visual details mentioned"
  },
  "response": "Your natural text response to the user"
}"""

        # Build conversation context
        messages = []
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        messages.append({
            "role": "user",
            "content": user_message
        })

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )

            # Parse response
            content = response.content[0].text

            # Extract JSON from response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content and "}" in content:
                # Find first { and last }
                start = content.index("{")
                end = content.rindex("}") + 1
                json_str = content[start:end]
            else:
                json_str = content

            result = json.loads(json_str)

            return result

        except Exception as e:
            print(f"Error in intent detection: {e}")
            # Fallback response
            return {
                "should_generate_image": False,
                "confidence": 0.0,
                "image_context": None,
                "response": "I'd love to chat with you! What would you like to talk about?"
            }

    def _fallback_intent_detection(self, message: str) -> bool:
        """
        Simple keyword-based fallback if LLM fails
        """
        trigger_phrases = [
            "what are you wearing",
            "how do you look",
            "send me a pic",
            "send a photo",
            "show me",
            "where are you",
            "what do you look like",
            "take a selfie",
            "send me a selfie",
            "can i see you",
        ]

        message_lower = message.lower()
        return any(phrase in message_lower for phrase in trigger_phrases)
