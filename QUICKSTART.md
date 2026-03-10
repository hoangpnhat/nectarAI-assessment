# Quick Start Guide

**Time to complete**: 4-8 hours for basic setup + testing

## 🚀 Fastest Path to Working Demo

### Step 1: Setup RunPod (1 hour)

```bash
1. Create RunPod account → Add $45 credits
2. Deploy RTX 4090 pod with Pytorch template
3. SSH into pod
4. Run setup script (see below)
```

**Quick Setup Script** (paste into RunPod terminal):
```bash
#!/bin/bash
cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt xformers

# Install InstantID
cd custom_nodes
git clone https://github.com/cubiq/ComfyUI_InstantID.git
cd ComfyUI_InstantID && pip install -r requirements.txt && cd ..
cd ..

# Download models
mkdir -p models/instantid models/insightface/models
cd models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
cd ../instantid
wget https://huggingface.co/InstantX/InstantID/resolve/main/ip-adapter.bin
wget https://huggingface.co/InstantX/InstantID/resolve/main/ControlNetModel/diffusion_pytorch_model.safetensors -O controlnet.safetensors
cd ../insightface/models
wget https://huggingface.co/MonsterMMORPG/tools/resolve/main/antelopev2.zip && unzip antelopev2.zip
cd /workspace/ComfyUI

# Start ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

### Step 2: Load ComfyUI Workflow (5 minutes) ✅

**GOOD NEWS**: Workflow đã sẵn sàng!

1. Access ComfyUI at your RunPod URL
2. Download [`workflows/workflow_api.json`](workflows/workflow_api.json)
3. In ComfyUI: Click **Load** → Select `workflow_api.json`
4. Upload reference image to Node 1 (LoadImage)
5. Click **Queue Prompt** to test
6. Done! ✅

**What's included**:
- ✅ Pony Diffusion XL v6 (best for NSFW)
- ✅ SDXL VAE (separate, better quality)
- ✅ InstantID (ip_weight: 0.75, cn_strength: 0.5)
- ✅ Optimized settings (steps: 30, cfg: 7.0)
- ✅ Score prompts for Pony
- ✅ 1.5x upscaling

### Step 3: Setup Local Environment (30 min)

```bash
# Clone this repo (or your fork)
git clone https://github.com/yourusername/nectar.git
cd nectar

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Add your ANTHROPIC_API_KEY and COMFYUI_URL

# Frontend
cd ../frontend
npm install
cp .env.local.example .env.local
```

### Step 4: Run Application (5 min)

**Terminal 1** (Backend):
```bash
cd backend
source venv/bin/activate
python app/main.py
```

**Terminal 2** (Frontend):
```bash
cd frontend
npm run dev
```

Open http://localhost:3000

### Step 5: Generate Samples (2-4 hours)

1. Upload 2 reference faces (1 male, 1 female)
2. Generate 5+ scenes per character:
   - Coffee shop
   - Beach
   - Gym
   - Bedroom
   - Outdoor
3. Generate 2-3 NSFW examples per character
4. Save all to `generated_images/`

### Step 6: Record Demo & Document (1 hour)

1. Record 3-5 minute demo video showing:
   - Setup process
   - Natural conversation triggering images
   - Consistency comparison
2. Update README with your technical decisions
3. Create comparison grids

### Step 7: Submit

```bash
git add .
git commit -m "Complete Nectar AI assessment"
git push origin main
# Share repo with 0xtaozi and 0xmihutao
```

## 📋 Minimal Checklist

- [ ] RunPod setup complete (ComfyUI running)
- [ ] Workflow built and tested
- [ ] Local app running (backend + frontend)
- [ ] 5+ images per character (male + female)
- [ ] 2-3 NSFW examples per character
- [ ] Demo video recorded
- [ ] README updated with technical justifications
- [ ] GitHub repo shared

## 🔥 Pro Tips

1. **Save Time**: Workflow đã ready - chỉ cần load và test!
2. **Face Consistency**: Current settings (ip_weight: 0.75) đã optimized
3. **NSFW Quality**: Pony XL v6 + 30-35 steps = excellent anatomy
4. **Generation Speed**: Keep models in VRAM, don't reload
5. **Cost**: Stop RunPod when not using (~$15-20 total expected)
6. **VAE Quality**: Using separate SDXL VAE for better colors

## 🆘 Quick Troubleshooting

**Weird colors/artifacts**: Make sure sdxl_vae.safetensors is loaded (Node 21)
**Face not consistent**: Increase ip_weight from 0.75 to 0.80-0.85
**Abstract/noise output**: Check VAE file exists, try lowering cfg to 6.5
**Out of memory**: Reduce resolution to 768x768
**Slow generation**: Already optimized at 30 steps
**Model not found**: Check Pony XL filename is exact: `ponyDiffusionV6XL_v6StartWithThisOne.safetensors`

See [`workflows/TROUBLESHOOTING.md`](workflows/TROUBLESHOOTING.md) for detailed fixes!

## 📚 Full Documentation

- [Complete Setup Guide](docs/SETUP_GUIDE.md)
- [Testing Prompts](docs/TESTING_PROMPTS.md)
- [Workflow Template](workflows/workflow_template_notes.md)
- [Technical README](README.md)

## ⏱️ Time Breakdown

- RunPod + ComfyUI setup: 1-2 hours
- Workflow building: 1 hour
- Local setup: 30 min
- Sample generation: 2-4 hours
- Demo + docs: 1 hour
- **Total: 6-9 hours**

Start now and you can complete this in 1-2 focused work sessions! 🚀
