"""Pydantic models for request/response schemas"""

from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Chat request with optional character gender"""
    message: str
    character_gender: Optional[str] = "woman"


class ChatResponse(BaseModel):
    """Chat response with optional generated image"""
    message: str
    image_generated: bool
    image_base64: Optional[str] = None


class GenerateImageRequest(BaseModel):
    """Direct image generation request for Z-Turbo workflow"""
    positive_prompt: str  # Natural language, 100-300 words
    negative_prompt: str
    reference_image: Optional[str] = None
    seed: Optional[int] = None
    steps: int = 8  # Z-Turbo default
    cfg_scale: float = 1.0  # Z-Turbo default
    megapixel: str = "2.0"
    aspect_ratio: str = "5:7 (Balanced Portrait)"


class SetReferenceRequest(BaseModel):
    """Set reference image for character consistency"""
    image_path: str
    gender: str = "woman"
