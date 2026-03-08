# ComfyUI Workflow Setup for Character Consistency

## Overview

This directory contains ComfyUI workflows for generating character-consistent images using InstantID.

## Required Setup

### 1. Install ComfyUI on RunPod

```bash
# SSH into your RunPod instance
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt
pip install xformers

# Install ComfyUI Manager (for easy node management)
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
```

### 2. Required Custom Nodes

Install these via ComfyUI Manager or manually:

```bash
cd ComfyUI/custom_nodes

# InstantID nodes
git clone https://github.com/cubiq/ComfyUI_InstantID.git
cd ComfyUI_InstantID && pip install -r requirements.txt && cd ..

# IP-Adapter (alternative/complementary)
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# ControlNet
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
cd comfyui_controlnet_aux && pip install -r requirements.txt && cd ..

# Face Restoration/Enhancement
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
cd ComfyUI-Impact-Pack && pip install -r requirements.txt && cd ..

# ADetailer for anatomy fixes
git clone https://github.com/Bing-su/adetailer.git
```

### 3. Required Models

Download these models to the appropriate directories:

#### Base Models (`ComfyUI/models/checkpoints/`)

**Primary (choose one):**
- **SDXL 1.0**: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- **Pony Diffusion XL v6**: https://civitai.com/models/257749/pony-diffusion-v6-xl (for better NSFW)
- **Realistic Vision XL**: https://civitai.com/models/245598/realistic-vision-xl

**Recommended: Pony Diffusion XL** for best NSFW anatomical correctness

#### InstantID Models (`ComfyUI/models/instantid/`)

```bash
cd ComfyUI/models
mkdir -p instantid

# InstantID model
wget https://huggingface.co/InstantX/InstantID/resolve/main/ip-adapter.bin -O instantid/ip-adapter.bin

# ControlNet model for InstantID
wget https://huggingface.co/InstantX/InstantID/resolve/main/ControlNetModel/diffusion_pytorch_model.safetensors -O instantid/controlnet.safetensors
```

#### Face Analysis Model (`ComfyUI/models/insightface/`)

```bash
mkdir -p insightface/models/antelopev2
cd insightface/models/antelopev2

# Download InsightFace models
wget https://huggingface.co/MonsterMMORPG/tools/resolve/main/antelopev2.zip
unzip antelopev2.zip
```

#### LoRAs (Optional, `ComfyUI/models/loras/`)

For enhanced results:
- Anatomy LoRAs for better body generation
- Detail LoRAs for face enhancement
- Style LoRAs for specific aesthetics

### 4. Start ComfyUI

```bash
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

For RunPod, expose port 8188 in your pod configuration.

## Workflow Architecture

### character_consistency.json

This workflow implements:

1. **Reference Image Loading**: Load character face reference
2. **InstantID Processing**: Extract facial features and create identity embedding
3. **Prompt Conditioning**: Combine text prompt with identity embedding
4. **ControlNet (Optional)**: Add pose/depth control if needed
5. **SDXL Generation**: Generate image with identity preservation
6. **Face Restoration**: Enhance face details (CodeFormer/ADetailer)
7. **Final Output**: Save high-quality result

### Node Flow

```
┌─────────────────────┐
│  Load Reference     │
│  Image              │
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  InsightFace        │
│  Face Analysis      │
└──────┬──────────────┘
       │
┌──────▼──────────────┐       ┌─────────────────┐
│  InstantID          │       │  CLIP Text      │
│  Face Embedding     │◄──────┤  Encode         │
└──────┬──────────────┘       └─────────────────┘
       │
┌──────▼──────────────┐
│  ControlNet         │
│  (optional)         │
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  KSampler           │
│  (SDXL)             │
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  VAE Decode         │
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  Face Enhance       │
│  (ADetailer)        │
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  Save Image         │
└─────────────────────┘
```

## Key Parameters for Consistency

### InstantID Settings

```json
{
  "ip_adapter_scale": 0.85,  // Higher = stronger identity, but may reduce flexibility
  "controlnet_conditioning_scale": 0.6  // Balance between identity and prompt
}
```

### Generation Settings

```json
{
  "steps": 30-35,  // More steps for NSFW (better anatomy)
  "cfg_scale": 7.5,  // Standard for photorealism
  "sampler": "DPM++ 2M Karras",  // Good balance of quality/speed
  "scheduler": "karras",
  "denoise": 1.0
}
```

### Face Enhancement

```json
{
  "adetailer_model": "face_yolov8n.pt",
  "confidence_threshold": 0.3,
  "dilation": 4,
  "denoising_strength": 0.4  // Lower = preserve more of original
}
```

## Workflow Optimization Tips

1. **Model Loading**: Keep models in VRAM between generations
   - Use `--reserve-vram` flag
   - Don't unload models after each generation

2. **Batch Processing**: Generate multiple sizes/variations in one pass

3. **xFormers**: Already installed, enables memory-efficient attention

4. **Half Precision**: Use FP16 for 2x speed, minimal quality loss
   ```python
   --fp16  # Add to ComfyUI launch command
   ```

5. **TensorRT** (Advanced): Convert models for 2-3x speedup
   ```bash
   # Install TensorRT nodes
   cd custom_nodes
   git clone https://github.com/comfyanonymous/ComfyUI-TensorRT
   ```

## Testing the Workflow

1. Place a reference face image in `reference_images/test_face.jpg`

2. Test via API:
   ```python
   import requests

   workflow = {
       # ... your workflow with parameters
   }

   response = requests.post(
       "http://localhost:8188/prompt",
       json={"prompt": workflow}
   )
   ```

3. Monitor via ComfyUI web interface: `http://localhost:8188`

## Troubleshooting

### Identity Drift Issues

**Problem**: Face doesn't look consistent
**Solutions**:
- Increase `ip_adapter_scale` (0.85 → 0.95)
- Use higher resolution reference image (1024x1024+)
- Enable face restoration post-processing
- Use multiple reference angles if available

### Anatomy Issues (NSFW)

**Problem**: Incorrect limb count, weird hands
**Solutions**:
- Enable ADetailer with hand detection
- Use anatomy LoRA
- Increase generation steps (30 → 40)
- Add negative prompts: "extra fingers, mutated hands, fused fingers"

### Slow Generation

**Problem**: Taking too long per image
**Solutions**:
- Reduce steps (40 → 25-30)
- Use faster sampler (Euler a)
- Enable xFormers
- Consider TensorRT conversion

### Out of Memory

**Problem**: CUDA OOM errors
**Solutions**:
- Reduce resolution (1024 → 768)
- Enable `--lowvram` flag
- Unload unused models
- Use smaller base model

## API Integration

The `image_generation.py` service connects to ComfyUI via:

1. **HTTP API**: Submit workflow via `/prompt` endpoint
2. **WebSocket**: Monitor generation progress
3. **Image Download**: Retrieve output via `/view` endpoint

See `backend/app/services/image_generation.py` for implementation.

## Export Workflow for Submission

To export your workflow:

1. Open ComfyUI web interface
2. Build your workflow
3. Click "Save" → "Save API Format" → `workflow_api.json`
4. Or "Save" → "Save" → `workflow.json` (with metadata)

Include both formats in this directory for submission.
