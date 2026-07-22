import { useState, useRef, useCallback, useEffect } from 'react'

export type VoiceStatus = 'idle' | 'listening' | 'error'

interface UseVoiceInputReturn {
  isSupported: boolean
  status: VoiceStatus
  interimTranscript: string
  finalTranscript: string
  error: string | null
  startListening: (lang?: string) => void
  stopListening: () => string
  resetTranscript: () => void
}

export function useVoiceInput(): UseVoiceInputReturn {
  const [status, setStatus] = useState<VoiceStatus>('idle')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [finalTranscript, setFinalTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)

  const recognitionRef = useRef<any>(null)
  const finalRef = useRef('')

  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  const resetTranscript = useCallback(() => {
    setInterimTranscript('')
    setFinalTranscript('')
    finalRef.current = ''
    setError(null)
  }, [])

  const startListening = useCallback((lang?: string) => {
    if (!isSupported) {
      setError('Speech recognition not supported')
      return
    }

    if (recognitionRef.current) {
      try { recognitionRef.current.abort() } catch {}
      recognitionRef.current = null
    }

    const SpeechRecognitionCtor =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const recognition = new SpeechRecognitionCtor()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = lang || 'en-US'

    recognition.onresult = (event: any) => {
      let interim = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalRef.current += transcript
          setFinalTranscript(finalRef.current)
        } else {
          interim += transcript
        }
      }
      setInterimTranscript(interim)
    }

    recognition.onerror = (event: any) => {
      if (event.error === 'no-speech' || event.error === 'aborted') {
        setStatus('idle')
      } else {
        setStatus('error')
        setError(event.error)
      }
    }

    recognition.onend = () => {
      setStatus('idle')
      setInterimTranscript('')
    }

    recognitionRef.current = recognition
    setStatus('listening')
    setError(null)
    finalRef.current = ''
    setFinalTranscript('')
    setInterimTranscript('')

    try {
      recognition.start()
    } catch {
      setStatus('error')
      setError('Failed to start recognition')
    }
  }, [isSupported])

  const stopListening = useCallback((): string => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop() } catch {}
      recognitionRef.current = null
    }
    const transcript = finalRef.current
    return transcript
  }, [])

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort() } catch {}
      }
    }
  }, [])

  return { isSupported, status, interimTranscript, finalTranscript, error, startListening, stopListening, resetTranscript }
}
