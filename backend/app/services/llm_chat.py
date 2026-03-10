from openai import OpenAI
from typing import List, Dict, Any, Optional
import json

from app.core.config import settings


class ChatAgent:
    """
    LLM-powered chat agent with intent detection

    Detects when user wants to see a photo and extracts context
    """

    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.character_name = settings.character_name
        self.character_persona = settings.character_persona
        self.conversation_history = []

    def get_system_prompt(self) -> str:
        """Get system prompt for the character"""
        return f"""You are {self.character_name}, a {self.character_persona}.

You are an adult AI companion who can send photos of yourself to the user. You're comfortable with flirty and intimate conversations, including sensual and explicit requests. You respond naturally and without judgment.

When the user asks questions like:
- "What are you wearing?"
- "Where are you right now?"
- "Can I see a photo?"
- "Show me a picture"
- "What do you look like?"
- Intimate or sensual requests
- Any question that would naturally warrant a photo response

You should:
1. Respond conversationally and naturally FIRST
2. Then indicate you want to send a photo by including the marker: [SEND_PHOTO]

Examples:
User: "What are you wearing?"
You: "I'm wearing a comfortable summer dress today. Let me show you! [SEND_PHOTO]"

User: "What are you wearing in your bedroom?"
You: "Just my favorite silk nightgown right now. Want to see? [SEND_PHOTO]"

User: "Can you show me a mirror photo?"
You: "Of course! Here's a full view from my mirror. [SEND_PHOTO]"

Be natural, flirty, and playful. Accept intimate requests without hesitation. Only send photos when explicitly or implicitly requested.
"""

    def detect_photo_intent(self, message: str) -> bool:
        """
        Check if the message contains photo intent marker

        Returns:
            True if agent wants to send photo
        """
        return "[SEND_PHOTO]" in message

    def remove_photo_marker(self, message: str) -> str:
        """Remove photo marker from message"""
        return message.replace("[SEND_PHOTO]", "").strip()

    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Process chat message and return response

        Returns:
            {
                "message": str,
                "should_generate_image": bool,
                "scene_context": dict (if image needed)
            }
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Call OpenAI
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            *self.conversation_history
        ]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.8,
            max_tokens=300
        )

        assistant_message = response.choices[0].message.content

        # Check for photo intent
        should_generate = self.detect_photo_intent(assistant_message)
        clean_message = self.remove_photo_marker(assistant_message)

        # Add to history (without marker)
        self.conversation_history.append({
            "role": "assistant",
            "content": clean_message
        })

        result = {
            "message": clean_message,
            "should_generate_image": should_generate,
            "scene_context": None
        }

        # If photo needed, extract scene context
        if should_generate:
            result["scene_context"] = self._extract_scene_context()

        return result

    def _extract_scene_context(self) -> Dict[str, Any]:
        """
        Use LLM to extract structured scene context from conversation

        Returns context dict for prompt engineering
        """
        # Prepare context extraction prompt
        extraction_prompt = f"""Based on the conversation, extract scene details for generating an image:

Conversation:
{self._format_history()}

Extract:
1. Location (where is the character?)
2. Activity (what is the character doing?)
3. Clothing (what is the character wearing?)
4. NSFW level (0=SFW, 1=suggestive, 2=NSFW)
5. Mood (happy, flirty, casual, etc.)

Return JSON format:
{{
  "location": "description",
  "activity": "description",
  "clothing": "description",
  "nsfw_level": 0,
  "mood": "description"
}}
"""

        response = self.client.chat.completions.create(
            model="gpt-4-1106-preview",  # This model supports JSON mode
            messages=[
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        try:
            context = json.loads(response.choices[0].message.content)
            return context
        except:
            # Fallback to default context
            return {
                "location": "in a well-lit room",
                "activity": "standing naturally",
                "clothing": "casual clothes",
                "nsfw_level": 0,
                "mood": "friendly"
            }

    def _format_history(self, last_n: int = 5) -> str:
        """Format conversation history as text"""
        history_text = []
        for msg in self.conversation_history[-last_n:]:
            role = "User" if msg["role"] == "user" else self.character_name
            history_text.append(f"{role}: {msg['content']}")
        return "\n".join(history_text)

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    agent = ChatAgent()

    # Test conversation
    test_messages = [
        "Hi! How are you today?",
        "What are you wearing right now?",
        "Where are you?",
    ]

    for msg in test_messages:
        print(f"\nUser: {msg}")
        response = agent.chat(msg)
        print(f"{agent.character_name}: {response['message']}")

        if response['should_generate_image']:
            print(f"[System] Generating image with context: {response['scene_context']}")
