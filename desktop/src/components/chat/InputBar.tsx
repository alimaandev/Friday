import { useState, useRef, useCallback, useMemo, memo } from 'react'
import { QuickActions } from './QuickActions'

const LANG_LABELS: Record<string, string> = { 'en-US': 'EN', 'hi-IN': 'HI', 'ur-PK': 'UR' }

const SUGGESTIONS = [
  { label: 'Explain', action: 'Explain this concept in simple terms' },
  { label: 'Search', action: 'Search the web for' },
  { label: 'Code', action: 'Write code to' },
  { label: 'Summarize', action: 'Summarize the key points about' },
]

interface InputBarProps {
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

export const InputBar = memo(function InputBar({
  onSend, loading, onVoiceStart, onVoiceStop, voiceStatus, voiceInterim, isVoiceSupported,
  voiceLanguage, onCycleLanguage,
}: InputBarProps) {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const send = useCallback(() => {
    const text = value.trim()
    if (text && !loading) {
      setValue('')
      onSend(text)
    }
  }, [value, loading, onSend])

  const handleFilePick = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const text = reader.result as string
      const header = `[File: ${file.name}]\n\`\`\`\n${text}\n\`\`\`\n\n`
      setValue(v => v + header)
      if (inputRef.current) {
        inputRef.current.focus()
        inputRef.current.selectionStart = inputRef.current.selectionEnd = inputRef.current.value.length
      }
    }
    reader.readAsText(file)
    e.target.value = ''
  }, [])

  const isListening = voiceStatus === 'listening'
  const borderColor = isListening ? 'rgba(245,158,11,0.4)' : focused ? 'rgba(245,158,11,0.2)' : 'var(--glass-border)'

  return (
    <div className="flex justify-center px-8 pb-6 pt-3">
      <div className="w-full max-w-[720px]">
        <div
          className="rounded-2xl transition-all duration-300 glass"
          style={{
            border: `1px solid ${borderColor}`,
            boxShadow: isListening
              ? '0 8px 40px rgba(0,0,0,0.5), 0 0 60px rgba(245,158,11,0.06)'
              : focused
                ? '0 8px 40px rgba(0,0,0,0.5), 0 0 40px rgba(245,158,11,0.03)'
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
                className="absolute left-5 right-24 bottom-full mb-1 px-3 py-1.5 rounded-lg text-xs truncate pointer-events-none glass blue-border"
                style={{ color: 'var(--blue-bright)' }}
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
                    background: isListening
                      ? 'linear-gradient(135deg, #ef4444, #dc2626)'
                      : 'var(--surface)',
                    color: isListening ? '#fff' : '#a0a0a8',
                    boxShadow: isListening ? '0 0 16px rgba(239,68,68,0.3)' : 'none',
                    border: isListening ? 'none' : '1px solid var(--glass-border)',
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
                    color: isListening ? 'var(--gold)' : '#606068',
                    border: `1px solid ${isListening ? 'rgba(245,158,11,0.25)' : 'var(--glass-border)'}`,
                    background: 'transparent',
                  }}
                  title={`Voice language: ${voiceLanguage}. Click to cycle.`}
                >
                  {LANG_LABELS[voiceLanguage] || 'EN'}
                </button>
              )}

              <input
                ref={fileRef}
                type="file"
                accept=".txt,.md,.json,.csv,.py,.js,.ts,.jsx,.tsx,.html,.css,.yaml,.yml,.xml,.sh,.env,.toml,.ini,.cfg,.log"
                onChange={handleFilePick}
                style={{ display: 'none' }}
              />
              <button
                onClick={() => fileRef.current?.click()}
                className="h-9 w-9 rounded-xl flex items-center justify-center transition-all duration-200 active:scale-90"
                style={{
                  background: 'var(--surface)',
                  color: '#a0a0a8',
                  border: '1px solid var(--glass-border)',
                }}
                title="Attach file"
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
                </svg>
              </button>

              <button
                onClick={send}
                disabled={!value.trim() || loading}
                className="h-9 w-9 rounded-xl flex items-center justify-center transition-all duration-500 hover:scale-105 active:scale-95 disabled:opacity-25 disabled:hover:scale-100"
                style={{
                  background: 'linear-gradient(135deg, var(--blue), var(--blue-bright))',
                  color: '#000',
                  fontWeight: 600,
                  fontSize: '16px',
                  boxShadow: value.trim() ? '0 2px 12px var(--blue-glow)' : 'none',
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
                    e.currentTarget.style.background = 'rgba(245,158,11,0.08)'
                    e.currentTarget.style.borderColor = 'rgba(245,158,11,0.2)'
                    e.currentTarget.style.color = '#f59e0b'
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
          <QuickActions onAction={onSend} disabled={loading} />
        </div>
      </div>
    </div>
  )
})
