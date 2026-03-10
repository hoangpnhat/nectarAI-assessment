# RunPod Deployment Guide (For Reviewers)

**Fastest way to test this assessment** - Setup time: ~10 minutes

This guide helps reviewers quickly deploy and test the assessment without local GPU setup.

## 🚀 Quick Start (Reviewer Path)

### Step 1: Create RunPod Instance

1. Go to [RunPod.io](https://runpod.io)
2. Click **"Deploy"** → **"GPU Pods"**
3. Select GPU:
   - **Recommended:** RTX 4090 (~$0.69/hr)
   - **Budget:** RTX 3090 (~$0.39/hr)
   - **Fast:** A100 (~$1.89/hr)
4. Template: **RunPod Pytorch 2.0** or **Ubuntu + CUDA**
5. Storage: **50GB+**
6. Click **"Deploy On-Demand"**

### Step 2: SSH into Pod

```bash
# Get SSH command from RunPod dashboard
ssh root@<pod-ip> -p <port>
```

### Step 3: Install ComfyUI on Pod

```bash
# Update system
apt update && apt install -y git wget

# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI

# Install dependencies
pip install -r requirements.txt xformers

# Install custom nodes
cd custom_nodes
git clone https://github.com/cubiq/ComfyUI_InstantID
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack

cd ComfyUI-Impact-Pack
pip install -r requirements.txt
python install.py

cd ../../
```

### Step 4: Download Models (Critical)

**Option A: Quick download script (recommended)**

```bash
# Run this in ComfyUI directory
bash <<'SCRIPT'

# Create model directories
mkdir -p models/checkpoints models/instantid models/controlnet models/loras
mkdir -p models/ultralytics/bbox models/ultralytics/segm

# Base checkpoint
cd models/checkpoints
wget https://huggingface.co/frankjoshua/realisticVisionV60B1_v51VAE/resolve/main/realisticVisionV60B1_v51VAE.safetensors

# InstantID
cd ../instantid
wget https://huggingface.co/InstantX/InstantID/resolve/main/ip-adapter.bin

# ControlNet
cd ../controlnet
wget https://huggingface.co/InstantX/InstantID/resolve/main/ControlNetModel/diffusion_pytorch_model.safetensors

# Face detection
cd ../ultralytics/bbox
wget https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8n.pt

cd ../segm
wget https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8n_v2.pt

echo "✓ Models downloaded!"
cd ../../../
SCRIPT
```

**Option B: Manual download**
See `workflows/LORA_GUIDE.md` for direct links.

### Step 5: Clone Assessment Repo

```bash
cd ~
git clone <assessment-repo-url>
cd nectarAI-assessment
```

### Step 6: Upload Reference Images

```bash
# Copy reference images to ComfyUI input
cp reference_images/*.jpg ../ComfyUI/input/

# Or upload via SCP from local machine
scp reference_images/*.jpg root@<pod-ip>:~/ComfyUI/input/
```

### Step 7: Setup Backend

```bash
cd ~/nectarAI-assessment/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

**Update `.env` with pod's ComfyUI URL:**
```bash
COMFYUI_URL=http://localhost:8188  # If running on same pod
```

### Step 8: Start Services

**Terminal 1 - ComfyUI:**
```bash
cd ~/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

**Terminal 2 - Backend:**
```bash
cd ~/nectarAI-assessment/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 9: Test via Port Forwarding

**From your local machine:**

```bash
# Forward ComfyUI port
ssh -L 8188:localhost:8188 root@<pod-ip> -p <port>

# Forward Backend port (in another terminal)
ssh -L 8000:localhost:8000 root@<pod-ip> -p <port>
```

**Then access:**
- Backend: http://localhost:8000/health
- ComfyUI: http://localhost:8188

### Step 10: Run Tests

```bash
# On the pod or via port forwarding
cd ~/nectarAI-assessment/backend/tests
python test_api.py
```

## 🎨 Generate Sample Images

```bash
cd ~/nectarAI-assessment/backend/scripts

# Generate all samples
python run_samples.py

# Or specific sets
python generate_male.py
python generate_direct.py
```

## 🖥️ Access Frontend

**Option 1: Port Forward + Run Locally**
```bash
# Forward backend port
ssh -L 8000:localhost:8000 root@<pod-ip>

# On local machine
cd frontend
streamlit run streamlit_app.py
```

**Option 2: Run on Pod + Expose Streamlit**
```bash
# On pod
cd ~/nectarAI-assessment/frontend
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0

# Access via RunPod's exposed ports
# (Configure in RunPod dashboard)
```

## 💰 Cost Estimate

**Using RTX 4090 @ $0.69/hr:**
- Setup (first time): 15-20 mins = ~$0.25
- Testing: 10 mins = ~$0.12
- Sample generation: 10 mins = ~$0.12
- **Total per review session:** < $0.50

## 🎯 Verification Checklist

After setup, verify:

- [ ] ComfyUI GUI accessible at http://localhost:8188
- [ ] Can load `workflow_api.json` in ComfyUI
- [ ] All nodes show green (no red/missing nodes)
- [ ] Backend health check returns `{"api": "ok", "comfyui": "ok"}`
- [ ] Can set reference image
- [ ] Chat generates SFW images
- [ ] Sample images show consistent face across scenes

## 🐛 Common Issues

### "Node not found" in ComfyUI
**Solution:** Install missing custom nodes:
```bash
cd ComfyUI/custom_nodes
git clone <missing-node-repo>
```

### "Model not found"
**Solution:** Check model paths match workflow expectations. See `workflows/LORA_GUIDE.md`.

### "CUDA out of memory"
**Solution:** Use larger GPU or reduce resolution:
```bash
# In backend/.env
DEFAULT_WIDTH=768
DEFAULT_HEIGHT=768
```

### Backend can't connect to ComfyUI
**Solution:** Check ComfyUI is running and URL is correct:
```bash
curl http://localhost:8188/system_stats
```

## 📝 Notes for Reviewers

1. **Models take time to download** - First setup takes 20-30 mins
2. **Keep pod running** during review session, pause when done
3. **Sample images included** in repo - can verify consistency without generating
4. **Workflow JSON included** - can inspect nodes without running
5. **RunPod cost** - Should be < $2 for full review

## 🔗 Alternative: Review Without Running

If you prefer to review without full setup:

1. **Code Review:** All code is in `backend/` and `frontend/`
2. **Workflow Review:** Open `workflows/workflow_api.json` in text editor or ComfyUI
3. **Sample Images:** Pre-generated in `outputs/samples/`
4. **Documentation:** README.md explains technical approach

The samples demonstrate character consistency without needing to run the system.

## 📞 Support

For setup issues during review:
- Check INSTALLATION.md for detailed steps
- See workflows/LORA_GUIDE.md for model links
- Backend logs: `backend/backend.log`
- ComfyUI logs: terminal output
