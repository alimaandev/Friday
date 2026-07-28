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

const VOICE_STORAGE_KEY = 'friday_tts_voice_uri'

export function useVoiceOutput(): UseVoiceOutputReturn {
  const [enabled, setEnabled] = useState(() => {
    const saved = localStorage.getItem('friday_voice_output_enabled')
    return saved ? saved === 'true' : false
  })
  const [status, setStatus] = useState<VoiceOutputStatus>('idle')
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  const [selectedVoice, setSelectedVoiceState] = useState<SpeechSynthesisVoice | null>(null)
  const selectedVoiceRef = useRef<SpeechSynthesisVoice | null>(null)
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)
  const speakQueueRef = useRef<string[]>([])
  const speakingRef = useRef(false)
  const synthRef = useRef<SpeechSynthesis | null>(null)

  const isSupported =
    typeof window !== 'undefined' && 'speechSynthesis' in window

  const processQueue = useCallback(() => {
    if (speakingRef.current || speakQueueRef.current.length === 0) return
    const synth = synthRef.current
    if (!synth) return

    const text = speakQueueRef.current.shift()!
    speakingRef.current = true

    const utterance = new SpeechSynthesisUtterance(text)
    if (selectedVoiceRef.current) utterance.voice = selectedVoiceRef.current
    utterance.rate = 1
    utterance.pitch = 1
    utterance.volume = 1

    utterance.onstart = () => setStatus('speaking')
    utterance.onend = () => {
      speakingRef.current = false
      if (speakQueueRef.current.length > 0) {
        processQueue()
      } else {
        setStatus('idle')
      }
    }
    utterance.onerror = () => {
      speakingRef.current = false
      setStatus('idle')
    }
    utterance.onpause = () => setStatus('paused')
    utterance.onresume = () => setStatus('speaking')

    utteranceRef.current = utterance
    synth.speak(utterance)
  }, [])

  const speak = useCallback((text: string) => {
    if (!isSupported || !enabled || !text.trim()) return
    speakQueueRef.current.push(text)
    processQueue()
  }, [isSupported, enabled, processQueue])

  const stop = useCallback(() => {
    const synth = synthRef.current
    if (synth) synth.cancel()
    speakQueueRef.current = []
    speakingRef.current = false
    setStatus('idle')
  }, [])

  const pause = useCallback(() => {
    const synth = synthRef.current
    if (synth) synth.pause()
  }, [])

  const resume = useCallback(() => {
    const synth = synthRef.current
    if (synth) synth.resume()
  }, [])

  const setVoice = useCallback((voice: SpeechSynthesisVoice) => {
    selectedVoiceRef.current = voice
    setSelectedVoiceState(voice)
    try { localStorage.setItem(VOICE_STORAGE_KEY, voice.voiceURI) } catch {}
  }, [])

  const setEnabledWrapped = useCallback((v: boolean) => {
    setEnabled(v)
    try { localStorage.setItem('friday_voice_output_enabled', String(v)) } catch {}
  }, [])

  useEffect(() => {
    if (!isSupported) return
    const synth = window.speechSynthesis
    synthRef.current = synth

    const loadVoices = () => {
      const v = synth.getVoices()
      if (v.length > 0) {
        setVoices(v)
        const savedURI = localStorage.getItem(VOICE_STORAGE_KEY)
        if (savedURI) {
          const match = v.find(vo => vo.voiceURI === savedURI)
          if (match) {
            selectedVoiceRef.current = match
            setSelectedVoiceState(match)
            return
          }
        }
        if (!selectedVoiceRef.current) {
          const en = v.find(vo => vo.lang.startsWith('en'))
          const fallback = en || v[0]
          selectedVoiceRef.current = fallback
          setSelectedVoiceState(fallback)
        }
      }
    }

    loadVoices()
    synth.addEventListener('voiceschanged', loadVoices)
    return () => synth.removeEventListener('voiceschanged', loadVoices)
  }, [isSupported])

  return {
    isSupported, enabled, setEnabled: setEnabledWrapped,
    status, speak, stop, pause, resume,
    voices, selectedVoice, setVoice,
  }
}