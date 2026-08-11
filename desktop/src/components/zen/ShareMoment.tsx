import { memo, useCallback, useRef } from 'react'
import type { OrbState } from '../../types'

const ORB_STATE_LABELS: Record<string, string> = {
  idle: 'IDLE',
  listening: 'LISTENING',
  thinking: 'THINKING',
  reasoning: 'REASONING',
  executing: 'EXECUTING',
  searching: 'SEARCHING',
  coding: 'CODING',
  speaking: 'SPEAKING',
  error: 'ERROR',
  offline: 'OFFLINE',
}

interface ShareMomentProps {
  open: boolean
  onClose: () => void
  orbState: OrbState
  persona: string
  message: string
  time: string
  greeting?: string
}

export const ShareMoment = memo(function ShareMoment({
  open,
  onClose,
  orbState,
  persona,
  message,
  time,
  greeting = 'FRIDAY',
}: ShareMomentProps) {
  const cardRef = useRef<HTMLDivElement>(null)

  const handleDownload = useCallback(() => {
    const card = cardRef.current
    if (!card) return
    const canvas = document.createElement('canvas')
    canvas.width = 1080
    canvas.height = 1350
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.fillStyle = '#0a0a0f'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    ctx.strokeStyle = 'rgba(255,255,255,0.08)'
    ctx.lineWidth = 2
    ctx.strokeRect(24, 24, canvas.width - 48, canvas.height - 48)

    const cx = canvas.width / 2
    ctx.fillStyle = 'rgba(255,255,255,0.9)'
    ctx.font = '400 88px Inter, sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('FRIDAY', cx, 240)

    ctx.strokeStyle = 'rgba(255,255,255,0.2)'
    ctx.lineWidth = 1.5
    ctx.beginPath()
    ctx.arc(cx, 520, 220, 0, Math.PI * 2)
    ctx.stroke()
    ctx.beginPath()
    ctx.arc(cx, 520, 140, 0, Math.PI * 2)
    ctx.stroke()

    ctx.fillStyle = 'rgba(255,255,255,0.85)'
    ctx.font = '400 40px Inter, sans-serif'
    ctx.fillText(ORB_STATE_LABELS[orbState] ?? orbState.toUpperCase(), cx, 580)

    ctx.fillStyle = 'rgba(160,160,168,1)'
    ctx.font = '400 36px Inter, sans-serif'
    const label = `${persona.toUpperCase()} · ${time}`
    ctx.fillText(label, cx, 800)

    const snippet = message.length > 120 ? message.slice(0, 120) + '…' : message
    ctx.fillStyle = 'rgba(229,229,229,1)'
    ctx.font = '400 32px Inter, sans-serif'
    const lines = snippet.split('\n').slice(0, 3)
    lines.forEach((line, i) => {
      ctx.fillText(line, cx, 880 + i * 48)
    })

    ctx.fillStyle = 'rgba(96,96,104,1)'
    ctx.font = '300 26px Inter, sans-serif'
    ctx.fillText('github.com/alimaandev/Friday', cx, 1280)

    const link = document.createElement('a')
    link.download = `friday-moment-${Date.now()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  }, [orbState, persona, message, time])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-6 animate-fade-in"
      style={{ background: 'rgba(0,0,0,0.7)' }}
      onClick={onClose}
    >
      <div className="flex flex-col items-center gap-4" onClick={e => e.stopPropagation()}>
        <div
          ref={cardRef}
          className="relative w-[320px] aspect-[4/5] rounded-2xl overflow-hidden glass animate-fade-slide-up"
          style={{ border: '1px solid rgba(255,255,255,0.1)' }}
        >
          <div className="absolute inset-0 flex flex-col items-center justify-center px-8 text-center">
            <div className="text-[40px] font-thin tracking-[0.3em] uppercase" style={{ color: '#e5e5e5' }}>
              {greeting}
            </div>
            <div
              className="mt-8 w-36 h-36 rounded-full"
              style={{
                border: `2px solid ${orbState === 'offline' ? 'rgba(255,255,255,0.15)' : 'rgba(255,255,255,0.4)'}`,
                boxShadow: orbState === 'offline' ? 'none' : '0 0 40px rgba(255,255,255,0.12)',
              }}
            />
            <div className="mt-4 text-xs tracking-[0.25em]" style={{ color: '#a0a0a8' }}>
              {ORB_STATE_LABELS[orbState] ?? orbState.toUpperCase()}
            </div>
            <div className="mt-8 text-xs" style={{ color: '#606068' }}>
              {persona.toUpperCase()} · {time}
            </div>
            {message && (
              <div className="mt-4 text-sm leading-relaxed max-h-28 overflow-y-auto" style={{ color: '#ccc' }}>
                {message}
              </div>
            )}
            <div className="mt-auto pb-6 text-[10px] tracking-widest" style={{ color: '#404048' }}>
              github.com/alimaandev/Friday
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDownload}
            className="px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 hover:scale-105 active:scale-95"
            style={{
              background: 'linear-gradient(135deg, #e5e5e5, #ffffff)',
              color: '#000',
            }}
          >
            Download PNG
          </button>
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-xl text-sm transition-all duration-200 hover:bg-white/[.06] glass"
            style={{ color: '#a0a0a8' }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
})
