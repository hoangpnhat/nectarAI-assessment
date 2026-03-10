"""API route definitions"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import io
import base64
from pathlib import Path
import random

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    GenerateImageRequest,
    SetReferenceRequest
)
from app.core.config import settings
from app.services import ComfyUIClient, ChatAgent, PromptEngineer, NSFWEnhancer, ReferenceAnalyzer

# Initialize router
router = APIRouter()

# Initialize services
comfyui_client = ComfyUIClient()
chat_agent = ChatAgent()
prompt_engineer = PromptEngineer()
nsfw_enhancer = NSFWEnhancer()
reference_analyzer = ReferenceAnalyzer()

# Global state (in production, use proper state management)
REFERENCE_IMAGE_PATH = None
CHARACTER_GENDER = "woman"
REFERENCE_FEATURES = None  # Extracted features from reference image


def detect_nsfw_level(message: str) -> int:
    """
    Detect NSFW level from user message

    Returns:
        0 = SFW (safe for work)
        1 = Suggestive (intimate but not explicit)
        2 = NSFW (explicit)
    """
    message_lower = message.lower()

    # Explicit NSFW keywords (level 2)
    explicit_keywords = [
        "nude", "naked", "full body", "mirror photo", "shower",
        "bath", "explicit", "nsfw"
    ]

    for keyword in explicit_keywords:
        if keyword in message_lower:
            return 2

    # Suggestive keywords (level 1)
    suggestive_keywords = [
        "bedroom", "lingerie", "underwear", "underneath",
        "intimate", "sensual", "sexy", "revealing"
    ]

    for keyword in suggestive_keywords:
        if keyword in message_lower:
            return 1

    # Default SFW (level 0)
    return 0


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "message": "Nectar AI Image Generation API",
        "version": "1.0.0"
    }


@router.get("/health")
async def health_check():
    """Check if ComfyUI is accessible"""
    try:
        import requests
        response = requests.get(f"{settings.comfyui_url}/system_stats")
        comfyui_status = "ok" if response.status_code == 200 else "error"
    except:
        comfyui_status = "error"

    return {
        "api": "ok",
        "comfyui": comfyui_status,
        "reference_image_set": REFERENCE_IMAGE_PATH is not None
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint with automatic image generation

    If the character decides to send a photo, it will be generated and returned
    Uses extracted reference features to enhance prompt consistency
    """
    global REFERENCE_IMAGE_PATH, CHARACTER_GENDER, REFERENCE_FEATURES

    try:
        # Process chat
        response = chat_agent.chat(request.message)

        result = ChatResponse(
            message=response["message"],
            image_generated=False,
            image_base64=None
        )

        # Generate image if needed
        if response["should_generate_image"]:
            try:
                # Build prompt from scene context
                scene_context = response.get("scene_context", {})

                # Detect NSFW level from user message
                nsfw_level = detect_nsfw_level(request.message)

                # Enhance scene context with NSFW keywords if needed
                if nsfw_level > 0:
                    scene_context = nsfw_enhancer.enhance_scene_context(
                        scene_context,
                        nsfw_level=nsfw_level
                    )
                    print(f"[NSFW Enhancement] Level {nsfw_level} applied to scene")

                # Use prompt engineer to create optimized prompts
                # Include reference features for better consistency
                prompts = prompt_engineer.build_prompt(
                    scene_context=scene_context,
                    character_gender=request.character_gender or CHARACTER_GENDER,
                    reference_features=REFERENCE_FEATURES
                )

                # Generate image with Z-Turbo workflow
                print(f"[Z-Turbo] Generating with NSFW level: {nsfw_level}")
                print(f"[Z-Turbo] Prompt length: {len(prompts['positive'].split())} words")

                image = comfyui_client.generate_image(
                    positive_prompt=prompts["positive"],
                    negative_prompt=prompts["negative"],
                    reference_image_path=REFERENCE_IMAGE_PATH,
                    seed=random.randint(0, 2**32 - 1),
                    steps=settings.default_steps,
                    cfg_scale=settings.default_cfg_scale,
                    megapixel=settings.default_megapixel,
                    aspect_ratio=settings.default_aspect_ratio
                )

                # Convert to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()

                result.image_generated = True
                result.image_base64 = img_base64

            except Exception as e:
                print(f"Image generation error: {e}")
                result.message += "\n\n[Sorry, I couldn't generate the image right now]"

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-image")
async def generate_image(request: GenerateImageRequest):
    """
    Direct image generation endpoint (bypassing chat)

    Useful for testing and manual control with Z-Turbo workflow
    """
    global REFERENCE_IMAGE_PATH

    try:
        print(f"[Z-Turbo Direct] Generating with prompt length: {len(request.positive_prompt.split())} words")

        image = comfyui_client.generate_image(
            positive_prompt=request.positive_prompt,
            negative_prompt=request.negative_prompt,
            reference_image_path=request.reference_image or REFERENCE_IMAGE_PATH,
            seed=request.seed,
            steps=request.steps,
            cfg_scale=request.cfg_scale,
            megapixel=request.megapixel,
            aspect_ratio=request.aspect_ratio
        )

        # Return as PNG
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)

        return StreamingResponse(buffered, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-reference")
async def set_reference(request: SetReferenceRequest):
    """
    Set reference image for character consistency

    Automatically analyzes reference image using GPT-4 Vision to extract:
    - Gender, age range, ethnicity
    - Skin tone, body type
    - Hair color, style, length
    - Facial hair (for men)
    - Eye color, face shape
    - Distinctive features (high cheekbones, freckles, etc.)

    These features are used to enhance prompt generation for better consistency.

    Args:
        image_path: Path to reference image (relative to ComfyUI input folder)
        gender: "man" or "woman"
    """
    global REFERENCE_IMAGE_PATH, CHARACTER_GENDER, REFERENCE_FEATURES

    REFERENCE_IMAGE_PATH = request.image_path
    CHARACTER_GENDER = request.gender

    # Analyze reference image with GPT-4 Vision
    print(f"[API] Analyzing reference image: {request.image_path}")
    try:
        features = reference_analyzer.analyze_reference_image(request.image_path)
        REFERENCE_FEATURES = features

        print(f"[API] ✅ Reference analysis complete")
        print(f"     Detected: {features.get('ethnicity', 'N/A')} {features.get('gender', 'N/A')}")
        print(f"     Hair: {features.get('hair_color', 'N/A')} {features.get('hair_length', 'N/A')}")
        print(f"     Features: {', '.join(features.get('distinctive_features', [])[:3])}")

        return {
            "status": "ok",
            "reference_image": REFERENCE_IMAGE_PATH,
            "character_gender": CHARACTER_GENDER,
            "features": features,
            "compact_description": reference_analyzer.format_features_for_prompt(features)
        }
    except Exception as e:
        print(f"[API] ⚠️  Reference analysis failed: {e}")
        print(f"[API] Continuing without detailed features")
        REFERENCE_FEATURES = None

        return {
            "status": "ok",
            "reference_image": REFERENCE_IMAGE_PATH,
            "character_gender": CHARACTER_GENDER,
            "features": None,
            "error": f"Feature extraction failed: {str(e)}"
        }


@router.post("/upload-reference")
async def upload_reference(file: UploadFile = File(...), gender: str = "woman"):
    """
    Upload reference image file

    Automatically analyzes uploaded image to extract character features.

    Returns the filename that can be used with set-reference
    """
    global REFERENCE_IMAGE_PATH, CHARACTER_GENDER, REFERENCE_FEATURES

    try:
        # Save to ComfyUI input folder
        comfyui_input_dir = Path("../ComfyUI/input")
        comfyui_input_dir.mkdir(parents=True, exist_ok=True)

        file_path = comfyui_input_dir / file.filename

        # Write file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Set as current reference
        REFERENCE_IMAGE_PATH = file.filename
        CHARACTER_GENDER = gender

        # Analyze uploaded reference image
        print(f"[API] Analyzing uploaded reference: {file.filename}")
        try:
            features = reference_analyzer.analyze_reference_image(file.filename)
            REFERENCE_FEATURES = features

            print(f"[API] ✅ Upload analysis complete")

            return {
                "status": "ok",
                "filename": file.filename,
                "path": str(file_path),
                "character_gender": gender,
                "features": features,
                "compact_description": reference_analyzer.format_features_for_prompt(features)
            }
        except Exception as e:
            print(f"[API] ⚠️  Upload analysis failed: {e}")
            REFERENCE_FEATURES = None

            return {
                "status": "ok",
                "filename": file.filename,
                "path": str(file_path),
                "character_gender": gender,
                "features": None,
                "error": f"Feature extraction failed: {str(e)}"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-conversation")
async def reset_conversation():
    """Reset chat history"""
    chat_agent.reset_conversation()
    return {"status": "ok", "message": "Conversation reset"}


@router.get("/conversation-history")
async def get_conversation_history():
    """Get current conversation history"""
    return {
        "history": chat_agent.conversation_history,
        "count": len(chat_agent.conversation_history)
    }
