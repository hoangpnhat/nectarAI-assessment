"""
Universal Sample Generator for Z-Turbo Workflow
Generates character-consistent images for both male and female characters
Assessment submission: 5+ diverse scenes with SFW and NSFW mix
"""
import requests
import base64
from pathlib import Path
import time
import random
import sys

BASE_URL = "http://localhost:8000"

# ============================================================================
# FEMALE CHARACTER SCENARIOS (Chat-based generation)
# ============================================================================
FEMALE_SCENARIOS = [
    # SFW Scenes
    {
        "name": "female_cafe_sfw",
        "reference": "Copy of 8.jpg",
        "gender": "woman",
        "message": "Where are you right now? I'm curious about your surroundings. Send me a photo!",
        "description": "SFW - Woman in cozy cafe",
        "nsfw_level": 0
    },
    {
        "name": "female_park_sfw",
        "reference": "Copy of 8.jpg",
        "gender": "woman",
        "message": "What are you wearing at the park today? Can I see your outfit?",
        "description": "SFW - Woman at park, casual attire",
        "nsfw_level": 0
    },
    # Suggestive Scenes
    {
        "name": "female_bedroom_suggestive",
        "reference": "Copy of 8.jpg",
        "gender": "woman",
        "message": "What are you wearing in your bedroom right now? Show me a photo.",
        "description": "Suggestive - Woman in bedroom, intimate setting",
        "nsfw_level": 1
    },
    # NSFW Scenes
    {
        "name": "female_mirror_nsfw",
        "reference": "Copy of 8.jpg",
        "gender": "woman",
        "message": "Can you take a full body mirror photo? I'd love to see all of you.",
        "description": "NSFW - Full body nude mirror photo",
        "nsfw_level": 2
    },
    {
        "name": "female_lingerie_nsfw",
        "reference": "Copy of 8.jpg",
        "gender": "woman",
        "message": "What are you wearing underneath? Can you show me your lingerie?",
        "description": "NSFW - Intimate lingerie/underwear",
        "nsfw_level": 2
    },
]

# ============================================================================
# MALE CHARACTER SCENARIOS (Direct generation with natural language prompts)
# ============================================================================
MALE_SCENARIOS = [
    # SFW Scenes
    {
        "name": "male_gym_sfw",
        "reference": "Copy of 15.JPG",
        "gender": "man",
        "positive": """A natural portrait photograph of a young athletic man at a modern gym. He has a fit, muscular physique with defined shoulders and arms. He wears a fitted black tank top and athletic shorts, showing his toned body. His complexion is warm with natural skin texture, slight perspiration visible from working out. He stands near weight equipment with a confident, relaxed posture. The gym has bright fluorescent lighting mixed with natural light from large windows, creating dynamic highlights across his muscles. Background shows gym equipment slightly out of focus, maintaining attention on the subject. Professional fitness photography style, shot with 35mm lens, natural color grading. High resolution, hyperrealistic detailing, photorealistic skin texture.""",
        "negative": "cartoon, anime, 3d render, illustration, drawing, deformed, bad anatomy, extra limbs, ugly, blurry, low quality, watermark, text, plastic skin, overweight",
        "description": "SFW - Man at gym, athletic"
    },
    {
        "name": "male_office_sfw",
        "reference": "Copy of 15.JPG",
        "gender": "man",
        "positive": """A professional portrait of a young man in a modern office environment. He wears a crisp white business casual shirt with rolled-up sleeves, seated at a clean desk with a laptop visible. His posture is confident and relaxed, leaning slightly back in his ergonomic chair. The office has large windows with soft natural afternoon light filtering through, creating a professional atmosphere. Behind him, blurred office elements like bookshelves and modern decor suggest a corporate environment. His expression is calm and professional, with a slight smile. Shot with shallow depth of field, 50mm lens, corporate photography style. High resolution, hyperrealistic detailing, natural color palette with cool tones.""",
        "negative": "cartoon, anime, 3d render, illustration, drawing, deformed, bad anatomy, extra limbs, ugly, blurry, low quality, watermark, text",
        "description": "SFW - Man in modern office"
    },
    # Suggestive Scene
    {
        "name": "male_bedroom_suggestive",
        "reference": "Copy of 15.JPG",
        "gender": "man",
        "positive": """A casual intimate portrait of a young man in a bedroom setting. He wears comfortable loungewear - a simple fitted t-shirt and casual sweatpants, relaxing on a bed with soft bedding. His posture is natural and relaxed, reclining against pillows. The bedroom has warm, intimate lighting from bedside lamps, creating a cozy evening atmosphere. Soft shadows play across his features and the room. Background shows hints of bedroom furniture - a nightstand, soft throw pillows - all slightly out of focus. The mood is relaxed and intimate without being explicit. Shot with natural bedroom lighting, 35mm lens, editorial style photography. High resolution, hyperrealistic detailing, warm color palette.""",
        "negative": "cartoon, anime, 3d render, illustration, drawing, deformed, bad anatomy, extra limbs, ugly, blurry, low quality, watermark, text, plastic skin",
        "description": "Suggestive - Man in bedroom, relaxed"
    },
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)

def test_connectivity():
    """Test if backend and ComfyUI are accessible"""
    print("\n→ Testing connectivity...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        health = r.json()

        if health['api'] != 'ok':
            print("✗ Backend API not healthy")
            return False

        if health['comfyui'] != 'ok':
            print("✗ ComfyUI not accessible")
            print("  Make sure ComfyUI is running on http://127.0.0.1:8188")
            return False

        print("✓ Backend API: OK")
        print("✓ ComfyUI: OK")
        return True
    except Exception as e:
        print(f"✗ Connectivity test failed: {e}")
        print("  Make sure backend is running on http://localhost:8000")
        return False

# ============================================================================
# FEMALE CHARACTER GENERATION (Chat-based)
# ============================================================================

def generate_female_sample(scenario, index, total):
    """
    Generate female character image via chat endpoint
    Uses LLM to generate natural language prompts
    """
    print(f"\n{'=' * 60}")
    print(f"[{index}/{total}] {scenario['name']}")
    print(f"Description: {scenario['description']}")
    print(f"NSFW Level: {scenario['nsfw_level']}")
    print(f"{'=' * 60}")

    try:
        # Set reference
        print("→ Setting reference image...")
        r = requests.post(f"{BASE_URL}/set-reference", json={
            "image_path": scenario['reference'],
            "gender": scenario['gender']
        })

        # Reset conversation for clean context
        print("→ Resetting conversation...")
        requests.post(f"{BASE_URL}/reset-conversation")

        # Chat to trigger image generation
        print(f"→ User: \"{scenario['message'][:60]}...\"")
        print("→ Generating with Z-Turbo workflow...")
        print("   (Base → Detailers → FaceSwap → Upscale)")
        print("   Estimated time: 90-180 seconds...")

        start_time = time.time()

        r = requests.post(f"{BASE_URL}/chat", json={
            "message": scenario['message'],
            "character_gender": scenario['gender']
        }, timeout=300)

        elapsed = time.time() - start_time
        response = r.json()

        # Print character response
        print(f"\n💬 Character: \"{response['message'][:80]}...\"")
        print(f"⏱️  Generation time: {elapsed:.1f}s")

        if response['image_generated'] and response['image_base64']:
            # Save image
            output_dir = Path("../outputs/samples")
            output_dir.mkdir(parents=True, exist_ok=True)

            img_data = base64.b64decode(response['image_base64'])
            output_path = output_dir / f"{scenario['name']}.png"
            output_path.write_bytes(img_data)

            # Check file size
            size_mb = len(img_data) / (1024 * 1024)
            print(f"✅ SUCCESS: {output_path.name} ({size_mb:.2f} MB)")

            if size_mb < 0.1:
                print(f"   ⚠️  Warning: File size very small, might be black image!")

            return True
        else:
            print(f"❌ FAILED: No image generated")
            print(f"   Response: {response}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ FAILED: Request timed out (>300s)")
        print(f"   Z-Turbo workflow might be stuck or VRAM insufficient")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

# ============================================================================
# MALE CHARACTER GENERATION (Direct generation)
# ============================================================================

def generate_male_sample(scenario, index, total):
    """
    Generate male character image via direct generation endpoint
    Uses pre-written natural language prompts
    """
    print(f"\n{'=' * 60}")
    print(f"[{index}/{total}] {scenario['name']}")
    print(f"Description: {scenario['description']}")
    print(f"{'=' * 60}")

    try:
        print("→ Setting male reference image...")
        requests.post(f"{BASE_URL}/set-reference", json={
            "image_path": scenario['reference'],
            "gender": scenario['gender']
        })

        print("→ Generating with Z-Turbo workflow...")
        print("   (Base → Detailers → FaceSwap → Upscale)")
        print("   Estimated time: 90-180 seconds...")

        start_time = time.time()

        # Direct generation via /generate-image endpoint (Z-Turbo params)
        response = requests.post(
            f"{BASE_URL}/generate-image",
            json={
                "positive_prompt": scenario["positive"],
                "negative_prompt": scenario["negative"],
                "reference_image": scenario["reference"],
                "seed": random.randint(0, 2**32 - 1),
                "steps": 8,  # Z-Turbo default
                "cfg_scale": 1.0,  # Z-Turbo default
                "megapixel": "2.0",
                "aspect_ratio": "5:7 (Balanced Portrait)"
            },
            timeout=300
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            # Save image
            output_dir = Path("../outputs/samples")
            output_dir.mkdir(parents=True, exist_ok=True)

            output_path = output_dir / f"{scenario['name']}.png"
            output_path.write_bytes(response.content)

            # Check file size
            size_mb = len(response.content) / (1024 * 1024)
            print(f"⏱️  Generation time: {elapsed:.1f}s")
            print(f"✅ SUCCESS: {output_path.name} ({size_mb:.2f} MB)")

            if size_mb < 0.1:
                print(f"   ⚠️  Warning: File size very small, might be black image!")

            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ FAILED: Request timed out (>300s)")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

# ============================================================================
# BATCH GENERATION
# ============================================================================

def generate_batch(scenarios, generator_func, character_type):
    """Generate a batch of scenarios"""
    results = []
    total = len(scenarios)

    print(f"\n🎬 Starting {character_type} character generation...")
    print(f"   Total scenarios: {total}")

    for i, scenario in enumerate(scenarios, 1):
        success = generator_func(scenario, i, total)
        results.append((scenario['name'], success))

        # Wait between generations
        if i < total:
            print(f"\n⏳ Waiting 5 seconds before next generation...")
            time.sleep(5)

    return results

# ============================================================================
# MAIN MENU
# ============================================================================

def print_menu():
    """Print generation menu"""
    print_header("Z-TURBO SAMPLE GENERATOR")

    print("\n📋 Available Options:")
    print("  1. Generate ALL samples (Female + Male)")
    print("  2. Generate FEMALE samples only (5 scenes)")
    print("  3. Generate MALE samples only (3 scenes)")
    print("  4. Generate CUSTOM selection")
    print("  0. Exit")

    print("\n📊 Sample Breakdown:")
    print(f"  Female: {len(FEMALE_SCENARIOS)} scenarios")
    print(f"    - SFW: 2 scenes")
    print(f"    - Suggestive: 1 scene")
    print(f"    - NSFW: 2 scenes")
    print(f"  Male: {len(MALE_SCENARIOS)} scenarios")
    print(f"    - SFW: 2 scenes")
    print(f"    - Suggestive: 1 scene")

    print("\n⏱️  Estimated Time:")
    print(f"  Per image: ~90-180 seconds")
    print(f"  All images: ~{(len(FEMALE_SCENARIOS) + len(MALE_SCENARIOS)) * 2} minutes")

    print("\n⚠️  Requirements:")
    print("  ✓ ComfyUI running on http://127.0.0.1:8188")
    print("  ✓ Backend running on http://localhost:8000")
    print("  ✓ Z-Turbo workflow loaded")
    print("  ✓ ReActor NSFW bypass applied")
    print("  ✓ Reference images in ComfyUI/input/")
    print("    - Female: Copy of 8.jpg")
    print("    - Male: Copy of 15.JPG")

def print_summary(results, character_type=""):
    """Print generation summary"""
    print_header(f"{character_type} GENERATION SUMMARY".strip())

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    successful = sum(1 for _, s in results if s)
    total = len(results)

    print(f"\n📊 Results: {successful}/{total} successful")

    if successful > 0:
        print(f"\n✅ Images saved to: outputs/samples/")
        print(f"\n📁 Next steps:")
        print(f"  1. Review images in outputs/samples/")
        print(f"  2. Verify character consistency across scenes")
        print(f"  3. Check quality (should be 3-8MB per image)")
        print(f"  4. Add to GitHub repo for assessment")

    return successful == total

def main():
    """Main entry point"""

    # Test connectivity first
    if not test_connectivity():
        print("\n❌ Connectivity check failed!")
        print("   Make sure ComfyUI and backend are running.")
        return 1

    # Show menu
    print_menu()

    while True:
        try:
            choice = input("\n👉 Select option (0-4): ").strip()

            if choice == "0":
                print("\n👋 Exiting...")
                return 0

            elif choice == "1":
                # Generate ALL
                input("\n▶️  Generate ALL samples? Press Enter to continue (Ctrl+C to cancel)...")

                female_results = generate_batch(FEMALE_SCENARIOS, generate_female_sample, "FEMALE")
                print("\n" + "=" * 60)
                male_results = generate_batch(MALE_SCENARIOS, generate_male_sample, "MALE")

                all_results = female_results + male_results
                success = print_summary(all_results, "OVERALL")
                return 0 if success else 1

            elif choice == "2":
                # Generate FEMALE only
                input("\n▶️  Generate FEMALE samples? Press Enter to continue (Ctrl+C to cancel)...")

                results = generate_batch(FEMALE_SCENARIOS, generate_female_sample, "FEMALE")
                success = print_summary(results, "FEMALE")
                return 0 if success else 1

            elif choice == "3":
                # Generate MALE only
                input("\n▶️  Generate MALE samples? Press Enter to continue (Ctrl+C to cancel)...")

                results = generate_batch(MALE_SCENARIOS, generate_male_sample, "MALE")
                success = print_summary(results, "MALE")
                return 0 if success else 1

            elif choice == "4":
                # Custom selection
                print("\n📝 Custom selection:")
                print("   Female scenarios:")
                for i, s in enumerate(FEMALE_SCENARIOS, 1):
                    print(f"     {i}. {s['name']} - {s['description']}")
                print(f"\n   Male scenarios:")
                for i, s in enumerate(MALE_SCENARIOS, 1):
                    print(f"     {i + len(FEMALE_SCENARIOS)}. {s['name']} - {s['description']}")

                selected = input("\n   Enter numbers (comma-separated, e.g., 1,3,5): ").strip()
                indices = [int(x.strip()) - 1 for x in selected.split(",")]

                all_scenarios = FEMALE_SCENARIOS + MALE_SCENARIOS
                custom_scenarios = [all_scenarios[i] for i in indices if 0 <= i < len(all_scenarios)]

                if not custom_scenarios:
                    print("❌ No valid scenarios selected")
                    continue

                input(f"\n▶️  Generate {len(custom_scenarios)} samples? Press Enter to continue...")

                results = []
                for i, scenario in enumerate(custom_scenarios, 1):
                    if scenario in FEMALE_SCENARIOS:
                        success = generate_female_sample(scenario, i, len(custom_scenarios))
                    else:
                        success = generate_male_sample(scenario, i, len(custom_scenarios))
                    results.append((scenario['name'], success))

                    if i < len(custom_scenarios):
                        time.sleep(5)

                success = print_summary(results, "CUSTOM")
                return 0 if success else 1

            else:
                print("❌ Invalid choice. Please select 0-4.")

        except KeyboardInterrupt:
            print("\n\n🛑 Cancelled by user")
            return 1
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
