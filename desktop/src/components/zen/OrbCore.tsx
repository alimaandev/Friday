import { memo } from 'react'
import type { OrbState } from '../../types'
import { JarvisOrb } from '../center/AiCore'

/* ─── Zen monochrome palette ─── */
const C_TEXT = '#e5e5e5'
const C_SECONDARY = '#a0a0a8'
const C_TERTIARY = '#606068'

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

interface AmbientChip {
  id: string
  label: string
  value: string
  position: { top: string; left: string }
  delay: number
}

interface OrbCoreProps {
  orbState: OrbState
  handPosition?: { x: number; y: number } | null
  voiceActivity?: boolean
  temperature?: number | null
  location?: string
  memory?: number
  model?: string
  latency?: number
  time?: string
}

export const OrbCore = memo(function OrbCore({
  orbState,
  handPosition = null,
  voiceActivity = false,
  temperature = null,
  location = '',
  memory = 0,
  model = '',
  latency = 0,
  time = '',
}: OrbCoreProps) {
  const isOnline = orbState !== 'offline'

  const chips: AmbientChip[] = [
    temperature != null
      ? { id: 'temp', label: 'TEMP', value: `${Math.round(temperature)}°C`, position: { top: '6%', left: '12%' }, delay: 0 }
      : null,
    time ? { id: 'time', label: 'TIME', value: time, position: { top: '18%', left: '84%' }, delay: 0.8 } : null,
    model ? { id: 'model', label: 'MODEL', value: model, position: { top: '72%', left: '10%' }, delay: 1.6 } : null,
    memory > 0 ? { id: 'mem', label: 'MEMORY', value: `${memory}`, position: { top: '78%', left: '80%' }, delay: 2.4 } : null,
  ].filter(Boolean) as AmbientChip[]

  return (
    <div className="relative flex items-center justify-center w-full h-full" style={{ zIndex: 1 }}>
      <div className="absolute inset-0 pointer-events-none">
        <JarvisOrb orbState={orbState} handPosition={handPosition} voiceActivity={voiceActivity} />
      </div>

      <div
        className="relative flex items-center gap-2 px-3 py-1.5 rounded-full glass animate-fade-in"
        style={{ border: '1px solid rgba(255,255,255,0.08)' }}
      >
        <span
          className={`inline-block w-1.5 h-1.5 rounded-full ${isOnline ? 'animate-pulse-glow' : ''}`}
          style={{
            background: isOnline ? '#ffffff' : C_TERTIARY,
            boxShadow: isOnline ? '0 0 8px rgba(255,255,255,0.5)' : 'none',
          }}
        />
        <span className="text-[11px] tracking-[0.2em]" style={{ color: isOnline ? C_TEXT : C_TERTIARY }}>
          {isOnline ? (ORB_STATE_LABELS[orbState] ?? orbState.toUpperCase()) : 'OFFLINE'}
        </span>
        {location && <span className="text-[10px] uppercase tracking-widest" style={{ color: C_TERTIARY }}>{location}</span>}
      </div>

      {chips.map(chip => (
        <div
          key={chip.id}
          className="absolute flex items-center gap-1.5 px-2.5 py-1 rounded-md glass cursor-pointer transition-all duration-300 hover:scale-110 animate-fade-slide-up"
          style={{
            top: chip.position.top,
            left: chip.position.left,
            border: '1px solid rgba(255,255,255,0.06)',
            animationDelay: `${chip.delay}s`,
          }}
          title={`${chip.label}: ${chip.value}`}
        >
          <span className="text-[9px] tracking-[0.15em]" style={{ color: C_TERTIARY }}>{chip.label}</span>
          <span className="text-[11px] font-mono" style={{ color: C_SECONDARY }}>{chip.value}</span>
        </div>
      ))}

      {latency > 0 && (
        <div
          className="absolute bottom-[6%] left-1/2 -translate-x-1/2 px-2 py-0.5 rounded glass animate-fade-slide-up"
          style={{ border: '1px solid rgba(255,255,255,0.05)', animationDelay: '3s' }}
        >
          <span className="text-[9px] font-mono tracking-widest" style={{ color: C_TERTIARY }}>
            {latency}MS
          </span>
        </div>
      )}
    </div>
  )
})
