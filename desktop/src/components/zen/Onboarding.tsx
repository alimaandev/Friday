import { memo, useEffect, useState } from 'react'

interface OnboardingProps {
  onDismiss: () => void
  onSuggest: (text: string) => void
}

const FLAGSHIP_SUGGESTIONS = [
  'Autopilot: organize my desktop and summarize',
  'Remember that my name is Tony',
  'What happened today in tech news?',
  'Set an automation to remind me to stand up hourly',
]

/**
 * P3 — "Hello, I'm Friday" first-launch onboarding. Shows once (persisted to
 * localStorage) inside zen mode: a short greeting plus flagship suggestions.
 */
export const Onboarding = memo(function Onboarding({ onDismiss, onSuggest }: OnboardingProps) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const seen = localStorage.getItem('friday_onboarded')
    if (seen === '1') setVisible(false)
  }, [])

  if (!visible) return null

  const dismiss = () => {
    try { localStorage.setItem('friday_onboarded', '1') } catch {}
    setVisible(false)
    onDismiss()
  }

  return (
    <div className="absolute inset-0 z-40 flex items-center justify-center p-6" style={{ background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(4px)' }}>
      <div className="w-[min(440px,92vw)] rounded-2xl glass animate-fade-slide-up p-6" style={{ border: '1px solid rgba(255,255,255,0.08)', boxShadow: '0 25px 60px rgba(0,0,0,0.6)' }}>
        <div className="text-center mb-4">
          <div className="text-lg font-thin tracking-[0.25em] uppercase mb-2" style={{ color: '#fff' }}>Hello, I'm Friday</div>
          <div className="text-[11px] leading-relaxed" style={{ color: '#a0a0a8' }}>
            Your desktop command center. Ask me anything, or try one of these to get started.
          </div>
        </div>

        <div className="space-y-2 mb-5">
          {FLAGSHIP_SUGGESTIONS.map(s => (
            <button
              key={s}
              onClick={() => { onSuggest(s); dismiss() }}
              className="w-full text-left px-3 py-2 rounded-lg text-[12px] transition-all duration-200 hover:bg-white/[.06]"
              style={{ color: '#ccc', border: '1px solid rgba(255,255,255,0.07)', background: 'rgba(255,255,255,0.02)' }}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="flex justify-center">
          <button
            onClick={dismiss}
            className="px-5 py-2 rounded-lg text-[12px] font-mono tracking-widest transition-all duration-200"
            style={{ color: '#a0a0a8', border: '1px solid rgba(255,255,255,0.15)', background: 'rgba(255,255,255,0.03)' }}
          >
            GET STARTED
          </button>
        </div>
      </div>
    </div>
  )
})
