import { useState, useRef, useCallback, memo } from 'react'

const LANG_LABELS: Record<string, string> = { 'en-US': 'EN', 'hi-IN': 'HI', 'ur-PK': 'UR' }

const SUGGESTIONS = [
  { label: 'Explain', action: 'Explain this concept in simple terms' },
  { label: 'Search', action: 'Search the web for' },
  { label: 'Code', action: 'Write code to' },
  { label: 'Automate', action: 'Autopilot: ' },
]

interface ZenInputProps {
  onSend: (text: string) => void
  loading: boolean
  onVoiceStart: () => void
  onVoiceStop: () => string
  voiceStatus: 'idle' | 'listening' | 'error'
  voiceInterim: string
  isVoiceSupported: boolean
  voiceLanguage: string
  onCycleLanguage: () => void
}

export const ZenInput = memo(function ZenInput({
  onSend, loading, onVoiceStart, onVoiceStop, voiceStatus, voiceInterim, isVoiceSupported,
  voiceLanguage, onCycleLanguage,
}: ZenInputProps) {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const send = useCallback(() => {
    const text = value.trim()
    if (text && !loading) {
      setValue('')
      onSend(text)
    }
  }, [value, loading, onSend])

  const isListening = voiceStatus === 'listening'
  const borderColor = isListening
    ? 'rgba(255,255,255,0.35)'
    : focused
      ? 'rgba(255,255,255,0.2)'
      : 'rgba(255,255,255,0.08)'

  return (
    <div className="flex justify-center px-8 pb-6 pt-3">
      <div className="w-full max-w-[720px]">
        <div
          className="rounded-2xl transition-all duration-300 glass"
          style={{
            border: `1px solid ${borderColor}`,
            boxShadow: isListening
              ? '0 8px 40px rgba(0,0,0,0.5), 0 0 60px rgba(255,255,255,0.05)'
              : focused
                ? '0 8px 40px rgba(0,0,0,0.5), 0 0 40px rgba(255,255,255,0.02)'
                : '0 4px 24px rgba(0,0,0,0.3)',
          }}
        >
          <div className="relative flex items-end">
            <textarea
              ref={inputRef}
              rows={1}
              value={value}
              onChange={e => setValue(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  send()
                }
              }}
              placeholder="Message Friday..."
              disabled={loading}
              className="w-full resize-none bg-transparent outline-none text-sm leading-relaxed py-4 pl-5 pr-32 placeholder:text-neutral-600"
              style={{
                color: '#e5e5e5',
                minHeight: '56px',
                maxHeight: '160px',
                fontWeight: 350,
                letterSpacing: '0.01em',
              }}
            />

            {isListening && voiceInterim && (
              <div
                className="absolute left-5 right-24 bottom-full mb-1 px-3 py-1.5 rounded-lg text-xs truncate pointer-events-none glass"
                style={{ color: '#ffffff', border: '1px solid rgba(255,255,255,0.15)' }}
              >
                {voiceInterim}
              </div>
            )}

            <div className="absolute right-2 bottom-2 flex items-center gap-1.5">
              {isVoiceSupported && (
                <button
                  onMouseDown={onVoiceStart}
                  onMouseUp={() => {
                    const transcript = onVoiceStop()
                    if (transcript.trim()) {
                      setValue('')
                      onSend(transcript.trim())
                    }
                  }}
                  onTouchStart={onVoiceStart}
                  onTouchEnd={() => {
                    const transcript = onVoiceStop()
                    if (transcript.trim()) {
                      setValue('')
                      onSend(transcript.trim())
                    }
                  }}
                  className="h-9 w-9 rounded-xl flex items-center justify-center transition-all duration-300 active:scale-90"
                  style={{
                    background: isListening ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.06)',
                    color: isListening ? '#000' : '#a0a0a8',
                    boxShadow: isListening ? '0 0 16px rgba(255,255,255,0.3)' : 'none',
                    border: isListening ? 'none' : '1px solid rgba(255,255,255,0.1)',
                  }}
                  title={isListening ? 'Release to send' : 'Hold to speak'}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                    <line x1="12" y1="19" x2="12" y2="23" />
                    <line x1="8" y1="23" x2="16" y2="23" />
                  </svg>
                </button>
              )}

              {isVoiceSupported && (
                <button
                  onClick={onCycleLanguage}
                  className="h-9 w-8 rounded-xl flex items-center justify-center transition-all duration-200 text-[10px] font-bold tracking-wider"
                  style={{
                    color: isListening ? '#fff' : '#606068',
                    border: `1px solid ${isListening ? 'rgba(255,255,255,0.25)' : 'rgba(255,255,255,0.1)'}`,
                    background: 'transparent',
                  }}
                  title={`Voice language: ${voiceLanguage}. Click to cycle.`}
                >
                  {LANG_LABELS[voiceLanguage] || 'EN'}
                </button>
              )}

              <button
                onClick={send}
                disabled={!value.trim() || loading}
                className="h-9 w-9 rounded-xl flex items-center justify-center transition-all duration-500 hover:scale-105 active:scale-95 disabled:opacity-25 disabled:hover:scale-100"
                style={{
                  background: 'linear-gradient(135deg, #e5e5e5, #ffffff)',
                  color: '#000',
                  fontWeight: 600,
                  fontSize: '16px',
                  boxShadow: value.trim() ? '0 2px 12px rgba(255,255,255,0.25)' : 'none',
                }}
              >
                {'\u2191'}
              </button>
            </div>
          </div>

          {!value.trim() && !loading && (
            <div className="flex items-center gap-1.5 px-5 pb-2 overflow-x-auto" style={{ scrollbarWidth: 'none' }}>
              {SUGGESTIONS.map(s => (
                <button
                  key={s.label}
                  onClick={() => { setValue(s.action); inputRef.current?.focus() }}
                  className="text-[11px] px-2.5 py-1 rounded-full whitespace-nowrap transition-all duration-150 active:scale-95"
                  style={{
                    color: '#777',
                    border: '1px solid rgba(255,255,255,0.06)',
                    background: 'rgba(255,255,255,0.02)',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.08)'
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'
                    e.currentTarget.style.color = '#ccc'
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.02)'
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'
                    e.currentTarget.style.color = '#777'
                  }}
                >
                  {s.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
})
