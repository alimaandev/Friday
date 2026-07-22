import { useState, useRef, useCallback, useEffect } from 'react'

export type VoiceOutputStatus = 'idle' | 'speaking' | 'paused'

interface UseVoiceOutputReturn {
  isSupported: boolean
  enabled: boolean
  setEnabled: (v: boolean) => void
  status: VoiceOutputStatus
  speak: (text: string) => void
  stop: () => void
  pause: () => void
  resume: () => void
  voices: SpeechSynthesisVoice[]
  selectedVoice: SpeechSynthesisVoice | null
  setVoice: (voice: SpeechSynthesisVoice) => void
}

export function useVoiceOutput(): UseVoiceOutputReturn {
  const [enabled, setEnabled] = useState(false)
  const [status, setStatus] = useState<VoiceOutputStatus>('idle')
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null)
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  const isSupported =
    typeof window !== 'undefined' && 'speechSynthesis' in window

  useEffect(() => {
    if (!isSupported) return
    const synth = window.speechSynthesis

    const loadVoices = () => {
      const v = synth.getVoices()
      if (v.length > 0) {
        setVoices(v)
        if (!selectedVoice) {
          const en = v.find(voice => voice.lang.startsWith('en'))
          setSelectedVoice(en || v[0])
        }
      }
    }

    loadVoices()
    synth.addEventListener('voiceschanged', loadVoices)
    return () => synth.removeEventListener('voiceschanged', loadVoices)
  }, [isSupported, selectedVoice])

  const speak = useCallback((text: string) => {
    if (!isSupported || !enabled || !text.trim()) return

    const synth = window.speechSynthesis
    synth.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    if (selectedVoice) utterance.voice = selectedVoice
    utterance.rate = 1
    utterance.pitch = 1
    utterance.volume = 1

    utterance.onstart = () => setStatus('speaking')
    utterance.onend = () => setStatus('idle')
    utterance.onerror = () => setStatus('idle')
    utterance.onpause = () => setStatus('paused')
    utterance.onresume = () => setStatus('speaking')

    utteranceRef.current = utterance
    synth.speak(utterance)
  }, [isSupported, enabled, selectedVoice])

  const stop = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.cancel()
    setStatus('idle')
  }, [isSupported])

  const pause = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.pause()
  }, [isSupported])

  const resume = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.resume()
  }, [isSupported])

  return {
    isSupported, enabled, setEnabled, status, speak, stop, pause, resume,
    voices, selectedVoice, setVoice: setSelectedVoice,
  }
}
