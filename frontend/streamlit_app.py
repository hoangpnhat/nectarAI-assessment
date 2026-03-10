"""
Streamlit Chat Interface for Nectar AI Assessment
Multi-modal chat with character-consistent image generation
"""
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
st.set_page_config(
    page_title="Nectar AI - Character Chat",
    page_icon="💬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.stChatMessage {
    padding: 1rem;
    border-radius: 0.5rem;
}
.user-message {
    background-color: #e3f2fd;
}
.assistant-message {
    background-color: #f5f5f5;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'reference_set' not in st.session_state:
    st.session_state.reference_set = False
if 'character_name' not in st.session_state:
    st.session_state.character_name = "Emma"

def check_backend_health():
    """Check if backend is accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.json()
    except:
        return None

def set_reference_image(image_path, gender):
    """Set reference image for character"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/set-reference",
            json={"image_path": image_path, "gender": gender}
        )
        return response.json()
    except Exception as e:
        st.error(f"Failed to set reference: {e}")
        return None

def upload_reference_image(uploaded_file, gender):
    """Upload reference image file"""
    try:
        files = {"file": uploaded_file}
        data = {"gender": gender}
        response = requests.post(
            f"{BACKEND_URL}/upload-reference",
            files=files,
            data=data
        )
        return response.json()
    except Exception as e:
        st.error(f"Failed to upload reference: {e}")
        return None

def send_chat_message(message, gender="woman"):
    """Send chat message and get response"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message, "character_gender": gender},
            timeout=180  # 3 minutes for image generation
        )
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out. Image generation may be taking longer than expected.")
        return None
    except Exception as e:
        st.error(f"Chat failed: {e}")
        return None

def reset_conversation():
    """Reset conversation history"""
    try:
        requests.post(f"{BACKEND_URL}/reset-conversation")
        st.session_state.messages = []
        st.success("Conversation reset!")
    except Exception as e:
        st.error(f"Failed to reset: {e}")

def display_image_from_base64(base64_str):
    """Display image from base64 string"""
    try:
        img_data = base64.b64decode(base64_str)
        img = Image.open(BytesIO(img_data))
        st.image(img, use_column_width=True)  # Compatible with older Streamlit
    except Exception as e:
        st.error(f"Failed to display image: {e}")

# Main UI
st.title("💬 Nectar AI - Character Chat")
st.markdown("Chat with an AI character who can send photos of themselves")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Backend status
    health = check_backend_health()
    if health:
        st.success(f"✅ Backend: {health['api']}")
        st.success(f"✅ ComfyUI: {health['comfyui']}")
        if health.get('reference_image_set'):
            st.success("✅ Reference image set")
            st.session_state.reference_set = True
        else:
            st.warning("⚠️ No reference image set")
    else:
        st.error("❌ Backend not accessible")
        st.stop()

    st.divider()

    # Reference image setup
    st.header("📸 Character Reference")

    # Gender selection
    gender = st.selectbox("Character Gender", ["woman", "man"])

    # Option 1: Select from existing images
    st.subheader("Option 1: Select existing")
    available_images = [
        "Copy of 9.jpg",
        "Copy of 1.jpeg",
        "Copy of 4.jpg",
        "Copy of 10.JPG"
    ]
    selected_image = st.selectbox("Choose reference image", available_images)

    if st.button("Set Reference", type="primary"):
        result = set_reference_image(selected_image, gender)
        if result and result.get('status') == 'ok':
            st.success(f"✅ Reference set: {selected_image}")
            st.session_state.reference_set = True
            st.session_state.character_name = "Emma" if gender == "woman" else "Alex"
            st.rerun()

    st.divider()

    # Option 2: Upload new image
    st.subheader("Option 2: Upload new")
    uploaded_file = st.file_uploader(
        "Upload reference photo",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear face photo for the character"
    )

    if uploaded_file and st.button("Upload & Set"):
        result = upload_reference_image(uploaded_file, gender)
        if result and result.get('status') == 'ok':
            st.success(f"✅ Uploaded: {result['filename']}")
            st.session_state.reference_set = True
            st.rerun()

    st.divider()

    # Reset conversation
    if st.button("🔄 Reset Conversation"):
        reset_conversation()
        st.rerun()

    st.divider()
    st.caption(f"Character: {st.session_state.character_name}")
    st.caption("Nectar AI Assessment 2026")

# Main chat area
if not st.session_state.reference_set:
    st.warning("⚠️ Please set a reference image in the sidebar to start chatting")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("image"):
            display_image_from_base64(message["image"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = send_chat_message(prompt, gender)

            if response:
                # Display text response
                st.markdown(response["message"])

                # Display image if generated
                if response.get("image_generated") and response.get("image_base64"):
                    with st.spinner("Generated image:"):
                        display_image_from_base64(response["image_base64"])

                    # Save message with image
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["message"],
                        "image": response["image_base64"]
                    })
                else:
                    # Save message without image
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["message"]
                    })
            else:
                st.error("Failed to get response from the character")

# Example prompts
with st.expander("💡 Example prompts to try"):
    st.markdown("""
    **SFW prompts:**
    - "Hi! How are you today?"
    - "What are you wearing?"
    - "Where are you right now?"
    - "Can you show me a photo?"

    **NSFW prompts:**
    - "What are you wearing in your bedroom?"
    - "Can you send me a sensual photo?"
    - "Show me your lingerie"

    The character will naturally decide when to send photos based on context.
    """)
