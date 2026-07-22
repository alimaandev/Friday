import { useEffect, useState } from 'react'
import type { ProactiveAlert } from '../../types'

interface AlertToastProps {
  alert: ProactiveAlert
  onDismiss: () => void
}

const SEVERITY_COLORS: Record<string, { border: string; bg: string; icon: string }> = {
  warning: { border: 'rgba(239,68,68,0.4)', bg: 'rgba(239,68,68,0.1)', icon: '\u26A0' },
  info: { border: 'rgba(212,160,64,0.3)', bg: 'rgba(212,160,64,0.08)', icon: '\u2139' },
}

export function AlertToast({ alert, onDismiss }: AlertToastProps) {
  const [visible, setVisible] = useState(false)
  const sev = SEVERITY_COLORS[alert.severity] || SEVERITY_COLORS.info

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true))
    const timer = setTimeout(() => {
      setVisible(false)
      setTimeout(onDismiss, 300)
    }, 6000)
    return () => clearTimeout(timer)
  }, [onDismiss])

  return (
    <div
      className="pointer-events-auto transition-all duration-300"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(-12px)',
      }}
    >
      <div
        className="rounded-xl px-3.5 py-2.5 text-xs backdrop-blur-sm"
        style={{
          background: sev.bg,
          border: `1px solid ${sev.border}`,
          maxWidth: '360px',
        }}
      >
        <div className="flex items-start gap-2">
          <span className="mt-0.5 shrink-0">{sev.icon}</span>
          <div className="min-w-0 flex-1">
            <div className="font-medium" style={{ color: '#e5e5e5' }}>{alert.title}</div>
            <div className="mt-0.5 leading-relaxed whitespace-pre-wrap" style={{ color: '#999' }}>{alert.description}</div>
          </div>
          <button
            onClick={() => { setVisible(false); setTimeout(onDismiss, 300) }}
            className="shrink-0 -mr-1 -mt-0.5 h-5 w-5 rounded flex items-center justify-center transition-colors hover:bg-white/[.06]"
            style={{ color: '#666' }}
          >
            {'\u2715'}
          </button>
        </div>
        {alert.action_label && (
          <button
            className="mt-1.5 px-2 py-0.5 rounded text-[10px] font-medium transition-all hover:scale-105"
            style={{ background: 'rgba(212,160,64,0.15)', color: '#D4A040' }}
          >
            {alert.action_label}
          </button>
        )}
      </div>
    </div>
  )
}
