# Demo Video Recording Guide

Complete guide for recording the assessment demo video.

## 📹 What to Record

**Duration:** 3-5 minutes

**Content to demonstrate:**
1. System setup and health check
2. Setting reference image
3. Natural conversation with SFW image generation
4. NSFW request with image generation
5. Identity consistency verification (compare faces)
6. Male character example (bonus)

## 🎬 Recording Script

### Scene 1: Introduction (30 seconds)
```
Show:
- Project structure in IDE
- Terminal windows (ComfyUI, Backend, Frontend)
- System health check: curl http://localhost:8000/health

Say:
"This is my Nectar AI assessment submission. I've built a multi-modal
chat system with character-consistent image generation using InstantID
and ComfyUI. Let me show you how it works."
```

### Scene 2: Setup (30 seconds)
```
Show:
- Open Streamlit UI (http://localhost:8501)
- Sidebar: Select "Copy of 9.jpg" reference
- Click "Set Reference"
- Show confirmation

Say:
"First, I set the reference image. The system uses InstantID to extract
facial embeddings and maintain identity across all generations."
```

### Scene 3: SFW Chat (60 seconds)
```
Show:
- Type: "Hi! What are you wearing today?"
- Character responds naturally
- Type: "Where are you right now? Can I see a photo?"
- Show character response with [SEND_PHOTO] intent
- Wait for image generation (30-40 seconds)
- Image appears in chat

Say:
"The LLM detects when to send photos based on conversation context.
Notice how the character responds naturally, then automatically generates
an image matching the conversation."
```

### Scene 4: Context Awareness (30 seconds)
```
Show:
- Generated image in UI
- Point out details: location matches chat (cafe/park),
  clothing matches description

Say:
"The prompt engineering system extracts scene context from the conversation
and creates a detailed diffusion prompt. The location, clothing, and mood
all match what we discussed."
```

### Scene 5: NSFW Generation (60 seconds)
```
Show:
- Reset conversation (sidebar button)
- Type: "What are you wearing in your bedroom? Show me."
- Character responds
- Wait for image generation
- NSFW image appears

Say:
"The system handles NSFW requests by detecting keywords and enhancing
the prompt after GPT extraction. Notice the FaceDetailer and HandDetailer
in action - no mushy anatomy, correct hand count, realistic details."
```

### Scene 6: Identity Consistency (30 seconds)
```
Show:
- Open outputs/samples folder
- Display 5 female samples side-by-side
- Zoom in on faces

Say:
"Here are 5 different scenes generated with the same reference.
Notice the consistent facial structure, eye color, and signature features.
This is InstantID maintaining the visual DNA across diverse contexts."
```

### Scene 7: Male Character (30 seconds - Optional)
```
Show:
- Change reference to male
- Generate one male sample
- Show male_gym_sfw.png result

Say:
"The system works with both male and female references. Same identity
preservation, same quality pipeline."
```

### Scene 8: Technical Overview (30 seconds)
```
Show:
- ComfyUI workflow (open workflow_api.json or show in ComfyUI UI)
- Point out key nodes:
  * InstantID
  * FaceDetailer
  * HandDetailer
  * UltimateSDUpscale
  * LoRA

Say:
"The workflow uses a multi-stage pipeline: InstantID for identity,
FaceDetailer and HandDetailer for anatomical correctness, and
UltimateSDUpscale for quality. This solves the key challenges in
NSFW character generation."
```

### Scene 9: Closing (20 seconds)
```
Show:
- README.md in IDE
- Scroll through technical decisions section

Say:
"All code, documentation, and samples are in the GitHub repo.
The README explains my approach to identity preservation and
technical choices. Thank you for reviewing my submission!"
```

## 🛠️ Recording Setup

### Tools:
- **Screen recorder**: OBS Studio, SimpleScreenRecorder, or built-in
- **Resolution**: 1920x1080 (1080p minimum)
- **Frame rate**: 30fps
- **Audio**: Optional but recommended for explanation

### Terminal Setup:
```bash
# Terminal 1: ComfyUI (should be running)
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188

# Terminal 2: Backend (should be running)
cd backend
python app.py

# Terminal 3: Frontend (start before recording)
cd frontend
streamlit run streamlit_app.py
```

### Before Recording:
1. ✅ Clean desktop (close unnecessary windows)
2. ✅ Zoom text size for readability
3. ✅ Test one generation to ensure everything works
4. ✅ Have samples pre-generated (don't wait 5 minutes during recording)
5. ✅ Prepare script/talking points

## 📝 Recording Checklist

- [ ] Introduction showing project structure
- [ ] System health check demonstration
- [ ] Reference image setup in UI
- [ ] SFW chat conversation → image generation
- [ ] NSFW chat conversation → image generation
- [ ] Identity consistency verification (compare faces)
- [ ] Male character example (optional but recommended)
- [ ] Workflow explanation in ComfyUI
- [ ] Technical decisions in README

## 🎯 Key Points to Emphasize

1. **Identity Consistency**: Same face across all scenes
2. **Zero-shot**: Works with any reference, no training
3. **Anatomical Correctness**: FaceDetailer + HandDetailer = no artifacts
4. **Context Awareness**: Images match conversation
5. **NSFW Quality**: Realistic, not mushy or deformed
6. **Technical Stack**: InstantID + SD1.5 + Enhancement pipeline

## 💡 Tips

- **Keep it concise**: Don't explain every detail
- **Show, don't tell**: Let the results speak
- **Highlight key tech**: InstantID, FaceDetailer, enhancement pipeline
- **Compare faces**: Side-by-side comparison shows consistency best
- **Test recording**: Do a 30-second test first

## 📤 After Recording

1. Export video as MP4 (H.264 codec)
2. Name: `nectar_ai_demo.mp4` or similar
3. Add to repository root
4. Update README.md with video link
5. Commit and push to GitHub

## 🔗 Alternative: Loom/YouTube

If video file is too large for GitHub:
- Upload to Loom/YouTube (unlisted)
- Add link to README.md
- Include in submission message

---

**Ready to record when you are!** 🎥
