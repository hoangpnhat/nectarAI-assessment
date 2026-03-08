# Testing Prompts & Sample Generation Guide

## Character References

For testing, you'll need:
- 1-2 male reference face images (clear, front-facing, good lighting)
- 1-2 female reference face images (clear, front-facing, good lighting)

**Where to get reference images:**
- Free stock photos: Unsplash, Pexels (search "portrait")
- AI-generated faces: thispersondoesnotexist.com
- Use photos with good lighting and clear facial features

## Test Conversation Flows

### Flow 1: Natural Image Triggers

```
User: Hey! How's it going?
AI: Hey! I'm doing great, just relaxing. How about you?

User: What are you up to right now?
AI: [Should generate image] I'm just chilling at home in my living room...
[IMAGE: living room, casual home wear, relaxed pose]

User: What are you wearing?
AI: [Should generate image] I've got on a cozy sweater and jeans...
[IMAGE: sweater and jeans, indoor setting, casual style]

User: You look great! Can you send me another photo?
AI: [Should generate image] Sure! Here's one from earlier today...
[IMAGE: different scene, same character identity]
```

### Flow 2: Location-Based

```
User: Where are you right now?
AI: [Should generate image] I'm at my favorite coffee shop downtown...
[IMAGE: coffee shop, sitting, casual outfit, natural lighting]

User: Nice! Do you go there often?
AI: Yeah, I love it here. Great atmosphere!

User: Show me what it looks like
AI: [Should generate image] Here's the view from my seat...
[IMAGE: coffee shop, different angle or activity]
```

### Flow 3: Activity-Based

```
User: What did you do today?
AI: I went to the gym this morning, then grabbed lunch

User: How was the gym?
AI: [Should generate image] It was intense! Here's me after my workout...
[IMAGE: gym setting, athletic wear, post-workout]

User: Looking fit! What about now?
AI: [Should generate image] Now I'm just relaxing at home...
[IMAGE: home setting, relaxed clothes]
```

### Flow 4: NSFW Progression (Natural)

```
User: You look really good in that outfit
AI: Thanks! I appreciate the compliment

User: Do you have anything more... revealing?
AI: [Should detect NSFW intent] Well, I do have some more intimate photos...

User: I'd love to see them
AI: [Should generate NSFW image] Here's something just for you...
[IMAGE: bedroom, lingerie/intimate wear, sultry pose, soft lighting]

User: That's beautiful. Can I see more?
AI: [Should generate NSFW image] Of course... here's another one
[IMAGE: more explicit, bedroom setting, proper anatomy]
```

## Sample Prompts by Scene Type

### SFW Scenes

#### 1. Coffee Shop
```
Prompt Engineering Output:
"photograph of [character], sitting at coffee shop table, casual clothes,
holding coffee cup, natural lighting, cozy atmosphere, indoor cafe setting,
wooden tables, photorealistic, cinematic lighting, detailed skin texture,
highly detailed, 8k uhd"
```

#### 2. Beach Sunset
```
"photograph of [character], standing at beach, summer outfit, sunset,
golden hour lighting, confident expression, beach background, sand,
ocean waves, blue sky, photorealistic, cinematic lighting, detailed skin texture,
highly detailed, 8k uhd"
```

#### 3. Gym Workout
```
"photograph of [character], gym setting, athletic wear, exercise pose,
gym equipment in background, dramatic lighting, determined expression,
indoor fitness center, photorealistic, detailed, 8k uhd"
```

#### 4. Bedroom Casual
```
"photograph of [character], bedroom setting, casual home wear,
sitting on bed, soft bedding, warm lighting, relaxed expression,
intimate setting, photorealistic, detailed skin texture, 8k uhd"
```

#### 5. Outdoor Park
```
"photograph of [character], outdoor park, natural daylight, trees,
casual outdoor clothes, natural pose, sunny day, green environment,
photorealistic, cinematic lighting, 8k uhd"
```

### NSFW Scenes (Anatomically Correct)

#### 1. Bedroom Intimate (Soft)
```
"photograph of [character], bedroom interior, lingerie, sitting on bed,
soft bedding, intimate setting, warm lighting, sultry expression,
realistic skin texture, detailed body, natural proportions, anatomically correct,
photorealistic, detailed, 8k uhd"

Negative: "bad anatomy, extra limbs, extra fingers, mutated hands,
fused fingers, bad proportions, deformed, blurry, low quality"
```

#### 2. Bedroom Intimate (Explicit)
```
"photograph of [character], bedroom, intimate pose, lying down,
soft lighting, detailed anatomy, realistic skin texture, detailed body,
natural proportions, anatomically correct, professional photography,
highly detailed, 8k uhd"

Negative: "bad anatomy, bad hands, missing fingers, extra fingers,
poorly drawn face, poorly drawn hands, fat, disfigured, mutation, ugly,
bad proportions, extra limbs"
```

#### 3. Bathroom Scene
```
"photograph of [character], bathroom setting, shower scene,
wet skin texture, water droplets, realistic lighting, detailed body,
natural proportions, anatomically correct, photorealistic,
highly detailed, 8k uhd"

Negative: "bad anatomy, bad hands, extra fingers, three hands,
poorly drawn body, deformed, blurry, low quality, cartoon"
```

## Consistency Testing Protocol

### Test 1: Same Scene, Different Prompts

Generate 3 images with slight prompt variations:
1. "portrait, smiling, natural lighting"
2. "portrait, serious expression, natural lighting"
3. "portrait, looking away, natural lighting"

**Verify**: Face structure, eye color, distinctive features remain identical

### Test 2: Different Scenes, Same Identity

Generate 3 different locations:
1. Coffee shop
2. Beach
3. Bedroom

**Verify**: Face stays consistent across environments

### Test 3: Different Poses

Generate 3 different poses:
1. Sitting
2. Standing
3. Lying down

**Verify**: Face identity preserved regardless of body position

### Test 4: NSFW Anatomy Test

Generate 2-3 NSFW images:

**Check for**:
- ✅ Correct number of fingers (5 per hand, unless hidden)
- ✅ Proper arm/leg count (2 of each)
- ✅ Realistic body proportions
- ✅ No "mushy" or merged anatomy
- ✅ Natural skin textures
- ✅ Coherent backgrounds
- ❌ No extra limbs
- ❌ No fused fingers
- ❌ No deformed faces

## Quality Checklist Per Image

### Identity Consistency ✓
- [ ] Face structure matches reference
- [ ] Eye color/shape identical
- [ ] Distinctive features present
- [ ] Overall facial similarity >90%

### Technical Quality ✓
- [ ] Sharp focus, not blurry
- [ ] Proper lighting
- [ ] Natural skin texture
- [ ] No obvious AI artifacts

### Anatomical Correctness ✓
- [ ] Correct limb count
- [ ] Proper finger count (if visible)
- [ ] Natural body proportions
- [ ] No deformities

### Context Adherence ✓
- [ ] Scene matches prompt
- [ ] Outfit appropriate
- [ ] Background coherent
- [ ] Lighting fits setting

## Sample Output Organization

Organize your generated samples:

```
generated_images/
├── male_character/
│   ├── 01_coffee_shop.png
│   ├── 02_beach_sunset.png
│   ├── 03_gym_workout.png
│   ├── 04_bedroom_casual.png
│   ├── 05_outdoor_park.png
│   ├── 06_nsfw_intimate.png (example 1)
│   └── 07_nsfw_explicit.png (example 2)
├── female_character/
│   ├── 01_coffee_shop.png
│   ├── 02_beach_sunset.png
│   ├── 03_gym_workout.png
│   ├── 04_bedroom_casual.png
│   ├── 05_outdoor_park.png
│   ├── 06_nsfw_intimate.png (example 1)
│   └── 07_nsfw_explicit.png (example 2)
└── comparison/
    ├── male_consistency_grid.png (all faces side by side)
    └── female_consistency_grid.png (all faces side by side)
```

## Creating Comparison Grids

Use this Python script to create side-by-side comparisons:

```python
from PIL import Image
import os

def create_comparison_grid(image_paths, output_path, grid_size=(3, 3)):
    """Create grid of images for consistency comparison"""
    images = [Image.open(p) for p in image_paths]

    # Resize all to same size
    size = (512, 512)
    images = [img.resize(size) for img in images]

    # Create grid
    rows, cols = grid_size
    grid_img = Image.new('RGB', (cols * size[0], rows * size[1]))

    for i, img in enumerate(images[:rows*cols]):
        row = i // cols
        col = i % cols
        grid_img.paste(img, (col * size[0], row * size[1]))

    grid_img.save(output_path)
    print(f"Created comparison grid: {output_path}")

# Usage
male_images = [
    "generated_images/male_character/01_coffee_shop.png",
    "generated_images/male_character/02_beach_sunset.png",
    # ... add all male images
]

create_comparison_grid(male_images, "generated_images/comparison/male_grid.png")
```

## Demo Video Script

### Introduction (15 seconds)
"This is Nectar AI - a character-consistent image generation system.
I'll demonstrate how the AI character maintains the same facial identity
across different scenes and contexts."

### Character Setup (30 seconds)
[Show screen]
- Upload reference image
- Enter character description
- Click "Start Chatting"

### Natural Conversation (2 minutes)
[Show conversation flow]
- Type: "Hey, what are you up to?"
- AI responds with text
- Type: "What are you wearing?"
- AI generates image - point out natural trigger
- Type: "Can you send me another photo from the beach?"
- AI generates beach scene
- Compare the two faces - highlight consistency

### Consistency Demonstration (30 seconds)
[Show comparison grid]
"As you can see, across 5 different scenes - coffee shop, beach, gym,
bedroom, and outdoor - the character's face remains perfectly consistent.
Same eyes, same bone structure, same distinctive features."

### NSFW Capability (30 seconds)
"The system also handles NSFW content with anatomically correct results.
Notice the proper anatomy, realistic skin textures, and maintained identity."

### Technical Overview (30 seconds)
[Show code/workflow briefly]
"Built with Next.js frontend, FastAPI backend, and ComfyUI with InstantID
for face consistency. Using SDXL base model with custom workflow optimizations."

### Conclusion (15 seconds)
"The entire pipeline maintains character identity while allowing flexible
scene generation. Thank you!"

## Final Submission Checklist

Before submitting, verify:

- [ ] **7+ high-quality images per character** (male + female)
- [ ] **2-3 NSFW examples each** (anatomically correct)
- [ ] **Comparison grids** created and included
- [ ] **Demo video** recorded (3-5 minutes)
- [ ] **All faces visually consistent** across scenes
- [ ] **No anatomy artifacts** in any image
- [ ] **Technical documentation** complete
- [ ] **GitHub repo** ready with all code
- [ ] **README** includes technical justifications

Good luck! 🚀
