"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ConversationMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatMessage(BaseModel):
    content: str = Field(..., description="User message content")
    conversation_history: List[ConversationMessage] = Field(
        default=[],
        description="Previous conversation messages for context"
    )
    character_description: str = Field(
        default="A beautiful person",
        description="Character description for image generation"
    )
    reference_image_path: str = Field(
        ...,
        description="Path to character reference image"
    )

class ImageGenerationRequest(BaseModel):
    reference_image_path: str = Field(..., description="Path to reference image")
    character_description: str = Field(
        default="A beautiful person",
        description="Character description"
    )
    scene: str = Field(default="portrait", description="Scene/setting description")
    pose: str = Field(default="natural pose", description="Character pose")
    outfit: str = Field(default="casual clothes", description="Outfit description")
    lighting: str = Field(default="natural lighting", description="Lighting setup")
    is_nsfw: bool = Field(default=False, description="Generate NSFW content")
    num_steps: Optional[int] = Field(default=30, description="Number of diffusion steps")
    cfg_scale: Optional[float] = Field(default=7.5, description="CFG scale")
    instantid_strength: Optional[float] = Field(default=0.85, description="InstantID conditioning strength")

class ImageGenerationResponse(BaseModel):
    image_url: str = Field(..., description="URL to generated image")
    image_path: str = Field(..., description="Server path to image")
    generation_time: float = Field(..., description="Generation time in seconds")
    prompt: str = Field(..., description="Final prompt used")
    settings: Dict[str, Any] = Field(..., description="Generation settings used")

class IntentAnalysis(BaseModel):
    should_generate_image: bool
    confidence: float
    image_context: Optional[Dict[str, str]] = None
    response: str

class PromptData(BaseModel):
    prompt: str
    negative_prompt: str
    settings: Dict[str, Any]
