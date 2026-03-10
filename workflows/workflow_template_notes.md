# ComfyUI Workflow Template Notes

## Workflow Structure for Character Consistency

Since ComfyUI workflows are created visually and exported as JSON with specific node IDs, here's the logical structure you should build:

### Required Nodes

#### 1. Input Nodes

```
LoadImage (Node ID: 1)
- Purpose: Load reference face image
- Inputs: image file path
- Outputs: IMAGE

CLIPTextEncode (Node ID: 6) - Positive Prompt
- Purpose: Encode positive text prompt
- Inputs: text (prompt), clip
- Outputs: CONDITIONING

CLIPTextEncode (Node ID: 7) - Negative Prompt
- Purpose: Encode negative prompt
- Inputs: text (negative prompt), clip
- Outputs: CONDITIONING
```

#### 2. Model Loading

```
CheckpointLoaderSimple (Node ID: 4)
- Purpose: Load SDXL base model
- Inputs: ckpt_name (model file)
- Outputs: MODEL, CLIP, VAE

InstantIDModelLoader (Node ID: 10)
- Purpose: Load InstantID IP-Adapter
- Inputs: instantid_file
- Outputs: INSTANTID_MODEL

InstantIDFaceAnalysis (Node ID: 11)
- Purpose: Load InsightFace model
- Inputs: provider (CPU/CUDA)
- Outputs: FACEANALYSIS

ControlNetLoader (Node ID: 16)
- Purpose: Load InstantID ControlNet
- Inputs: control_net_name (controlnet.safetensors)
- Outputs: CONTROL_NET
```

#### 3. Face Processing

```
ApplyInstantID (Node ID: 12)
- Purpose: Extract face embedding AND apply InstantID to model in one step
- Inputs:
  - instantid (from node 10)
  - insightface (from node 11)
  - control_net (from node 16)
  - image (reference face image, from node 1)
  - model (from node 4)
  - positive (from node 6)
  - negative (from node 7)
  - ip_weight: 0.85
  - cn_strength: 0.6
  - start_at: 0.0
  - end_at: 1.0
- Outputs: MODEL (modified), positive (modified), negative (modified)
```

> ⚠️ **Note**: There is NO separate `InstantIDFaceEmbedding` node in `ComfyUI_InstantID`.
> Face embedding extraction is handled internally by `ApplyInstantID` using the
> `InsightFace` model passed via the `insightface` input.
> You also need a `ControlNetLoader` node pointing to `controlnet.safetensors`.

#### 4. Image Generation

```
KSampler (Node ID: 3)
- Purpose: Main diffusion sampling
- Inputs:
  - model (from node 12)
  - positive (from node 12)
  - negative (from node 12)
  - latent_image (from node 5)
  - seed: random
  - steps: 30
  - cfg: 7.5
  - sampler_name: "dpmpp_2m_karras"
  - scheduler: "karras"
  - denoise: 1.0
- Outputs: LATENT

EmptyLatentImage (Node ID: 5)
- Purpose: Create empty latent space
- Inputs:
  - width: 1024
  - height: 1024
  - batch_size: 1
- Outputs: LATENT
```

#### 5. Decoding & Output

```
VAEDecode (Node ID: 8)
- Purpose: Decode latent to image
- Inputs:
  - samples (from node 3)
  - vae (from node 4)
- Outputs: IMAGE

SaveImage (Node ID: 9)
- Purpose: Save final image
- Inputs:
  - images (from node 8)
  - filename_prefix: "nectar_output"
- Outputs: (saves to disk)
```

#### 6. Optional Enhancement

```
ADetailerNode (Node ID: 14) [Optional]
- Purpose: Enhance face details
- Inputs:
  - image (from node 8)
  - adetailer_model: "face_yolov8n.pt"
  - confidence_threshold: 0.3
  - denoising_strength: 0.4
- Outputs: IMAGE (enhanced)

FaceRestoreNode (Node ID: 15) [Optional]
- Purpose: Additional face restoration
- Inputs:
  - image (from node 14 or 8)
  - model: "CodeFormer"
  - fidelity: 0.7
- Outputs: IMAGE
```

## Building in ComfyUI

1. **Open ComfyUI** web interface (http://localhost:8188)

2. **Add nodes** using right-click menu or node browser:
   - Search for "InstantID" nodes
   - Add checkpoint loader, samplers, VAE nodes
   - Connect nodes as described above

3. **Configure parameters**:
   - Set IP-Adapter scale to 0.85 for strong identity
   - Use DPM++ 2M Karras sampler
   - 30 steps, CFG 7.5

4. **Test with reference image**:
   - Load a test face image
   - Generate with different prompts
   - Verify consistency

5. **Export workflow**:
   - Click "Save" button
   - Choose "Save (API Format)" → `workflow_api.json`
   - Also save regular format → `workflow.json`

## API Format vs. Regular Format

**API Format (`workflow_api.json`)**:
- Used by backend to programmatically generate images
- Contains only node definitions and connections
- Parameters can be modified via code

**Regular Format (`workflow.json`)**:
- Used to load workflow back into ComfyUI
- Contains UI state and metadata
- Easier to edit visually

## Dynamic Parameter Injection

In your backend code (`image_generation.py`), you'll modify workflow parameters:

```python
workflow = load_workflow("workflow_api.json")

# Update prompts
workflow["6"]["inputs"]["text"] = prompt  # Positive
workflow["7"]["inputs"]["text"] = negative_prompt  # Negative

# Update generation settings
workflow["3"]["inputs"]["steps"] = settings["steps"]
workflow["3"]["inputs"]["cfg"] = settings["cfg_scale"]
workflow["3"]["inputs"]["seed"] = random.randint(0, 2**32)

# Update InstantID strength
workflow["12"]["inputs"]["ip_weight"] = settings["instantid_strength"]

# Update resolution
workflow["5"]["inputs"]["width"] = settings["width"]
workflow["5"]["inputs"]["height"] = settings["height"]

# Send to ComfyUI
response = requests.post(f"{comfyui_url}/prompt", json={"prompt": workflow})
```

## Alternative: Diffusers Implementation

If you prefer not to use ComfyUI, you can implement directly with Diffusers:

```python
from diffusers import StableDiffusionXLPipeline
from insightface.app import FaceAnalysis
import torch

# Load InstantID components
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
)
pipe.to("cuda")

# Load InstantID adapter
# Note: This requires InstantID integration with Diffusers
# See: https://github.com/InstantID/InstantID

face_app = FaceAnalysis(name='antelopev2')
face_app.prepare(ctx_id=0, det_size=(640, 640))

# Extract face embedding
ref_image = load_image("reference.jpg")
faces = face_app.get(cv2.cvtColor(np.array(ref_image), cv2.COLOR_RGB2BGR))
face_emb = torch.from_numpy(faces[0].normed_embedding).unsqueeze(0)

# Generate with identity
image = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    ip_adapter_image_embeds=[face_emb],
    num_inference_steps=30,
    guidance_scale=7.5,
).images[0]
```

## Testing Checklist

- [ ] Load workflow in ComfyUI
- [ ] Test with male reference image
- [ ] Test with female reference image
- [ ] Generate 3-5 different scenes with same identity
- [ ] Verify facial consistency across images
- [ ] Test NSFW generation (2-3 examples)
- [ ] Check anatomical correctness
- [ ] Measure generation time
- [ ] Export workflow in both formats
- [ ] Test API integration with backend

## Recommended Node Versions

Keep track of which versions work best:

```
ComfyUI: Latest stable
InstantID nodes: v1.2+
InsightFace models: antelopev2
Base model: Pony Diffusion XL v6 OR SDXL 1.0
```

## Next Steps

1. Set up RunPod instance with GPU
2. Install ComfyUI and all required nodes
3. Download models (will take some time - SDXL is ~6GB)
4. Build and test workflow
5. Export and integrate with backend
6. Generate sample images for submission
