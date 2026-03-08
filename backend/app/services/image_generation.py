"""
Image Generation Service using ComfyUI API
Handles character-consistent image generation with InstantID
"""
import os
import json
import uuid
import time
import asyncio
from typing import Dict, Any, Optional
import aiohttp
import websocket
from PIL import Image
import base64
from io import BytesIO

class ImageGenerationService:
    def __init__(self):
        self.comfyui_url = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)

        # Load workflow template
        self.workflow_template = None

    async def initialize(self):
        """Initialize service and load workflow"""
        print(f"🔧 Initializing Image Generation Service")
        print(f"   ComfyUI URL: {self.comfyui_url}")

        # Load workflow if exists
        workflow_path = "workflows/character_consistency.json"
        if os.path.exists(workflow_path):
            with open(workflow_path, 'r') as f:
                self.workflow_template = json.load(f)
            print(f"   ✓ Loaded workflow from {workflow_path}")
        else:
            print(f"   ⚠ Workflow not found at {workflow_path}, will use API format")

    async def check_comfyui_status(self) -> bool:
        """Check if ComfyUI is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.comfyui_url}/system_stats", timeout=5) as response:
                    return response.status == 200
        except Exception as e:
            print(f"ComfyUI connection error: {e}")
            return False

    async def generate_image(
        self,
        reference_image_path: str,
        prompt: str,
        negative_prompt: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate character-consistent image using InstantID

        Args:
            reference_image_path: Path to reference face image
            prompt: Positive prompt
            negative_prompt: Negative prompt
            settings: Generation settings (steps, cfg_scale, etc.)

        Returns:
            Dictionary with image_url, image_path, and generation_time
        """
        start_time = time.time()

        try:
            # If using ComfyUI workflow
            if self.workflow_template:
                result = await self._generate_with_workflow(
                    reference_image_path,
                    prompt,
                    negative_prompt,
                    settings
                )
            else:
                # Fallback to direct Diffusers generation
                result = await self._generate_with_diffusers(
                    reference_image_path,
                    prompt,
                    negative_prompt,
                    settings
                )

            generation_time = time.time() - start_time

            return {
                "image_url": result["image_url"],
                "image_path": result["image_path"],
                "generation_time": generation_time,
                "prompt": prompt,
                "settings": settings
            }

        except Exception as e:
            print(f"Error generating image: {e}")
            raise

    async def _generate_with_workflow(
        self,
        reference_image_path: str,
        prompt: str,
        negative_prompt: str,
        settings: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate image using ComfyUI workflow
        """
        # Create a copy of workflow template
        workflow = self.workflow_template.copy()

        # Update workflow nodes with parameters
        # This is a simplified version - actual implementation depends on workflow structure
        # You'll need to map parameters to specific node IDs

        # Example node updates (adjust based on actual workflow):
        # workflow["6"]["inputs"]["text"] = prompt  # CLIP Text Encode (Positive)
        # workflow["7"]["inputs"]["text"] = negative_prompt  # CLIP Text Encode (Negative)
        # workflow["3"]["inputs"]["steps"] = settings["steps"]  # KSampler
        # workflow["3"]["inputs"]["cfg"] = settings["cfg_scale"]

        # Queue the prompt
        prompt_id = str(uuid.uuid4())

        async with aiohttp.ClientSession() as session:
            payload = {
                "prompt": workflow,
                "client_id": prompt_id
            }

            async with session.post(
                f"{self.comfyui_url}/prompt",
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"ComfyUI API error: {response.status}")

                result = await response.json()
                prompt_id = result["prompt_id"]

            # Wait for generation to complete
            image_data = await self._wait_for_completion(prompt_id)

            # Save image
            image_id = str(uuid.uuid4())
            image_path = os.path.join(self.output_dir, f"{image_id}.png")

            with open(image_path, 'wb') as f:
                f.write(image_data)

            return {
                "image_url": f"/api/images/{image_id}",
                "image_path": image_path
            }

    async def _wait_for_completion(self, prompt_id: str, timeout: int = 120) -> bytes:
        """
        Wait for ComfyUI to complete generation via WebSocket
        """
        ws_url = self.comfyui_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/ws?clientId={prompt_id}"

        # For simplicity, using polling instead of WebSocket in this example
        # In production, use WebSocket for real-time updates

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < timeout:
                # Check history
                async with session.get(
                    f"{self.comfyui_url}/history/{prompt_id}"
                ) as response:
                    if response.status == 200:
                        history = await response.json()

                        if prompt_id in history:
                            outputs = history[prompt_id].get("outputs", {})

                            # Find the output image node
                            for node_id, node_output in outputs.items():
                                if "images" in node_output:
                                    image_info = node_output["images"][0]
                                    filename = image_info["filename"]
                                    subfolder = image_info.get("subfolder", "")

                                    # Download the image
                                    params = {
                                        "filename": filename,
                                        "subfolder": subfolder,
                                        "type": "output"
                                    }

                                    async with session.get(
                                        f"{self.comfyui_url}/view",
                                        params=params
                                    ) as img_response:
                                        if img_response.status == 200:
                                            return await img_response.read()

                await asyncio.sleep(2)

        raise TimeoutError("Image generation timed out")

    async def _generate_with_diffusers(
        self,
        reference_image_path: str,
        prompt: str,
        negative_prompt: str,
        settings: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Fallback: Generate using Diffusers library directly
        This is a placeholder - actual implementation would use InstantID with Diffusers
        """
        # This is where you'd implement direct Diffusers pipeline
        # For now, return a placeholder

        print("⚠ Using Diffusers fallback (not implemented yet)")
        print("   For production, implement InstantID pipeline here")

        # Placeholder: Create a simple test image
        image_id = str(uuid.uuid4())
        image_path = os.path.join(self.output_dir, f"{image_id}.png")

        # Create placeholder image
        img = Image.new('RGB', (1024, 1024), color='gray')
        img.save(image_path)

        return {
            "image_url": f"/api/images/{image_id}",
            "image_path": image_path
        }

    def load_reference_image(self, image_path: str) -> Image.Image:
        """Load and preprocess reference image"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Reference image not found: {image_path}")

        img = Image.open(image_path)

        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        return img

    def encode_image_base64(self, image_path: str) -> str:
        """Encode image to base64 for API transfer"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')
