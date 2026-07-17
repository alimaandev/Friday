import { useState, useRef, useCallback, memo } from 'react'
import { QuickActions } from './QuickActions'

interface InputBarProps {
  onSend: (text: string) => void
  loading: boolean
}

export const InputBar = memo(function InputBar({ onSend, loading }: InputBarProps) {
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

  return (
    <div className="flex justify-center px-8 pb-6 pt-3">
      <div className="w-full max-w-[720px]">
        <div
          className="rounded-2xl transition-all duration-500"
          style={{
            background: '#0D0D0D',
            border: `1px solid ${focused ? 'rgba(212,160,64,0.25)' : 'rgba(255,255,255,0.06)'}`,
            boxShadow: focused
              ? '0 8px 40px rgba(0,0,0,0.5), 0 0 60px rgba(212,160,64,0.04)'
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
              className="w-full resize-none bg-transparent outline-none text-sm leading-relaxed py-4 pl-5 pr-14 placeholder:text-neutral-600"
              style={{
                color: '#e5e5e5',
                minHeight: '56px',
                maxHeight: '160px',
                fontWeight: 350,
                letterSpacing: '0.01em',
              }}
            />

            <button
              onClick={send}
              disabled={!value.trim() || loading}
              className="absolute right-2 bottom-2 h-9 w-9 rounded-xl flex items-center justify-center transition-all duration-500 hover:scale-105 active:scale-95 disabled:opacity-25 disabled:hover:scale-100"
              style={{
                background: 'linear-gradient(135deg, #D4A040, #B8860B)',
                color: '#000',
                fontWeight: 600,
                fontSize: '16px',
                boxShadow: value.trim() ? '0 2px 12px rgba(212,160,64,0.3)' : 'none',
              }}
            >
              {'\u2191'}
            </button>
          </div>

          <QuickActions onAction={onSend} disabled={loading} />
        </div>
      </div>
    </div>
  )
})
