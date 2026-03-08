"""
FastAPI application for AI Image Generation with Character Consistency
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from dotenv import load_dotenv

from app.services.intent_detection import IntentDetectionService
from app.services.image_generation import ImageGenerationService
from app.services.prompt_engineering import PromptEngineeringService
from app.models.schemas import ChatMessage, ImageGenerationRequest, ImageGenerationResponse

load_dotenv()

app = FastAPI(
    title="Nectar AI - Character Consistent Image Generation",
    description="Multi-modal chat with character-consistent image generation",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
intent_service = IntentDetectionService()
prompt_service = PromptEngineeringService()
image_service = ImageGenerationService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting Nectar AI Image Generation Service...")
    await image_service.initialize()
    print("✅ Services initialized successfully")

@app.get("/")
async def root():
    return {
        "message": "Nectar AI - Character Consistent Image Generation API",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    comfyui_status = await image_service.check_comfyui_status()
    return {
        "status": "healthy",
        "comfyui_connected": comfyui_status,
        "services": {
            "intent_detection": True,
            "prompt_engineering": True,
            "image_generation": comfyui_status
        }
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """
    Process chat message and determine if image generation is needed
    """
    try:
        # Detect intent
        intent_result = await intent_service.analyze_message(
            message.content,
            message.conversation_history
        )

        response = {
            "message": intent_result["response"],
            "should_generate_image": intent_result["should_generate_image"],
            "image_context": intent_result.get("image_context")
        }

        # If image generation is needed, generate it
        if intent_result["should_generate_image"]:
            image_context = intent_result["image_context"]

            # Engineer prompt from context
            prompt_data = prompt_service.create_prompt(
                character_description=message.character_description,
                context=image_context
            )

            # Generate image
            image_result = await image_service.generate_image(
                reference_image_path=message.reference_image_path,
                prompt=prompt_data["prompt"],
                negative_prompt=prompt_data["negative_prompt"],
                settings=prompt_data["settings"]
            )

            response["image_url"] = image_result["image_url"]
            response["generation_time"] = image_result["generation_time"]

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-image")
async def generate_image(request: ImageGenerationRequest):
    """
    Direct image generation endpoint
    """
    try:
        # Engineer prompt
        prompt_data = prompt_service.create_prompt(
            character_description=request.character_description,
            context={
                "scene": request.scene,
                "pose": request.pose,
                "outfit": request.outfit,
                "lighting": request.lighting,
                "is_nsfw": request.is_nsfw
            }
        )

        # Generate image
        result = await image_service.generate_image(
            reference_image_path=request.reference_image_path,
            prompt=prompt_data["prompt"],
            negative_prompt=prompt_data["negative_prompt"],
            settings=prompt_data["settings"]
        )

        return ImageGenerationResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-reference")
async def upload_reference(file: UploadFile = File(...)):
    """
    Upload character reference image
    """
    try:
        # Save uploaded file
        upload_dir = "reference_images"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        return {
            "filename": file.filename,
            "path": file_path,
            "size": len(content)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/images/{image_id}")
async def get_image(image_id: str):
    """
    Retrieve generated image
    """
    image_path = os.path.join("generated_images", f"{image_id}.png")

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)

@app.get("/api/examples")
async def get_examples():
    """
    Get example generated images for demonstration
    """
    examples_dir = "generated_images/examples"
    if not os.path.exists(examples_dir):
        return {"examples": []}

    examples = []
    for filename in os.listdir(examples_dir):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            examples.append({
                "filename": filename,
                "url": f"/api/images/examples/{filename}"
            })

    return {"examples": examples}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    )
