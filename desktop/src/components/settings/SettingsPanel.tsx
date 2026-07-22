import { useEffect, useRef } from 'react'

interface SettingsPanelProps {
  onClose: () => void
  voiceOutputEnabled: boolean
  onToggleVoiceOutput: () => void
  voiceLanguage: string
  onCycleLanguage: () => void
  wakeWordActive: boolean
  onToggleWakeWord: () => void
  camActive: boolean
  onToggleCamera: () => void
  backendOnline: boolean
  calendarAuth: string
  emailAuth: string
  onGoogleConnect: () => void
}

export function SettingsPanel({
  onClose,
  voiceOutputEnabled,
  onToggleVoiceOutput,
  voiceLanguage,
  onCycleLanguage,
  wakeWordActive,
  onToggleWakeWord,
  camActive,
  onToggleCamera,
  backendOnline,
  calendarAuth,
  emailAuth,
  onGoogleConnect,
}: SettingsPanelProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  const toggleRow = (label: string, enabled: boolean, onToggle: () => void) => (
    <div className="flex items-center justify-between py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
      <span className="text-sm" style={{ color: '#ccc' }}>{label}</span>
      <button
        onClick={onToggle}
        className="relative w-10 h-5 rounded-full transition-all"
        style={{
          background: enabled ? 'rgba(0,168,255,0.3)' : 'rgba(255,255,255,0.08)',
          border: enabled ? '1px solid rgba(0,168,255,0.4)' : '1px solid rgba(255,255,255,0.1)',
        }}
      >
        <span
          className="absolute top-0.5 w-3.5 h-3.5 rounded-full transition-all"
          style={{
            left: enabled ? '22px' : '3px',
            background: enabled ? '#00a8ff' : '#666',
          }}
        />
      </button>
    </div>
  )

  const statusBadge = (label: string, ok: boolean) => (
    <span
      className="inline-block px-2 py-0.5 rounded text-[11px]"
      style={{
        background: ok ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
        color: ok ? '#4ade80' : '#f87171',
      }}
    >
      {ok ? 'Connected' : 'Disconnected'}
    </span>
  )

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.6)' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div
        ref={ref}
        className="w-[420px] max-h-[80vh] overflow-y-auto rounded-2xl glass"
        style={{
          border: '1px solid var(--glass-border)',
          boxShadow: '0 25px 60px rgba(0,0,0,0.5)',
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 h-12 shrink-0" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <span className="text-sm font-medium tracking-wide" style={{ color: '#e5e5e5' }}>Settings</span>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-sm transition-all hover:bg-white/[.05]"
            style={{ color: '#888' }}
          >
            ×
          </button>
        </div>

        <div className="px-6 py-4 space-y-1">
          {/* Section: Voice */}
          <div className="text-[10px] tracking-[0.15em] py-2" style={{ color: '#555' }}>VOICE</div>
          {toggleRow('Voice Output', voiceOutputEnabled, onToggleVoiceOutput)}
          <div className="flex items-center justify-between py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
            <span className="text-sm" style={{ color: '#ccc' }}>Language</span>
            <button
              onClick={onCycleLanguage}
              className="px-3 py-1 rounded-lg text-xs transition-all hover:bg-white/[.05]"
              style={{ color: '#00a8ff', border: '1px solid rgba(0,168,255,0.2)' }}
            >
              {voiceLanguage}
            </button>
          </div>
          {toggleRow('Wake Word ("Hey Friday")', wakeWordActive, onToggleWakeWord)}

          {/* Section: Input */}
          <div className="text-[10px] tracking-[0.15em] py-2" style={{ color: '#555' }}>INPUT</div>
          {toggleRow('Gesture Control (Camera)', camActive, onToggleCamera)}

          {/* Section: Connections */}
          <div className="text-[10px] tracking-[0.15em] py-2" style={{ color: '#555' }}>CONNECTIONS</div>
          <div className="flex items-center justify-between py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
            <span className="text-sm" style={{ color: '#ccc' }}>Backend</span>
            {statusBadge('backend', backendOnline)}
          </div>
          <div className="flex items-center justify-between py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
            <span className="text-sm" style={{ color: '#ccc' }}>Google Calendar</span>
            {calendarAuth === 'authenticated' ? (
              statusBadge('calendar', true)
            ) : (
              <button
                onClick={onGoogleConnect}
                className="px-3 py-1 rounded-lg text-xs transition-all hover:bg-white/[.05]"
                style={{ color: '#00a8ff', border: '1px solid rgba(0,168,255,0.2)' }}
              >
                Connect
              </button>
            )}
          </div>
          <div className="flex items-center justify-between py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
            <span className="text-sm" style={{ color: '#ccc' }}>Google Email</span>
            {emailAuth === 'authenticated' ? (
              statusBadge('email', true)
            ) : (
              <button
                onClick={onGoogleConnect}
                className="px-3 py-1 rounded-lg text-xs transition-all hover:bg-white/[.05]"
                style={{ color: '#00a8ff', border: '1px solid rgba(0,168,255,0.2)' }}
              >
                Connect
              </button>
            )}
          </div>

          {/* Section: About */}
          <div className="text-[10px] tracking-[0.15em] py-2" style={{ color: '#555' }}>ABOUT</div>
          <div className="flex items-center justify-between py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
            <span className="text-sm" style={{ color: '#ccc' }}>Theme</span>
            <span className="text-xs" style={{ color: '#888' }}>Dark</span>
          </div>
          <div className="flex items-center justify-between py-3">
            <span className="text-sm" style={{ color: '#ccc' }}>Version</span>
            <span className="text-xs" style={{ color: '#666' }}>0.4</span>
          </div>
        </div>
      </div>
    </div>
  )
}