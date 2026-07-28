import { memo, useState, useEffect } from 'react'
import type { SystemInfo } from '../../types'

interface StatusRibbonProps {
  systemInfo: SystemInfo
  latency: number
  orbState: string
  memory: number
  backendOnline: boolean
  onCommandPalette: () => void
  voiceOutputEnabled: boolean
  onToggleVoiceOutput: () => void
  voiceInputStatus: string
  voiceOutputStatus: string
  ambientActive?: boolean
  onExitAmbient?: () => void
  persona?: string
}

const ORB_LABELS: Record<string, string> = {
  idle: 'Idle',
  listening: 'Listening',
  thinking: 'Thinking',
  reasoning: 'Reasoning',
  executing: 'Executing',
  searching: 'Searching',
  coding: 'Coding',
  speaking: 'Speaking',
  error: 'Error',
  offline: 'Offline',
}

export const StatusRibbon = memo(function StatusRibbon({
  systemInfo, latency, orbState, memory, backendOnline, onCommandPalette,
  voiceOutputEnabled, onToggleVoiceOutput, voiceInputStatus, voiceOutputStatus,
  ambientActive, onExitAmbient, persona,
}: StatusRibbonProps) {
  const [time, setTime] = useState('')
  useEffect(() => {
    const update = () => setTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }))
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [])

  const model = systemInfo.model || '-'
  const uptime = `${Math.round(systemInfo.uptime_seconds / 60)}m`
  const cpu = `${systemInfo.cpu_cores}c`

  return (
    <div
      className="h-9 flex items-center gap-3 px-4 shrink-0 overflow-x-auto text-[11px]"
      style={{
        background: 'var(--glass)',
        borderBottom: '1px solid var(--glass-border)',
        scrollbarWidth: 'none',
        color: '#a0a0a8',
      }}
    >
      <span className="font-mono shrink-0 tracking-wider" style={{ color: '#ccc' }}>{time}</span>

      <span className="w-px h-3 rounded-full shrink-0" style={{ background: 'var(--glass-border)' }} />

      <span className="flex items-center gap-1.5 shrink-0">
        <span
          className={`inline-block w-1.5 h-1.5 rounded-full ${backendOnline ? 'animate-pulse-glow' : ''}`}
          style={{
            background: backendOnline ? 'var(--blue)' : '#ef4444',
            boxShadow: backendOnline ? '0 0 8px var(--blue-glow)' : 'none',
          }}
        />
        <span style={{ color: backendOnline ? 'var(--blue)' : '#ef4444' }}>
          {backendOnline ? 'ONLINE' : 'OFFLINE'}
        </span>
      </span>

      <span className="w-px h-3 rounded-full shrink-0" style={{ background: 'var(--glass-border)' }} />

      <span className="shrink-0">
        <span style={{ color: '#ccc' }}>{model}</span>
        <span className="mx-1.5" style={{ color: '#606068' }}>·</span>
        <span>{latency}ms</span>
        <span className="mx-1.5" style={{ color: '#606068' }}>·</span>
        <span>{memory}% RAM</span>
        <span className="mx-1.5" style={{ color: '#606068' }}>·</span>
        <span>{cpu} · {uptime}</span>
      </span>

      <span className="w-px h-3 rounded-full shrink-0" style={{ background: 'var(--glass-border)' }} />

      <span className="shrink-0" style={{ color: '#606068' }}>{ORB_LABELS[orbState] ?? orbState.toUpperCase()}</span>

      {persona && (
        <span className="shrink-0 text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded" style={{ color: '#00a8ff', background: 'rgba(0,168,255,0.08)', border: '1px solid rgba(0,168,255,0.15)' }}>
          {persona}
        </span>
      )}

      <div className="flex-1" />

      {/* Ambient mode indicator */}
      {ambientActive && (
        <span className="flex items-center gap-1.5 shrink-0 mr-2">
          <span
            className="inline-block w-1.5 h-1.5 rounded-full animate-pulse"
            style={{
              background: voiceInputStatus === 'listening' ? '#22c55e' : '#00a8ff',
              boxShadow: voiceInputStatus === 'listening'
                ? '0 0 8px rgba(34,197,94,0.5)'
                : '0 0 8px var(--blue-glow)',
            }}
          />
          <span className="text-[10px]" style={{ color: voiceInputStatus === 'listening' ? '#22c55e' : 'var(--blue)' }}>
            {voiceInputStatus === 'listening' ? 'AMBIENT' : voiceOutputStatus === 'speaking' ? 'SPEAKING' : 'AWAITING'}
          </span>
          {onExitAmbient && (
            <button
              onClick={onExitAmbient}
              className="ml-1 text-[10px] transition-all hover:bg-white/[.04] px-1.5 py-0.5 rounded"
              style={{ color: '#606068' }}
              title="Exit ambient mode"
            >
              ✕
            </button>
          )}
        </span>
      )}

      {/* Legacy voice indicator (hidden during ambient mode) */}
      {!ambientActive && (voiceInputStatus === 'listening' || voiceOutputStatus === 'speaking') && (
        <span className="flex items-center gap-1.5 shrink-0 mr-2">
          <span
            className="inline-block w-1.5 h-1.5 rounded-full animate-pulse"
            style={{
              background: voiceInputStatus === 'listening' ? '#ef4444' : 'var(--blue)',
              boxShadow: voiceInputStatus === 'listening'
                ? '0 0 8px rgba(239,68,68,0.5)'
                : '0 0 8px var(--blue-glow)',
            }}
          />
          <span className="text-[10px]" style={{ color: voiceInputStatus === 'listening' ? '#ef4444' : 'var(--blue)' }}>
            {voiceInputStatus === 'listening' ? 'LISTENING' : 'SPEAKING'}
          </span>
        </span>
      )}

      <button
        onClick={onToggleVoiceOutput}
        className="flex items-center gap-1 shrink-0 transition-all hover:bg-white/[.04] px-2 py-0.5 rounded"
        style={{ color: voiceOutputEnabled ? 'var(--gold)' : '#606068' }}
        title={voiceOutputEnabled ? 'Mute voice output' : 'Enable voice output'}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          {voiceOutputEnabled ? (
            <>
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
            </>
          ) : (
            <>
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
              <line x1="23" y1="9" x2="17" y2="15" />
              <line x1="17" y1="9" x2="23" y2="15" />
            </>
          )}
        </svg>
      </button>

      <button
        onClick={onCommandPalette}
        className="flex items-center gap-1 shrink-0 transition-all hover:bg-white/[.04] px-2 py-0.5 rounded"
        style={{ color: '#606068' }}
      >
        <span className="font-mono text-[10px]">⌘</span>
        <span className="text-[10px]">cmd</span>
      </button>
    </div>
  )
})