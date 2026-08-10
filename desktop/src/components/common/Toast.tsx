import { useEffect, useState } from 'react'
import { subscribeToasts, dismissToast, getToasts } from '../../core/ToastStore'
import type { ToastItem } from '../../core/ToastStore'

const KIND_STYLES: Record<ToastItem['kind'], { border: string; bg: string; icon: string }> = {
  success: { border: 'rgba(52,211,153,0.4)', bg: 'rgba(52,211,153,0.1)', icon: '\u2713' },
  error: { border: 'rgba(239,68,68,0.4)', bg: 'rgba(239,68,68,0.1)', icon: '\u26A0' },
  warning: { border: 'rgba(251,191,36,0.4)', bg: 'rgba(251,191,36,0.1)', icon: '\u26A0' },
  info: { border: 'rgba(59,130,246,0.4)', bg: 'rgba(59,130,246,0.1)', icon: '\u2139' },
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>(() => getToasts())

  useEffect(() => {
    const unsubscribe = subscribeToasts(list => setToasts(list))
    return () => { unsubscribe() }
  }, [])

  return (
    <div className="fixed bottom-4 right-4 z-[90] flex flex-col gap-2 pointer-events-none w-80 max-w-[calc(100vw-2rem)]">
      {toasts.map(t => {
        const s = KIND_STYLES[t.kind]
        return (
          <div
            key={t.id}
            className="rounded-xl px-3.5 py-2.5 text-xs backdrop-blur-sm flex items-start gap-2.5"
            style={{ background: s.bg, border: `1px solid ${s.border}` }}
          >
            <span className="mt-0.5 shrink-0">{s.icon}</span>
            <span className="min-w-0 flex-1 leading-relaxed" style={{ color: '#e5e5e5' }}>{t.message}</span>
            <button
              onClick={() => { dismissToast(t.id) }}
              className="shrink-0 -mr-1 -mt-0.5 h-5 w-5 rounded flex items-center justify-center transition-colors hover:bg-white/[.06]"
              style={{ color: '#666' }}
            >
              {'\u2715'}
            </button>
          </div>
        )
      })}
    </div>
  )
}