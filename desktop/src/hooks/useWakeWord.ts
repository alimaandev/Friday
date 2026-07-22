import { useState, useRef, useCallback, useEffect } from 'react'

interface UseWakeWordReturn {
  isSupported: boolean
  active: boolean
  listening: boolean
  error: string | null
  start: () => void
  stop: () => void
}

const WAKE_PATTERNS = [/\bhey\s*friday\b/i, /\bfriday\b/i]
const COOLDOWN_MS = 5000

export function useWakeWord(onWake: () => void): UseWakeWordReturn {
  const [active, setActive] = useState(false)
  const [listening, setListening] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<any>(null)
  const cooldownRef = useRef(0)
  const activeRef = useRef(false)
  const onWakeRef = useRef(onWake)
  onWakeRef.current = onWake

  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  const stop = useCallback(() => {
    if (recognitionRef.current) {
      try { recognitionRef.current.abort() } catch {}
      recognitionRef.current = null
    }
    activeRef.current = false
    setActive(false)
    setListening(false)
  }, [])

  const start = useCallback(() => {
    if (!isSupported) {
      setError('Speech recognition not supported')
      return
    }

    stop()

    const SpeechRecognitionCtor =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const recognition = new SpeechRecognitionCtor()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event: any) => {
      const now = Date.now()
      if (now - cooldownRef.current < COOLDOWN_MS) return

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript.toLowerCase()
          if (WAKE_PATTERNS.some(p => p.test(transcript))) {
            cooldownRef.current = now
            onWakeRef.current()
            break
        }
      }
    }

    recognition.onerror = (event: any) => {
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        setError(event.error)
      }
    }

    recognition.onend = () => {
      setListening(false)
      if (activeRef.current && recognitionRef.current === recognition) {
        try { recognition.start() } catch {}
        setListening(true)
      }
    }

    recognitionRef.current = recognition
    activeRef.current = true
    setActive(true)
    setError(null)

    try {
      recognition.start()
      setListening(true)
    } catch {
      setError('Failed to start wake word detection')
      setActive(false)
      setListening(false)
    }
  }, [isSupported, stop])

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort() } catch {}
      }
    }
  }, [])

  return { isSupported, active, listening, error, start, stop }
}
