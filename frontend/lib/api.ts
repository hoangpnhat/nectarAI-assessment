import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Message {
  role: 'user' | 'assistant'
  content: string
  imageUrl?: string
  timestamp?: number
}

export interface ChatResponse {
  message: string
  should_generate_image: boolean
  image_url?: string
  image_context?: any
  generation_time?: number
}

export const api = {
  async chat(
    message: string,
    conversationHistory: Message[],
    referenceImagePath: string,
    characterDescription: string
  ): Promise<ChatResponse> {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, {
      content: message,
      conversation_history: conversationHistory,
      reference_image_path: referenceImagePath,
      character_description: characterDescription,
    })

    return response.data
  },

  async uploadReferenceImage(file: File): Promise<string> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(`${API_BASE_URL}/api/upload-reference`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data.path
  },

  async checkHealth(): Promise<boolean> {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`)
      return response.data.status === 'healthy'
    } catch {
      return false
    }
  },

  getImageUrl(imageUrl: string): string {
    if (imageUrl.startsWith('http')) {
      return imageUrl
    }
    return `${API_BASE_URL}${imageUrl}`
  },
}
