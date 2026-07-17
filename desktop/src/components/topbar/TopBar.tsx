import { memo, useState, useEffect } from 'react'
import type { SystemInfo } from '../../types'

interface StatusRibbonProps {
  systemInfo: SystemInfo
  latency: number
  orbState: string
  memory: number
  backendOnline: boolean
  onCommandPalette: () => void
}

export const StatusRibbon = memo(function StatusRibbon({
  systemInfo, latency, orbState, memory, backendOnline, onCommandPalette,
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
        background: '#0D0D0D',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        scrollbarWidth: 'none',
        color: '#9E9E9E',
      }}
    >
      {/* Time */}
      <span className="font-mono shrink-0 tracking-wider" style={{ color: '#ccc' }}>{time}</span>

      <span className="w-px h-3 rounded-full shrink-0" style={{ background: 'rgba(255,255,255,0.06)' }} />

      {/* Online status */}
      <span className="flex items-center gap-1.5 shrink-0">
        <span
          className={`inline-block w-1.5 h-1.5 rounded-full ${backendOnline ? 'animate-pulse-glow' : ''}`}
          style={{
            background: backendOnline ? '#D4A040' : '#ef4444',
            boxShadow: backendOnline ? '0 0 6px rgba(212,160,64,0.4)' : 'none',
          }}
        />
        <span style={{ color: backendOnline ? '#D4A040' : '#ef4444' }}>
          {backendOnline ? 'ONLINE' : 'OFFLINE'}
        </span>
      </span>

      <span className="w-px h-3 rounded-full shrink-0" style={{ background: 'rgba(255,255,255,0.06)' }} />

      {/* Model & latency */}
      <span className="shrink-0">
        <span style={{ color: '#ccc' }}>{model}</span>
        <span className="mx-1.5" style={{ color: '#666' }}>·</span>
        <span>{latency}ms</span>
        <span className="mx-1.5" style={{ color: '#666' }}>·</span>
        <span>{memory}% RAM</span>
        <span className="mx-1.5" style={{ color: '#666' }}>·</span>
        <span>{cpu} · {uptime}</span>
      </span>

      <span className="w-px h-3 rounded-full shrink-0" style={{ background: 'rgba(255,255,255,0.06)' }} />

      {/* Orb state */}
      <span className="shrink-0" style={{ color: '#888' }}>{orbState.toUpperCase()}</span>

      <div className="flex-1" />

      <button
        onClick={onCommandPalette}
        className="flex items-center gap-1 shrink-0 transition-all hover:bg-white/[.04] px-2 py-0.5 rounded"
        style={{ color: '#666' }}
      >
        <span className="font-mono text-[10px]">⌘</span>
        <span className="text-[10px]">cmd</span>
      </button>
    </div>
  )
})
