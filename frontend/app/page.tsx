'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import CharacterSetup from '@/components/CharacterSetup'

export default function Home() {
  const [characterSetup, setCharacterSetup] = useState<{
    referenceImage: string | null
    characterDescription: string
  } | null>(null)

  if (!characterSetup) {
    return <CharacterSetup onSetupComplete={setCharacterSetup} />
  }

  return (
    <ChatInterface
      referenceImage={characterSetup.referenceImage!}
      characterDescription={characterSetup.characterDescription}
      onReset={() => setCharacterSetup(null)}
    />
  )
}
