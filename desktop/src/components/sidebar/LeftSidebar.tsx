import { memo, useState, useRef } from 'react'
import type { Session } from '../../types'

interface LeftSidebarProps {
  sessions: Session[]
  activeId: string
  onSelect: (id: string) => void
  onNew: () => void
  onDelete: (id: string) => void
  onSettings: () => void
  outputDir: string
  onSetOutputDir: (path: string) => void
}

export const LeftSidebar = memo(function LeftSidebar({
  sessions, activeId, onSelect, onNew, onDelete, onSettings, outputDir, onSetOutputDir
}: LeftSidebarProps) {
  const [editing, setEditing] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSave = () => {
    const val = inputRef.current?.value.trim() || ''
    onSetOutputDir(val)
    setEditing(false)
  }

  const recentSessions = sessions.slice(-3).reverse()

  return (
    <div
      className="w-60 flex flex-col h-full shrink-0 glass"
      style={{
        borderRight: '1px solid var(--glass-border)',
      }}
    >
      <div
        className="flex items-center justify-between px-4 h-10 shrink-0"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
      >
        <span className="text-[11px] font-medium tracking-[0.2em]" style={{ color: '#666' }}>
          SESSIONS
        </span>
        <button
          onClick={onNew}
          className="w-6 h-6 flex items-center justify-center rounded-md text-sm transition-all hover:bg-white/[.04] active:scale-95"
          style={{ color: '#888' }}
        >
          +
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
        {sessions.map(s => {
          const act = s.id === activeId
          return (
            <div
              key={s.id}
              onClick={() => onSelect(s.id)}
              className="group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-all duration-150"
              style={{
                borderLeft: act ? '2px solid #D4A040' : '2px solid transparent',
                background: act ? 'rgba(212,160,64,0.06)' : 'transparent',
              }}
              onMouseEnter={e => { if (!act) e.currentTarget.style.background = 'rgba(255,255,255,0.03)' }}
              onMouseLeave={e => { if (!act) e.currentTarget.style.background = 'transparent' }}
            >
              <span className="truncate flex-1 text-sm" style={{
                color: act ? '#D4A040' : '#9E9E9E',
                fontWeight: act ? 450 : 350,
                letterSpacing: '0.01em',
              }}>
                {s.title}
              </span>
              <button
                onClick={e => { e.stopPropagation(); onDelete(s.id) }}
                className="opacity-0 group-hover:opacity-50 hover:opacity-100 transition-all duration-150 text-sm shrink-0 ml-2 w-5 h-5 flex items-center justify-center rounded hover:bg-white/[.06]"
                style={{ color: '#666' }}
              >
                ×
              </button>
            </div>
          )
        })}
      </div>

      {/* Recent conversations */}
      {recentSessions.length > 1 && (
        <div className="px-4 py-3 shrink-0" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
          <div className="text-[10px] tracking-[0.15em] mb-2" style={{ color: '#666' }}>RECENT</div>
          <div className="space-y-1">
            {recentSessions.map(s => (
              <button
                key={s.id}
                onClick={() => onSelect(s.id)}
                className="w-full text-left truncate text-[11px] px-2 py-1 rounded transition-all hover:bg-white/[.03]"
                style={{ color: s.id === activeId ? '#D4A040' : '#888' }}
              >
                {s.title}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Output folder */}
      <div className="px-4 py-3 shrink-0" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
        <div className="text-[10px] tracking-[0.15em] mb-2" style={{ color: '#666' }}>OUTPUT</div>
        {editing ? (
          <div className="flex gap-1">
            <input
              ref={inputRef}
              defaultValue={outputDir}
              className="flex-1 min-w-0 px-2 py-1 rounded text-[11px] outline-none"
              style={{ background: 'rgba(255,255,255,0.06)', color: '#ccc', border: '1px solid rgba(212,160,64,0.3)' }}
              placeholder="C:\path\to\output"
              onKeyDown={e => { if (e.key === 'Enter') handleSave(); if (e.key === 'Escape') setEditing(false) }}
              autoFocus
            />
            <button onClick={handleSave} className="px-2 py-1 rounded text-[11px]" style={{ background: 'rgba(212,160,64,0.15)', color: '#D4A040' }}>ok</button>
          </div>
        ) : (
          <button
            onClick={() => setEditing(true)}
            className="w-full text-left truncate text-[11px] px-2 py-1.5 rounded transition-all"
            style={{ color: outputDir ? '#9E9E9E' : '#555', background: 'rgba(255,255,255,0.02)' }}
            title={outputDir || 'Click to set'}
          >
            {outputDir || '+ set output folder'}
          </button>
        )}
      </div>

      <div className="px-4 py-3 flex items-center justify-between shrink-0" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
        <button onClick={onSettings} className="text-xs transition-all hover:text-white/80" style={{ color: '#666' }}>
          settings
        </button>
        <span className="text-[11px]" style={{ color: '#444' }}>v0.4</span>
      </div>
    </div>
  )
})
