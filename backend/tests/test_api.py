"""
Quick test script for backend API
"""
import requests
import json
import base64
from pathlib import Path
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*50)
    print("1. Testing Health Check")
    print("="*50)
    
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        result = r.json()
        print(f"✓ API Status: {result['api']}")
        print(f"✓ ComfyUI Status: {result['comfyui']}")
        print(f"✓ Reference Image Set: {result['reference_image_set']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_set_reference():
    """Test setting reference image"""
    print("\n" + "="*50)
    print("2. Setting Reference Image")
    print("="*50)
    
    try:
        r = requests.post(f"{BASE_URL}/set-reference", json={
            "image_path": "Copy of 9.jpg",  # Just filename, ComfyUI looks in input/ folder
            "gender": "woman"
        })
        result = r.json()
        print(f"✓ Status: {result['status']}")
        print(f"✓ Reference: {result['reference_image']}")
        print(f"✓ Gender: {result['character_gender']}")
        return True
    except Exception as e:
        print(f"✗ Set reference failed: {e}")
        return False

def test_simple_chat():
    """Test chat without image generation"""
    print("\n" + "="*50)
    print("3. Testing Simple Chat (No Image)")
    print("="*50)
    
    try:
        r = requests.post(f"{BASE_URL}/chat", json={
            "message": "Hi! How are you today?"
        })
        result = r.json()
        print(f"Character: {result['message']}")
        print(f"Image generated: {result['image_generated']}")
        return True
    except Exception as e:
        print(f"✗ Chat failed: {e}")
        return False

def test_chat_with_image():
    """Test chat with image generation"""
    print("\n" + "="*50)
    print("4. Testing Chat with Image Generation")
    print("="*50)
    print("This will take 30-60 seconds...")

    try:
        r = requests.post(f"{BASE_URL}/chat", json={
            "message": "What are you wearing right now?"
        }, timeout=120)

        result = r.json()
        print(f"\nDEBUG - Response: {result}")  # Debug line
        print(f"\nCharacter: {result['message']}")
        print(f"Image generated: {result['image_generated']}")
        
        if result['image_generated'] and result['image_base64']:
            # Save image
            output_dir = Path("../outputs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            img_data = base64.b64decode(result['image_base64'])
            output_path = output_dir / "test_chat_image.png"
            output_path.write_bytes(img_data)
            print(f"✓ Image saved to: {output_path}")
            return True
        else:
            print("✗ No image was generated")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out (>120s). ComfyUI might be slow or stuck.")
        return False
    except Exception as e:
        print(f"✗ Chat with image failed: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("BACKEND API TEST SUITE")
    print("="*50)
    print("\nMake sure:")
    print("1. ComfyUI is running on http://127.0.0.1:8188")
    print("2. Backend is running on http://localhost:8000")
    print("3. .env file has valid OPENAI_API_KEY")
    
    input("\nPress Enter to start tests...")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Set Reference", test_set_reference()))
    results.append(("Simple Chat", test_simple_chat()))
    results.append(("Chat with Image", test_chat_with_image()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
