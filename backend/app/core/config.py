from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    anthropic_api_key: Optional[str] = None

    # ComfyUI Settings
    comfyui_url: str = "http://127.0.0.1:8188"
    workflow_path: str = "../workflows/Z-Turbo-Det-Swap-Upsc .json"

    # Generation Settings (Z-Turbo workflow)
    default_steps: int = 8  # Z-Turbo uses fewer steps
    default_cfg_scale: float = 1.0  # Z-Turbo uses low CFG
    default_megapixel: str = "2.0"
    default_aspect_ratio: str = "5:7 (Balanced Portrait)"

    # Detailer settings
    enable_face_detailer: bool = True
    enable_eyes_detailer: bool = True
    enable_hands_detailer: bool = True
    enable_nipples_detailer: bool = True
    enable_pussy_detailer: bool = True

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Character Settings
    character_name: str = "Emma"
    character_persona: str = "friendly, flirty, and playful AI companion"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env file
    )


settings = Settings()
