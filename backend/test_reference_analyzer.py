"""
Test Reference Analyzer - GPT-4 Vision Feature Extraction
Demonstrates automatic character feature analysis from reference images
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.reference_analyzer import ReferenceAnalyzer
import json


def test_analyze_reference():
    """Test reference image analysis"""
    print("=" * 60)
    print("REFERENCE IMAGE ANALYZER TEST")
    print("=" * 60)

    analyzer = ReferenceAnalyzer()

    # Test images
    test_images = [
        {
            "path": "Copy of 8.jpg",
            "expected_gender": "woman",
            "description": "Female reference"
        },
        {
            "path": "Copy of 15.JPG",
            "expected_gender": "man",
            "description": "Male reference"
        }
    ]

    for test in test_images:
        print(f"\n{'=' * 60}")
        print(f"Testing: {test['description']}")
        print(f"Image: {test['path']}")
        print(f"{'=' * 60}")

        try:
            # Analyze image
            print(f"\n→ Analyzing reference image with GPT-4 Vision...")
            features = analyzer.analyze_reference_image(test['path'])

            print(f"\n✅ Analysis Complete!")
            print(f"\n📊 Extracted Features:")
            print(f"-" * 60)

            # Display key features
            print(f"  Gender: {features.get('gender', 'N/A')}")
            print(f"  Age Range: {features.get('age_range', 'N/A')}")
            print(f"  Ethnicity: {features.get('ethnicity', 'N/A')}")
            print(f"  Skin Tone: {features.get('skin_tone', 'N/A')}")
            print(f"  Body Type: {features.get('body_type', 'N/A')}")

            print(f"\n  Hair:")
            print(f"    Color: {features.get('hair_color', 'N/A')}")
            print(f"    Style: {features.get('hair_style', 'N/A')}")
            print(f"    Length: {features.get('hair_length', 'N/A')}")

            if features.get('facial_hair') and features['facial_hair'] != 'none':
                print(f"  Facial Hair: {features.get('facial_hair', 'N/A')}")

            print(f"\n  Eyes: {features.get('eye_color', 'N/A')}")
            print(f"  Face Shape: {features.get('face_shape', 'N/A')}")

            distinctive = features.get('distinctive_features', [])
            if distinctive:
                print(f"\n  Distinctive Features:")
                for feature in distinctive:
                    print(f"    - {feature}")

            print(f"\n  Overall Description:")
            print(f"    {features.get('overall_description', 'N/A')}")

            # Test format_features_for_prompt
            print(f"\n{'=' * 60}")
            print(f"NATURAL LANGUAGE DESCRIPTION (for prompts):")
            print(f"{'=' * 60}")
            prompt_desc = analyzer.format_features_for_prompt(features)
            print(f"\n{prompt_desc}")

            # Test get_compact_features
            print(f"\n{'=' * 60}")
            print(f"COMPACT FEATURES (for injection):")
            print(f"{'=' * 60}")
            compact = analyzer.get_compact_features(features)
            print(f"\nSubject: {compact['subject']}")
            print(f"Appearance: {compact['appearance']}")
            if compact['distinctive']:
                print(f"Distinctive: {compact['distinctive']}")

            # Show full JSON
            print(f"\n{'=' * 60}")
            print(f"FULL JSON OUTPUT:")
            print(f"{'=' * 60}")
            print(json.dumps(features, indent=2))

        except FileNotFoundError as e:
            print(f"\n⚠️  Warning: {e}")
            print(f"   Make sure reference image exists in ComfyUI/input/")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 60}")
    print(f"TEST COMPLETE")
    print(f"{'=' * 60}")

    print(f"\n💡 How this enhances prompts:")
    print(f"  1. Features are automatically extracted when reference is set")
    print(f"  2. LLM prompt engineer receives detailed character info")
    print(f"  3. Generated prompts include specific features:")
    print(f"     - Ethnicity (e.g., 'a young Asian woman')")
    print(f"     - Skin tone (e.g., 'fair complexion')")
    print(f"     - Hair details (e.g., 'long straight black hair')")
    print(f"     - Eye color (e.g., 'brown eyes')")
    print(f"     - Distinctive features (e.g., 'high cheekbones')")
    print(f"  4. Result: MUCH better character consistency across generations!")


if __name__ == "__main__":
    test_analyze_reference()
