'use client'

import { useState, useRef } from 'react'
import { api } from '@/lib/api'

interface CharacterSetupProps {
  onSetupComplete: (setup: {
    referenceImage: string
    characterDescription: string
  }) => void
}

export default function CharacterSetup({ onSetupComplete }: CharacterSetupProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [characterDescription, setCharacterDescription] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string)
      }
      reader.readAsDataURL(file)
      setError(null)
    }
  }

  const handleSubmit = async () => {
    if (!selectedFile || !characterDescription.trim()) {
      setError('Please provide both a reference image and character description')
      return
    }

    setUploading(true)
    setError(null)

    try {
      // Upload reference image
      const imagePath = await api.uploadReferenceImage(selectedFile)

      // Setup complete
      onSetupComplete({
        referenceImage: imagePath,
        characterDescription: characterDescription.trim(),
      })
    } catch (err) {
      setError('Failed to upload reference image. Please try again.')
      console.error(err)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Nectar AI
          </h1>
          <p className="text-gray-600">
            Create your AI character with consistent image generation
          </p>
        </div>

        <div className="space-y-6">
          {/* Reference Image Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Character Reference Image
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-purple-400 transition-colors"
            >
              {previewUrl ? (
                <div className="space-y-4">
                  <img
                    src={previewUrl}
                    alt="Reference preview"
                    className="max-w-xs max-h-64 mx-auto rounded-lg object-cover"
                  />
                  <p className="text-sm text-gray-600">
                    Click to change image
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <p className="text-gray-600">
                    Click to upload character reference photo
                  </p>
                  <p className="text-xs text-gray-500">
                    PNG, JPG up to 10MB
                  </p>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Character Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Character Description
            </label>
            <textarea
              value={characterDescription}
              onChange={(e) => setCharacterDescription(e.target.value)}
              placeholder="e.g., A 25-year-old woman with long brown hair and green eyes, athletic build, friendly smile"
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            />
            <p className="text-xs text-gray-500 mt-1">
              Describe the character's appearance, age, features, etc.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={uploading || !selectedFile || !characterDescription.trim()}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-lg transition-colors"
          >
            {uploading ? 'Setting up...' : 'Start Chatting'}
          </button>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            This demo uses AI to generate images. All images are generated based on your reference photo.
          </p>
        </div>
      </div>
    </div>
  )
}
