# Nectar AI - Frontend

Streamlit-based chat interface for multi-modal AI character interaction.

## Features

- **Real-time Chat**: Interactive chat with AI character
- **Image Display**: Automatic display of generated character photos
- **Reference Management**: Easy reference image selection/upload
- **Conversation Reset**: Clear chat history anytime
- **Responsive UI**: Clean, modern interface

## Installation

```bash
cd frontend
pip install -r requirements.txt
```

## Usage

1. **Start the backend first**:
```bash
cd ../backend
python app.py
```

2. **Start Streamlit**:
```bash
streamlit  streamlit run streamlit_app.py --server.address 127.0.0.1
```

3. **Access in browser**: http://localhost:8501

## Configuration

The frontend connects to backend at `http://localhost:8000`. Update `BACKEND_URL` in `streamlit_app.py` if needed.

## Usage Guide

### Setting Up Character

1. **Select Gender**: Choose "woman" or "man" in sidebar
2. **Set Reference**:
   - Option 1: Select from existing images
   - Option 2: Upload your own photo
3. **Click "Set Reference"**

### Chatting

- Type messages in the chat input
- Character will respond naturally
- Photos are sent automatically when contextually appropriate

### Example Prompts

**SFW:**
- "What are you wearing?"
- "Where are you right now?"
- "Can you show me a photo?"

**NSFW:**
- "What are you wearing in your bedroom?"
- "Can you send me a sensual photo?"

## Technical Stack

- **Streamlit**: Web UI framework
- **Requests**: HTTP client for backend API
- **Pillow**: Image processing
