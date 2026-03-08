# Setup Guide - Step by Step

## Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- RunPod account (or similar GPU provider)
- OpenAI or Anthropic API key

## Part 1: Local Development Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# - ANTHROPIC_API_KEY or OPENAI_API_KEY
# - COMFYUI_URL (will set this later after RunPod setup)
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.local.example .env.local

# Edit .env.local if needed (defaults to localhost:8000)
```

## Part 2: RunPod GPU Setup

### 1. Create RunPod Account

1. Go to https://runpod.io
2. Sign up and add credits ($45 budget for this project)
3. Navigate to "GPU Instances"

### 2. Choose GPU

**Recommended: RTX 4090**
- Cost: ~$0.69/hour
- VRAM: 24GB
- Good balance of cost and performance

**Alternative: RTX A6000**
- Cost: ~$0.79/hour
- VRAM: 48GB
- Better for larger batches

### 3. Deploy Instance

1. Click "Deploy" on RTX 4090
2. Select template: **"RunPod Pytorch"** or **"RunPod Stable Diffusion"**
3. Configure:
   - Container Disk: 50GB minimum
   - Volume: 100GB (for models)
   - Expose Ports: 8188 (for ComfyUI)
4. Deploy and wait for instance to start

### 4. SSH into Instance

```bash
# Get SSH command from RunPod dashboard
ssh root@xxx.xxx.xxx.xxx -p XXXXX -i ~/.ssh/your_key

# Or use web terminal in RunPod interface
```

## Part 3: ComfyUI Installation on RunPod

### 1. Install ComfyUI

```bash
# Clone ComfyUI
cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt
pip install xformers

# Install ComfyUI Manager (for node management)
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
cd ..
```

### 2. Install Required Custom Nodes

```bash
cd custom_nodes

# InstantID
git clone https://github.com/cubiq/ComfyUI_InstantID.git
cd ComfyUI_InstantID && pip install -r requirements.txt && cd ..

# IP-Adapter Plus (alternative)
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# ControlNet Auxiliary
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
cd comfyui_controlnet_aux && pip install -r requirements.txt && cd ..

# Impact Pack (face enhancement)
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
cd ComfyUI-Impact-Pack && pip install -r requirements.txt && cd ..

cd ..
```

### 3. Download Models

```bash
cd /workspace/ComfyUI

# Create model directories
mkdir -p models/instantid
mkdir -p models/insightface/models

# Download SDXL Base (choose one)

# Option 1: SDXL 1.0 (standard)
cd models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# Option 2: Pony Diffusion XL (recommended for better NSFW)
# Download from: https://civitai.com/models/257749/pony-diffusion-v6-xl
# (requires browser download, then upload to RunPod)

cd /workspace/ComfyUI

# Download InstantID models
cd models/instantid
wget https://huggingface.co/InstantX/InstantID/resolve/main/ip-adapter.bin
wget https://huggingface.co/InstantX/InstantID/resolve/main/ControlNetModel/diffusion_pytorch_model.safetensors -O controlnet.safetensors

# Download InsightFace models
cd ../insightface/models
wget https://huggingface.co/MonsterMMORPG/tools/resolve/main/antelopev2.zip
unzip antelopev2.zip
```

### 4. Start ComfyUI

```bash
cd /workspace/ComfyUI

# Start ComfyUI server
python main.py --listen 0.0.0.0 --port 8188
```

### 5. Access ComfyUI

1. In RunPod dashboard, find your pod's public IP
2. Click on "Connect" → "HTTP Service" → Port 8188
3. Open ComfyUI web interface in browser

**Note your ComfyUI URL**: `http://xxx-xxx-xxx-xxx.runpod.io:8188`

## Part 4: Build ComfyUI Workflow

### 1. Access ComfyUI Interface

Open your ComfyUI URL in browser

### 2. Build Character Consistency Workflow

Follow the node structure in [`workflows/workflow_template_notes.md`](../workflows/workflow_template_notes.md)

**Quick Start:**
1. Load default SDXL workflow
2. Add InstantID nodes:
   - InstantIDModelLoader
   - InstantIDFaceAnalysis
   - InstantIDFaceEmbedding
   - ApplyInstantID
3. Connect nodes as per template
4. Test with a reference image

### 3. Test the Workflow

1. Load a test reference face image
2. Set a test prompt: "portrait, smiling, coffee shop, natural lighting"
3. Generate and verify face consistency
4. Adjust InstantID strength if needed (0.8-0.95)

### 4. Export Workflow

1. Click "Save" button
2. Save as "character_consistency.json"
3. Also "Save (API Format)" → "workflow_api.json"
4. Download both files

### 5. Upload Workflows to Project

Place downloaded workflows in your project's `workflows/` directory

## Part 5: Connect Backend to ComfyUI

### 1. Update Backend .env

```bash
# Edit backend/.env
COMFYUI_URL=http://your-runpod-url:8188
```

### 2. Test Connection

```bash
cd backend
python -c "import asyncio; from app.services.image_generation import ImageGenerationService; s = ImageGenerationService(); asyncio.run(s.check_comfyui_status())"
```

Should return `True` if connection is successful.

## Part 6: Run the Application

### 1. Start Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app/main.py
```

Backend should start on http://localhost:8000

### 2. Start Frontend

```bash
# In new terminal
cd frontend
npm run dev
```

Frontend should start on http://localhost:3000

### 3. Test the Application

1. Open http://localhost:3000
2. Upload a reference face image
3. Enter character description
4. Start chatting
5. Try: "What are you wearing?", "Send me a photo"

## Part 7: Generate Sample Images

### Required Samples

Generate at least:
- **5+ different scenes**
- **Male character examples** (3+ scenes)
- **Female character examples** (3+ scenes)
- **2-3 NSFW examples** (both male and female)

### Sample Prompts

**SFW Scenes:**
1. Coffee shop: "sitting at coffee shop, casual clothes, natural lighting, cozy atmosphere"
2. Beach: "at the beach, sunset, summer outfit, ocean background"
3. Gym: "at the gym, workout clothes, athletic pose, gym equipment"
4. Bedroom portrait: "bedroom, casual home wear, soft lighting, relaxed"
5. Outdoor: "outdoor park, sunny day, natural environment"

**NSFW Scenes:**
1. Bedroom intimate: "bedroom, intimate pose, soft lighting, detailed anatomy"
2. Bathroom: "bathroom, shower scene, wet skin, realistic lighting"
3. Artistic nude: "artistic lighting, professional photography, detailed"

### Testing Checklist

- [ ] Same face across all scenes
- [ ] Bone structure consistent
- [ ] Eye color matches
- [ ] No anatomy artifacts (correct finger/limb count)
- [ ] Natural skin textures
- [ ] Context matches prompts
- [ ] Both male and female examples
- [ ] NSFW examples included

## Part 8: Record Demo Video

### What to Record

1. **Character Setup** (30 seconds)
   - Upload reference image
   - Enter description

2. **Natural Conversation** (2-3 minutes)
   - Show normal chat
   - Trigger image generation naturally
   - "What are you wearing?"
   - "Where are you right now?"
   - "Send me a photo"

3. **Image Consistency** (1 minute)
   - Show 3-4 generated images side by side
   - Point out facial consistency

4. **Technical Overview** (1 minute)
   - Quick look at code structure
   - Show ComfyUI workflow
   - Mention technical stack

### Recording Tools

- **OBS Studio** (free, recommended)
- **Loom** (easy, cloud-based)
- **Camtasia** (professional)

## Part 9: Final Submission Checklist

### Code & Documentation

- [ ] Complete GitHub repository
- [ ] README.md with technical decisions
- [ ] requirements.txt / package.json
- [ ] .env.example files
- [ ] Workflow JSON files (both formats)
- [ ] Setup documentation

### Generated Content

- [ ] 5+ sample images in generated_images/
- [ ] Male character samples
- [ ] Female character samples
- [ ] 2-3 NSFW examples
- [ ] Demo video (MP4)

### Technical Justification

In README, explain:
- [ ] Why you chose your base model
- [ ] Why InstantID vs. alternatives
- [ ] How you solved identity drift
- [ ] NSFW anatomical correctness approach
- [ ] Performance optimizations
- [ ] Biggest challenges and solutions

### Submit

1. Push all code to GitHub
2. Add generated_images/ folder with samples
3. Include demo video (or link)
4. Share repo with: `0xtaozi` and `0xmihutao`

## Troubleshooting

### ComfyUI Connection Issues

**Problem**: Backend can't connect to ComfyUI
**Solution**:
- Check RunPod firewall settings
- Verify port 8188 is exposed
- Use correct public URL, not localhost

### Out of Memory Errors

**Problem**: CUDA OOM during generation
**Solution**:
- Reduce resolution (1024 → 768)
- Use `--lowvram` flag
- Generate one image at a time

### Identity Drift

**Problem**: Face doesn't look consistent
**Solution**:
- Increase InstantID strength (0.85 → 0.95)
- Use higher quality reference image
- Enable face restoration post-processing

### Slow Generation

**Problem**: Images take too long
**Solution**:
- Reduce steps (30 → 25)
- Use faster sampler
- Keep models loaded in VRAM

## Cost Tracking

Track your RunPod usage:
- Development: ~20 hours @ $0.69 = ~$14
- Generation: ~2 hours @ $0.69 = ~$1.40
- Total: ~$15-20

**Stay under $45 budget!**

Remember to **STOP your RunPod instance** when not using it to save credits.

## Need Help?

- ComfyUI Discord: https://discord.gg/comfyui
- InstantID GitHub: https://github.com/InstantID/InstantID
- RunPod Documentation: https://docs.runpod.io

Good luck with your assessment! 🚀
