import json
import uuid
import requests
import websocket
import time
from typing import Dict, Any, Optional
from pathlib import Path
import io
from PIL import Image
import base64

from app.core.config import settings


class ComfyUIClient:
    """Client for interacting with ComfyUI API"""

    def __init__(self, server_url: str = None):
        self.server_url = server_url or settings.comfyui_url
        self.client_id = str(uuid.uuid4())
        self.ws = None

    def load_workflow(self, workflow_path: str = None) -> Dict[str, Any]:
        """Load workflow JSON file"""
        path = workflow_path or settings.workflow_path
        with open(path, 'r') as f:
            return json.load(f)

    def update_workflow_params(
        self,
        workflow: Dict[str, Any],
        positive_prompt: str,
        negative_prompt: str,
        reference_image_path: Optional[str] = None,
        seed: Optional[int] = None,
        steps: int = None,
        cfg_scale: float = None,
        megapixel: str = None,
        aspect_ratio: str = None
    ) -> Dict[str, Any]:
        """
        Update workflow parameters for Z-Turbo-Det-Swap-Upsc workflow

        Node IDs based on Z-Turbo workflow:
        - Node 306: CLIPTextEncode (Positive) - Natural language prompt
        - Node 297: CLIPTextEncode (Negative)
        - Node 363: LoadImage (Reference for face swap)
        - Node 301: KSampler (Main sampler)
        - Node 264: FluxResolutionNode (Resolution)
        - Node 355: ReActorFaceSwap
        - Node 294: FastNodeBypasser (Detailer enable/disable)
        """
        # Update prompts (natural language for Z-Turbo)
        if "306" in workflow:
            workflow["306"]["inputs"]["text"] = positive_prompt

        if "297" in workflow:
            workflow["297"]["inputs"]["text"] = negative_prompt

        # Update reference image for face swap
        if reference_image_path and "363" in workflow:
            workflow["363"]["inputs"]["image"] = reference_image_path

        # Update sampler settings (Node 301: KSampler)
        if "301" in workflow:
            if seed is not None:
                workflow["301"]["inputs"]["seed"] = seed
            if steps is not None:
                workflow["301"]["inputs"]["steps"] = steps or settings.default_steps
            if cfg_scale is not None:
                workflow["301"]["inputs"]["cfg"] = cfg_scale or settings.default_cfg_scale

        # Update resolution (Node 264: FluxResolutionNode)
        if "264" in workflow:
            if megapixel is not None:
                workflow["264"]["inputs"]["megapixel"] = megapixel or settings.default_megapixel
            if aspect_ratio is not None:
                workflow["264"]["inputs"]["aspect_ratio"] = aspect_ratio or settings.default_aspect_ratio

        # Update detailer settings (Node 294: FastNodeBypasser)
        if "294" in workflow:
            workflow["294"]["inputs"]["Enable ✨  Face Detailer"] = settings.enable_face_detailer
            workflow["294"]["inputs"]["Enable ✨  Eyes Detailer"] = settings.enable_eyes_detailer
            workflow["294"]["inputs"]["Enable ✨  Hands Detailer"] = settings.enable_hands_detailer
            workflow["294"]["inputs"]["Enable ✨  Nipples Detailer"] = settings.enable_nipples_detailer
            workflow["294"]["inputs"]["Enable ✨  Pussy Detailer"] = settings.enable_pussy_detailer

        # Update seed variance enhancer (Node 274)
        if "274" in workflow and seed is not None:
            workflow["274"]["inputs"]["seed"] = seed

        return workflow

    def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """Queue a prompt for generation"""
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }

        response = requests.post(
            f"{self.server_url}/prompt",
            json=payload
        )
        response.raise_for_status()

        result = response.json()
        prompt_id = result.get("prompt_id")

        if not prompt_id:
            raise Exception(f"Failed to queue prompt: {result}")

        return prompt_id

    def connect_websocket(self):
        """Connect to ComfyUI websocket for real-time updates"""
        ws_url = self.server_url.replace("http", "ws") + f"/ws?clientId={self.client_id}"
        self.ws = websocket.create_connection(ws_url)

    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for prompt to complete and return result"""
        if not self.ws:
            self.connect_websocket()

        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Generation timed out after {timeout} seconds")

            try:
                message = self.ws.recv()
                if not message:
                    continue

                data = json.loads(message)

                # Check if this is our prompt
                if data.get("type") == "executing":
                    executing_data = data.get("data", {})
                    if executing_data.get("prompt_id") == prompt_id:
                        node = executing_data.get("node")
                        if node is None:
                            # Execution finished
                            return self.get_images(prompt_id)

            except Exception as e:
                print(f"WebSocket error: {e}")
                time.sleep(1)

    def get_images(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get generated images from history

        Z-Turbo workflow SaveImage nodes:
        - Node 266: Z-Image (RAW)
        - Node 289: Z-Image-Detailer
        - Node 404: FaceSwap/ComfyUI
        - Node 395: SeedVR2/ComfyUI (FINAL - this is what we want!)
        """
        response = requests.get(f"{self.server_url}/history/{prompt_id}")
        response.raise_for_status()

        history = response.json()

        if prompt_id not in history:
            raise Exception(f"Prompt {prompt_id} not found in history")

        outputs = history[prompt_id].get("outputs", {})
        all_images = []

        # Collect all images with their node IDs
        for node_id, output_data in outputs.items():
            if "images" in output_data:
                for image_data in output_data["images"]:
                    filename = image_data.get("filename")
                    subfolder = image_data.get("subfolder", "")
                    folder_type = image_data.get("type", "output")

                    all_images.append({
                        "node_id": node_id,
                        "filename": filename,
                        "subfolder": subfolder,
                        "type": folder_type
                    })
                    print(f"[ComfyUI] Found image: node_{node_id} -> {subfolder}/{filename}")

        # Priority: Get SeedVR2 output (node 395) - FINAL UPSCALED OUTPUT
        # This is the intended final output: Base → Detailers → FaceSwap → SeedVR2 Upscale
        final_image = None

        # First priority: SeedVR2 output (node 395) - FINAL OUTPUT
        for img in all_images:
            if img["node_id"] == "395" or "SeedVR2" in img.get("subfolder", ""):
                final_image = img
                print(f"[ComfyUI] ✅ Selected SeedVR2 upscaled image: {img['subfolder']}/{img['filename']}")
                break

        # Second priority: FaceSwap output (node 404)
        if not final_image:
            for img in all_images:
                if img["node_id"] == "404" or "FaceSwap" in img.get("subfolder", ""):
                    final_image = img
                    print(f"[ComfyUI] Selected FaceSwap image: {img['subfolder']}/{img['filename']}")
                    break

        # Third priority: Detailer output (node 289)
        if not final_image:
            for img in all_images:
                if img["node_id"] == "289" or "Detailer" in img.get("filename", ""):
                    final_image = img
                    print(f"[ComfyUI] Selected Detailer image: {img['subfolder']}/{img['filename']}")
                    break

        # Fallback: Last image in the list
        if not final_image and all_images:
            final_image = all_images[-1]
            print(f"[ComfyUI] Selected last image: {final_image['subfolder']}/{final_image['filename']}")

        # Return the final image first, then all others
        if final_image:
            # Remove final_image from all_images to avoid duplicates
            all_images = [img for img in all_images if img != final_image]
            images = [final_image] + all_images
        else:
            images = all_images

        return {
            "prompt_id": prompt_id,
            "images": images
        }

    def is_black_image(self, image: Image.Image, threshold: float = 10.0) -> bool:
        """
        Check if image is mostly black (failed generation)

        Args:
            image: PIL Image
            threshold: Average brightness threshold (0-255)

        Returns:
            True if image is mostly black
        """
        try:
            # Convert to grayscale and get average brightness
            grayscale = image.convert('L')
            pixels = list(grayscale.getdata())
            avg_brightness = sum(pixels) / len(pixels)

            is_black = avg_brightness < threshold
            if is_black:
                print(f"[ComfyUI] ⚠️  Black image detected! Avg brightness: {avg_brightness:.2f}")

            return is_black
        except Exception as e:
            print(f"[ComfyUI] Error checking image: {e}")
            return False

    def download_image(self, image_info: Dict[str, str]) -> Image.Image:
        """Download image from ComfyUI server"""
        params = {
            "filename": image_info["filename"],
            "subfolder": image_info.get("subfolder", ""),
            "type": image_info.get("type", "output")
        }

        response = requests.get(
            f"{self.server_url}/view",
            params=params
        )
        response.raise_for_status()

        return Image.open(io.BytesIO(response.content))

    def generate_image(
        self,
        positive_prompt: str,
        negative_prompt: str,
        reference_image_path: Optional[str] = None,
        seed: Optional[int] = None,
        steps: int = None,
        cfg_scale: float = None,
        megapixel: str = None,
        aspect_ratio: str = None
    ) -> Image.Image:
        """
        High-level method to generate an image using Z-Turbo workflow

        Args:
            positive_prompt: Natural language positive prompt (100-300 words)
            negative_prompt: Negative text prompt
            reference_image_path: Path to reference face image for face swap
            seed: Random seed (None for random)
            steps: Number of sampling steps (default: 8 for Z-Turbo)
            cfg_scale: CFG scale (default: 1.0 for Z-Turbo)
            megapixel: Megapixel setting (e.g., "2.0")
            aspect_ratio: Aspect ratio (e.g., "5:7 (Balanced Portrait)")

        Returns:
            PIL Image object with detailers and upscaling applied
        """
        # Load workflow
        workflow = self.load_workflow()

        # Update parameters
        workflow = self.update_workflow_params(
            workflow=workflow,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            reference_image_path=reference_image_path,
            seed=seed,
            steps=steps or settings.default_steps,
            cfg_scale=cfg_scale or settings.default_cfg_scale,
            megapixel=megapixel or settings.default_megapixel,
            aspect_ratio=aspect_ratio or settings.default_aspect_ratio
        )

        # Queue prompt
        prompt_id = self.queue_prompt(workflow)
        print(f"[Z-Turbo] Queued prompt: {prompt_id}")
        print(f"[Z-Turbo] Using {steps or settings.default_steps} steps, CFG: {cfg_scale or settings.default_cfg_scale}")

        # Wait for completion
        result = self.wait_for_completion(prompt_id, timeout=600)  # Longer timeout for upscaling

        # Download first image (upscaled result)
        if result["images"]:
            image = self.download_image(result["images"][0])
            return image
        else:
            raise Exception("No images generated")

    def close(self):
        """Close websocket connection"""
        if self.ws:
            self.ws.close()
            self.ws = None
