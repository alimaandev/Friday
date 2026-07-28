import { useState, useRef, useCallback, useEffect } from 'react'

interface UseWakeWordReturn {
  isSupported: boolean
  active: boolean
  listening: boolean
  error: string | null
  start: () => void
  stop: () => void
}

const WAKE_PATTERN = /\bhey\s*friday\b/i
const COOLDOWN_MS = 5000
const SESSION_RENEW_INTERVAL = 40000

export function useWakeWord(onWake: () => void): UseWakeWordReturn {
  const [active, setActive] = useState(false)
  const [listening, setListening] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<any>(null)
  const cooldownRef = useRef(0)
  const activeRef = useRef(false)
  const sessionGenRef = useRef(0)
  const renewIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const onWakeRef = useRef(onWake)
  onWakeRef.current = onWake

  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  const stop = useCallback(() => {
    if (renewIntervalRef.current) {
      clearInterval(renewIntervalRef.current)
      renewIntervalRef.current = null
    }
    if (recognitionRef.current) {
      try { recognitionRef.current.abort() } catch {}
      recognitionRef.current = null
    }
    activeRef.current = false
    setActive(false)
    setListening(false)
  }, [])

  const startSession = useCallback(() => {
    if (!activeRef.current) return

    const SpeechRecognitionCtor =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const recognition = new SpeechRecognitionCtor()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    const gen = sessionGenRef.current

    recognition.onresult = (event: any) => {
      const now = Date.now()
      if (now - cooldownRef.current < COOLDOWN_MS) return
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript.toLowerCase()
        if (WAKE_PATTERN.test(transcript)) {
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
      recognitionRef.current = null
      if (activeRef.current && gen === sessionGenRef.current) {
        startSession()
      }
    }

    recognitionRef.current = recognition

    try {
      recognition.start()
      setListening(true)
    } catch {
      setError('Failed to start wake word detection')
      setActive(false)
      setListening(false)
      activeRef.current = false
    }
  }, [])

  const start = useCallback(() => {
    if (!isSupported) {
      setError('Speech recognition not supported')
      return
    }

    stop()
    activeRef.current = true
    sessionGenRef.current += 1
    setActive(true)
    setError(null)

    startSession()

    renewIntervalRef.current = setInterval(() => {
      if (!activeRef.current) return
      sessionGenRef.current += 1
      if (recognitionRef.current) {
        try { recognitionRef.current.abort() } catch {}
        recognitionRef.current = null
      }
      startSession()
    }, SESSION_RENEW_INTERVAL)
  }, [isSupported, stop, startSession])

  useEffect(() => {
    return () => {
      if (renewIntervalRef.current) {
        clearInterval(renewIntervalRef.current)
      }
      if (recognitionRef.current) {
        try { recognitionRef.current.abort() } catch {}
      }
    }
  }, [])

  return { isSupported, active, listening, error, start, stop }
}