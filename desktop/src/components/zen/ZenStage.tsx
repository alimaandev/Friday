import { memo, useRef, useEffect } from 'react'
import type { Message, OrbState, AutopilotRun } from '../../types'
import { OrbCore } from './OrbCore'
import { ZenInput } from './ZenInput'
import { MessageBubble } from '../chat/MessageBubble'
import { BrainView } from '../autopilot/BrainView'

interface ZenStageProps {
  orbState: OrbState
  metrics: { latency: number; model: string; provider: string; memory: number; tokenUsage: number }
  messages: Message[]
  autopilotRun: AutopilotRun | null
  onSend: (text: string) => void
  onStop: () => void
  onRegenerate: () => void
  loading: boolean
  voiceInputSupported: boolean
  voiceStatus: 'idle' | 'listening' | 'error'
  voiceInterim: string
  voiceLanguage: string
  onVoiceStart: () => void
  onVoiceStop: () => string
  onCycleLanguage: () => void
  onToggleDashboard: () => void
  handsFree?: boolean
  ambientActive?: boolean
  onToggleHandsFree?: () => void
  temperature?: number | null
  location?: string
  time?: string
  handPosition?: { x: number; y: number } | null
  voiceActivity?: boolean
}

export const ZenStage = memo(function ZenStage({
  orbState,
  metrics,
  messages,
  autopilotRun,
  onSend,
  onStop,
  onRegenerate,
  loading,
  voiceInputSupported,
  voiceStatus,
  voiceInterim,
  voiceLanguage,
  onVoiceStart,
  onVoiceStop,
  onCycleLanguage,
  onToggleDashboard,
  handsFree = false,
  ambientActive = false,
  onToggleHandsFree,
  temperature = null,
  location = '',
  time = '',
  handPosition = null,
  voiceActivity = false,
}: ZenStageProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const lastContent = messages[messages.length - 1]?.content

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, lastContent])

  return (
    <div className="relative flex flex-col h-full">
      {/* Minimal monochrome top strip */}
      <div className="flex items-center justify-between px-6 py-3 shrink-0 select-none">
        <div className="flex items-center gap-2">
          <span className="text-[13px] font-thin tracking-[0.3em] uppercase" style={{ color: '#a0a0a8' }}>
            Friday
          </span>
          {ambientActive && (
            <span
              className="text-[9px] font-mono tracking-widest px-1.5 py-0.5 rounded animate-fade-in"
              style={{ color: '#fff', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.15)' }}
            >
              AMBIENT
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {onToggleHandsFree && voiceInputSupported && (
            <button
              onClick={onToggleHandsFree}
              className="flex items-center gap-1.5 text-[10px] font-mono tracking-widest px-2.5 py-1 rounded-md transition-all duration-200 hover:bg-white/[.06]"
              style={{
                color: handsFree ? '#000' : '#606068',
                background: handsFree ? 'rgba(255,255,255,0.95)' : 'transparent',
                border: `1px solid ${handsFree ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.08)'}`,
                boxShadow: handsFree ? '0 0 12px rgba(255,255,255,0.25)' : 'none',
              }}
              title={handsFree ? 'Hands-free listening on — click to disable' : 'Hands-free listening off — click to enable (auto-speaks replies)'}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="23" />
              </svg>
              {handsFree ? 'HANDS-FREE' : 'LISTEN'}
            </button>
          )}
          <button
            onClick={onToggleDashboard}
            className="text-[10px] font-mono tracking-widest px-2 py-1 rounded-md transition-all duration-200 hover:bg-white/[.04]"
            style={{ color: '#606068' }}
            title="Toggle dashboard (⌘B)"
          >
            {location ? `${location} · ` : ''}⌘B
          </button>
        </div>
      </div>

      {/* Orb — always full-size, owns the stage */}
      <div className="relative flex-1 flex items-center justify-center px-8 min-h-0">
        <OrbCore
          orbState={orbState}
          temperature={temperature}
          location={location}
          time={time}
          memory={metrics.memory}
          model={metrics.model}
          latency={metrics.latency}
          handPosition={handPosition}
          voiceActivity={voiceActivity}
        />
        {autopilotRun && (
          <div className="absolute inset-0 flex items-center justify-center">
            <BrainView run={autopilotRun} size={320} />
          </div>
        )}
      </div>

      {/* Chat below the orb */}
      {messages.length > 0 && (
        <div className="w-full max-w-[720px] mx-auto flex-1 min-h-0 overflow-y-auto space-y-6 px-8 pb-4">
          {messages.map((m, idx) => (
            <MessageBubble
              key={m.id}
              message={m}
              index={idx}
              onRegenerate={m.role === 'assistant' && !m.streaming ? onRegenerate : undefined}
              onStop={m.role === 'assistant' && m.streaming ? onStop : undefined}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
      )}

      <ZenInput
        onSend={onSend}
        loading={loading}
        onVoiceStart={onVoiceStart}
        onVoiceStop={onVoiceStop}
        voiceStatus={voiceStatus}
        voiceInterim={voiceInterim}
        isVoiceSupported={voiceInputSupported}
        voiceLanguage={voiceLanguage}
        onCycleLanguage={onCycleLanguage}
      />
    </div>
  )
})
