"""
Quick test to verify backend configuration loads correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("BACKEND CONFIGURATION TEST")
print("=" * 60)

try:
    from app.core.config import settings
    print("\n✅ Settings loaded successfully!")

    print(f"\n📋 Configuration:")
    print(f"   ComfyUI URL: {settings.comfyui_url}")
    print(f"   Workflow: {settings.workflow_path}")
    print(f"   Steps: {settings.default_steps}")
    print(f"   CFG Scale: {settings.default_cfg_scale}")
    print(f"   Megapixel: {settings.default_megapixel}")
    print(f"   Aspect Ratio: {settings.default_aspect_ratio}")

    print(f"\n🎨 Detailers:")
    print(f"   Face: {settings.enable_face_detailer}")
    print(f"   Eyes: {settings.enable_eyes_detailer}")
    print(f"   Hands: {settings.enable_hands_detailer}")
    print(f"   Nipples: {settings.enable_nipples_detailer}")
    print(f"   Pussy: {settings.enable_pussy_detailer}")

    print(f"\n👤 Character:")
    print(f"   Name: {settings.character_name}")
    print(f"   Persona: {settings.character_persona}")

    # Test workflow loading
    print(f"\n📁 Testing workflow file...")
    workflow_path = Path(settings.workflow_path)
    if workflow_path.exists():
        print(f"   ✅ Workflow file exists: {workflow_path}")
        import json
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        print(f"   ✅ Workflow has {len(workflow)} nodes")

        # Check key nodes
        key_nodes = ["306", "297", "301", "363", "395", "404", "289", "266", "294"]
        found = [n for n in key_nodes if n in workflow]
        print(f"   ✅ Found {len(found)}/{len(key_nodes)} key nodes")
    else:
        print(f"   ⚠️  Workflow file not found: {workflow_path}")
        print(f"      (This is OK if you're using a different path)")

    # Test imports
    print(f"\n📦 Testing imports...")
    from app.services import ComfyUIClient, PromptEngineer, NSFWEnhancer, ChatAgent
    print(f"   ✅ ComfyUIClient")
    print(f"   ✅ PromptEngineer")
    print(f"   ✅ NSFWEnhancer")
    print(f"   ✅ ChatAgent")

    print(f"\n🎉 All tests passed! Backend is ready to start.")
    print(f"\n💡 To start the server:")
    print(f"   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
