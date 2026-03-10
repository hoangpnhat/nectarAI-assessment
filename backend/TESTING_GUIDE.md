# Backend Testing Guide

Quick guide to test the backend API locally.

## Prerequisites

1. **ComfyUI must be running**:
```bash
cd /home/Admin1234567/hoangpn/nectarAI-assessment/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

2. **Backend dependencies installed**:
```bash
cd /home/Admin1234567/hoangpn/nectarAI-assessment/backend
pip install -r requirements.txt
```

3. **Environment variables configured**:
```bash
# Edit .env file
nano .env

# Make sure you have:
OPENAI_API_KEY=sk-your-actual-key-here
```

## Step-by-Step Testing

### 1. Start Backend

```bash
cd /home/Admin1234567/hoangpn/nectarAI-assessment/backend
python app.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. Run Quick API Test

In a new terminal:

```bash
cd /home/Admin1234567/hoangpn/nectarAI-assessment/backend
python test_api.py
```

This will test:
- ✓ Health check
- ✓ Set reference image
- ✓ Simple chat (no image)
- ✓ Chat with image generation

**Expected duration**: 1-2 minutes

### 3. Generate Sample Images

```bash
cd /home/Admin1234567/hoangpn/nectarAI-assessment/backend
python generate_samples.py
```

This will create:
- 2 SFW scenes
- 3 NSFW scenes

**Expected duration**: 5-10 minutes

### 4. Manual Testing with cURL

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Set Reference
```bash
curl -X POST http://localhost:8000/set-reference \
  -H "Content-Type: application/json" \
  -d '{"image_path": "Copy of 9.jpg", "gender": "woman"}'
```

#### Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi! How are you?"}' | jq '.'
```

#### Direct Image Generation
```bash
curl -X POST http://localhost:8000/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "positive_prompt": "a photo of a woman in a cafe, natural lighting",
    "negative_prompt": "anime, cartoon, blurry",
    "steps": 30,
    "cfg_scale": 4.5
  }' --output test.png
```

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Fix**:
```bash
pip install -r requirements.txt
```

### ComfyUI connection error

**Error**: `comfyui: "error"` in health check

**Fix**:
1. Check ComfyUI is running: `curl http://127.0.0.1:8188/system_stats`
2. If not, start it: `cd ComfyUI && python main.py`

### OpenAI API error

**Error**: `AuthenticationError` or `Invalid API key`

**Fix**:
1. Check .env file: `cat .env | grep OPENAI_API_KEY`
2. Get valid key from: https://platform.openai.com/api-keys
3. Update .env: `nano .env`

### Workflow not found

**Error**: `FileNotFoundError: workflow_api.json`

**Fix**:
```bash
cp ComfyUI/user/default/workflows/nectarAI.json workflows/workflow_api.json
```

### Image generation timeout

**Error**: Request timed out after 120s

**Causes**:
- ComfyUI stuck on a node
- GPU out of memory
- Missing models

**Fix**:
1. Check ComfyUI logs
2. Reload ComfyUI
3. Check VRAM usage: `nvidia-smi`

## Expected Results

### test_api.py output:
```
==================================================
1. Testing Health Check
==================================================
✓ API Status: ok
✓ ComfyUI Status: ok
✓ Reference Image Set: False

==================================================
2. Setting Reference Image
==================================================
✓ Status: ok
✓ Reference: Copy of 9.jpg
✓ Gender: woman

==================================================
3. Testing Simple Chat (No Image)
==================================================
Character: Hi there! I'm doing great, thanks for asking! How are you?
Image generated: False

==================================================
4. Testing Chat with Image Generation
==================================================
This will take 30-60 seconds...

Character: I'm wearing a comfortable summer dress today. Let me show you!
Image generated: True
✓ Image saved to: ../outputs/test_chat_image.png

==================================================
TEST SUMMARY
==================================================
✓ PASS - Health Check
✓ PASS - Set Reference
✓ PASS - Simple Chat
✓ PASS - Chat with Image

Passed: 4/4

🎉 All tests passed!
```

### generate_samples.py output:
```
============================================================
[1/5] Generating: female_cafe_sfw
Description: SFW - Woman in cafe
============================================================
→ Setting reference image...
→ Resetting conversation...
→ Sending message: "Where are you right now? I'm curious about y..."
→ Generating image (this may take 30-90 seconds)...

📝 Character response:
   I'm at my favorite cozy cafe downtown! It's such a nice spot with warm lighting and great coffee...

✓ SUCCESS: Image saved to ../outputs/samples/female_cafe_sfw.png
```

## Next Steps

After successful testing:

1. ✓ Review generated images in `outputs/samples/`
2. ✓ Commit workflow and backend code
3. ✓ Prepare for frontend (Streamlit)
4. ✓ Deploy to RunPod for production testing

## Files Created

- `backend/test_api.py` - Quick API test suite
- `backend/generate_samples.py` - Sample image generator
- `outputs/test_chat_image.png` - Test output
- `outputs/samples/*.png` - Sample images for assessment
