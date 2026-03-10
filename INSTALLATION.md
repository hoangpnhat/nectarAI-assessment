# Installation Guide for Reviewers

This guide explains how to set up and run the Nectar AI assessment project.

## 📦 What's Included in the Repo

✅ **Included:**
- Backend code (`backend/`)
- Frontend code (`frontend/`)
- Workflow JSON (`workflows/workflow_api.json`)
- Sample images (`outputs/samples/`)
- Documentation (README, guides)

❌ **NOT Included (too large for Git):**
- ComfyUI installation (~10-50GB)
- AI Models (~20-30GB total)
- Custom nodes dependencies

## 🚀 Complete Setup Instructions

### Step 1: Clone This Repository

```bash
git clone <your-repo-url>
cd nectarAI-assessment
```

### Step 2: Install ComfyUI

**Why not included?** ComfyUI with models is 30-50GB. Git repositories should stay lean.

**Installation:**

```bash
# Inside nectarAI-assessment/ directory
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI

# Install Python dependencies
pip install -r requirements.txt

# Install custom nodes
cd custom_nodes

# InstantID (required for character consistency)
git clone https://github.com/cubiq/ComfyUI_InstantID

# Impact Pack (required for FaceDetailer/HandDetailer)
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack
cd ComfyUI-Impact-Pack
pip install -r requirements.txt
python install.py

cd ../..
```

**Result directory structure:**
```
nectarAI-assessment/
├── ComfyUI/              ← Installed here
│   ├── models/           ← Models go here
│   ├── input/            ← Reference images
│   ├── custom_nodes/
│   └── ...
├── backend/
├── frontend/
└── workflows/
```

### Step 3: Download Required Models

**Critical models for this workflow:**

#### 3.1 Base Checkpoint (Stable Diffusion 1.5)
```bash
cd ComfyUI/models/checkpoints/

# Download realisticVisionV60B1_v51VAE.safetensors
wget https://huggingface.co/frankjoshua/realisticVisionV60B1_v51VAE/resolve/main/realisticVisionV60B1_v51VAE.safetensors
```

#### 3.2 InstantID Models
```bash
cd ../instantid/

# IP-Adapter
wget https://huggingface.co/InstantX/InstantID/resolve/main/ip-adapter.bin

# ControlNet
mkdir -p ../controlnet/
cd ../controlnet/
wget https://huggingface.co/InstantX/InstantID/resolve/main/ControlNetModel/diffusion_pytorch_model.safetensors
```

#### 3.3 Face Detection Models (Impact Pack)
```bash
cd ../ultralytics/bbox/
wget https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8n.pt

cd ../segm/
wget https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8n_v2.pt
```

#### 3.4 NSFW LoRA (Optional but recommended)
```bash
cd ../../loras/
# Download from CivitAI or your preferred source
# Place more_details.safetensors here
```

**See `workflows/LORA_GUIDE.md` for detailed download links.**

### Step 4: Add Reference Images

```bash
# Copy reference images to ComfyUI input
cp reference_images/*.jpg ComfyUI/input/

# Or use the samples provided
# Reference images should be in ComfyUI/input/
```

### Step 5: Setup Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
nano .env  # or vim, code, etc.
```

### Step 6: Setup Frontend (Optional)

```bash
cd ../frontend

# Install dependencies
pip install -r requirements.txt
```

### Step 7: Start Services

**Terminal 1 - ComfyUI:**
```bash
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

Wait until you see: `To see the GUI go to: http://127.0.0.1:8188`

**Terminal 2 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend (optional):**
```bash
cd frontend
streamlit run streamlit_app.py
```

### Step 8: Verify Installation

**Test ComfyUI:**
```bash
curl http://localhost:8188/system_stats
```

**Test Backend:**
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "api": "ok",
  "comfyui": "ok",
  "reference_image_set": false
}
```

**Test Frontend:**
Open http://localhost:8501 in browser

## 🧪 Running Tests

```bash
cd backend/tests
python test_api.py
```

## 🎨 Generating Sample Images

```bash
cd backend/scripts

# Generate all samples (5 female + 3 male)
python generate_samples.py

# Or generate male samples separately
python generate_male.py
```

## 🚨 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'ComfyUI'"
**Solution:** ComfyUI should be installed at project root, not inside backend/

### Issue: "Model not found"
**Solution:** Check that models are in correct directories:
- `ComfyUI/models/checkpoints/`
- `ComfyUI/models/instantid/`
- `ComfyUI/models/controlnet/`
- etc.

### Issue: "Port already in use"
**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8188
lsof -ti:8188 | xargs kill -9
```

### Issue: "CUDA out of memory"
**Solution:** Reduce image resolution in `.env`:
```
DEFAULT_WIDTH=768
DEFAULT_HEIGHT=768
```

## 📊 System Requirements

- **GPU:** 8GB+ VRAM (RTX 3080, 4080, A4000, H100, etc.)
- **RAM:** 16GB+ recommended
- **Storage:** 60GB+ free space
- **OS:** Linux (tested on Ubuntu 20.04+), Windows 10/11, macOS

## 🎯 Quick Start (After Installation)

1. Start ComfyUI: `cd ComfyUI && python main.py`
2. Start Backend: `cd backend && uvicorn app.main:app --reload`
3. Open Frontend: `cd frontend && streamlit run streamlit_app.py`
4. Chat and generate images!

## 📞 Support

If you encounter issues:
1. Check `workflows/LORA_GUIDE.md` for model download instructions
2. Verify all models are in correct directories
3. Check ComfyUI logs for errors
4. Ensure OPENAI_API_KEY is valid in `.env`

## 🚢 Alternative: RunPod Deployment

If local setup is difficult, you can use RunPod:

1. Create RunPod pod with RTX 4090
2. Install ComfyUI as above
3. Update `COMFYUI_URL` in backend `.env`:
   ```
   COMFYUI_URL=http://your-pod-id.runpod.io:8188
   ```
4. Run backend locally or on RunPod

See README.md for detailed RunPod instructions.
