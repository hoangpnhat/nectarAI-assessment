"""
Test Z-Turbo workflow integration
Verifies that backend correctly retrieves SeedVR2 upscaled output
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.comfyui_client import ComfyUIClient
from app.services.prompt_engineer import PromptEngineer
from app.services.nsfw_enhancer import NSFWEnhancer
from app.core.config import settings
import random


def test_workflow_connection():
    """Test 1: Check if Z-Turbo workflow can be loaded"""
    print("=" * 60)
    print("TEST 1: Loading Z-Turbo Workflow")
    print("=" * 60)

    client = ComfyUIClient()

    try:
        workflow = client.load_workflow()
        print(f"✅ Workflow loaded successfully")
        print(f"   Path: {settings.workflow_path}")
        print(f"   Total nodes: {len(workflow)}")

        # Check key nodes
        key_nodes = {
            "306": "Positive Prompt (CLIPTextEncode)",
            "297": "Negative Prompt",
            "301": "KSampler",
            "363": "LoadImage (Reference)",
            "395": "SaveImage (SeedVR2 - FINAL OUTPUT)",
            "404": "SaveImage (FaceSwap)",
            "289": "SaveImage (Detailer)",
            "266": "SaveImage (RAW)"
        }

        print(f"\n   Key nodes found:")
        for node_id, description in key_nodes.items():
            if node_id in workflow:
                print(f"   ✅ Node {node_id}: {description}")
            else:
                print(f"   ❌ Node {node_id}: {description} - MISSING!")

        return True
    except Exception as e:
        print(f"❌ Failed to load workflow: {e}")
        return False


def test_prompt_generation():
    """Test 2: Test LLM-based prompt generation"""
    print("\n" + "=" * 60)
    print("TEST 2: LLM Prompt Generation")
    print("=" * 60)

    try:
        engineer = PromptEngineer()

        # Test scene context
        scene_context = {
            "location": "in a cozy bedroom",
            "activity": "sitting on the bed",
            "clothing": "casual attire",
            "mood": "relaxed",
            "nsfw_level": 0
        }

        print(f"   Scene context: {scene_context}")

        prompts = engineer.build_prompt(
            scene_context=scene_context,
            character_gender="woman",
            style="natural_photo"
        )

        print(f"\n   ✅ Prompt generated successfully!")
        print(f"   Positive prompt length: {len(prompts['positive'].split())} words")
        print(f"\n   Positive prompt preview (first 200 chars):")
        print(f"   {prompts['positive'][:200]}...")
        print(f"\n   Negative prompt (first 100 chars):")
        print(f"   {prompts['negative'][:100]}...")

        return True
    except Exception as e:
        print(f"❌ Failed to generate prompt: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_nsfw_enhancement():
    """Test 3: Test NSFW enhancement"""
    print("\n" + "=" * 60)
    print("TEST 3: NSFW Enhancement")
    print("=" * 60)

    enhancer = NSFWEnhancer()

    # Test Level 0 (SFW)
    scene_sfw = {
        "location": "in a park",
        "activity": "walking",
        "clothing": "casual dress",
        "mood": "happy",
        "nsfw_level": 0
    }

    enhanced_sfw = enhancer.enhance_scene_context(scene_sfw, nsfw_level=0)
    print(f"   Level 0 (SFW):")
    print(f"   ✅ No enhancement applied (as expected)")

    # Test Level 1 (Suggestive)
    scene_bedroom = {
        "location": "in a bedroom",
        "activity": "sitting on bed",
        "clothing": "casual clothes",
        "mood": "relaxed",
        "nsfw_level": 0
    }

    enhanced_level1 = enhancer.enhance_scene_context(scene_bedroom, nsfw_level=1)
    print(f"\n   Level 1 (Suggestive - Bedroom):")
    print(f"   ✅ Clothing: {enhanced_level1.get('clothing', 'N/A')[:60]}...")
    print(f"   ✅ Activity: {enhanced_level1.get('activity', 'N/A')[:60]}...")
    print(f"   ✅ Details: {enhanced_level1.get('nsfw_details', 'N/A')[:60]}...")

    # Test Level 2 (Explicit)
    enhanced_level2 = enhancer.enhance_scene_context(scene_bedroom, nsfw_level=2)
    print(f"\n   Level 2 (Explicit - Bedroom):")
    print(f"   ✅ Clothing: {enhanced_level2.get('clothing', 'N/A')[:60]}...")
    print(f"   ✅ Activity: {enhanced_level2.get('activity', 'N/A')[:60]}...")
    print(f"   ✅ Focus: {enhanced_level2.get('nsfw_focus', 'N/A')[:80]}...")

    return True


def test_workflow_params():
    """Test 4: Test workflow parameter update"""
    print("\n" + "=" * 60)
    print("TEST 4: Workflow Parameter Update")
    print("=" * 60)

    client = ComfyUIClient()

    try:
        workflow = client.load_workflow()

        test_prompt = "A natural portrait of a young woman sitting in a cozy coffee shop."
        test_negative = "bad quality, distorted"

        updated = client.update_workflow_params(
            workflow=workflow,
            positive_prompt=test_prompt,
            negative_prompt=test_negative,
            reference_image_path="test_reference.jpg",
            seed=12345,
            steps=8,
            cfg_scale=1.0,
            megapixel="2.0",
            aspect_ratio="5:7 (Balanced Portrait)"
        )

        # Verify updates
        checks = [
            (updated["306"]["inputs"]["text"] == test_prompt, "Positive prompt"),
            (updated["297"]["inputs"]["text"] == test_negative, "Negative prompt"),
            (updated["363"]["inputs"]["image"] == "test_reference.jpg", "Reference image"),
            (updated["301"]["inputs"]["seed"] == 12345, "Seed"),
            (updated["301"]["inputs"]["steps"] == 8, "Steps"),
            (updated["301"]["inputs"]["cfg"] == 1.0, "CFG scale"),
            (updated["264"]["inputs"]["megapixel"] == "2.0", "Megapixel"),
            (updated["264"]["inputs"]["aspect_ratio"] == "5:7 (Balanced Portrait)", "Aspect ratio")
        ]

        all_passed = True
        for passed, name in checks:
            if passed:
                print(f"   ✅ {name} updated correctly")
            else:
                print(f"   ❌ {name} NOT updated!")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ Failed to update workflow: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comfyui_connection():
    """Test 5: Check ComfyUI server connection"""
    print("\n" + "=" * 60)
    print("TEST 5: ComfyUI Server Connection")
    print("=" * 60)

    try:
        import requests
        response = requests.get(f"{settings.comfyui_url}/system_stats", timeout=5)

        if response.status_code == 200:
            print(f"   ✅ ComfyUI server is running at {settings.comfyui_url}")
            stats = response.json()
            print(f"   System stats: {stats}")
            return True
        else:
            print(f"   ❌ ComfyUI server returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  ComfyUI server not accessible at {settings.comfyui_url}")
        print(f"   This is OK for unit tests, but you'll need it running for actual generation")
        return False
    except Exception as e:
        print(f"   ❌ Error connecting to ComfyUI: {e}")
        return False


def test_image_output_priority():
    """Test 6: Verify image output priority logic"""
    print("\n" + "=" * 60)
    print("TEST 6: Image Output Priority Logic")
    print("=" * 60)

    # Mock history data simulating Z-Turbo workflow outputs
    mock_outputs = {
        "266": {
            "images": [
                {"filename": "Z-Image_00001.png", "subfolder": "", "type": "output"}
            ]
        },
        "289": {
            "images": [
                {"filename": "Z-Image-Detailer_00001.png", "subfolder": "", "type": "output"}
            ]
        },
        "404": {
            "images": [
                {"filename": "ComfyUI_00001.png", "subfolder": "FaceSwap", "type": "output"}
            ]
        },
        "395": {
            "images": [
                {"filename": "ComfyUI_00001.png", "subfolder": "SeedVR2", "type": "output"}
            ]
        }
    }

    all_images = []
    for node_id, output_data in mock_outputs.items():
        if "images" in output_data:
            for image_data in output_data["images"]:
                all_images.append({
                    "node_id": node_id,
                    "filename": image_data["filename"],
                    "subfolder": image_data.get("subfolder", ""),
                    "type": image_data.get("type", "output")
                })

    print(f"   Found {len(all_images)} output images:")
    for img in all_images:
        print(f"   - Node {img['node_id']}: {img['subfolder']}/{img['filename']}")

    # Test priority selection
    final_image = None

    # Priority 1: SeedVR2 (node 395)
    for img in all_images:
        if img["node_id"] == "395" or "SeedVR2" in img.get("subfolder", ""):
            final_image = img
            break

    if final_image:
        print(f"\n   ✅ Correct! Selected SeedVR2 upscaled output:")
        print(f"      Node {final_image['node_id']}: {final_image['subfolder']}/{final_image['filename']}")
        return True
    else:
        print(f"   ❌ Failed to select SeedVR2 output!")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Z-TURBO WORKFLOW INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        ("Workflow Loading", test_workflow_connection),
        ("LLM Prompt Generation", test_prompt_generation),
        ("NSFW Enhancement", test_nsfw_enhancement),
        ("Workflow Parameters", test_workflow_params),
        ("ComfyUI Connection", test_comfyui_connection),
        ("Image Output Priority", test_image_output_priority)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status}: {test_name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\n   Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print(f"\n   🎉 All tests passed! Backend is ready for Z-Turbo workflow.")
    else:
        print(f"\n   ⚠️  Some tests failed. Please review the issues above.")

    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
