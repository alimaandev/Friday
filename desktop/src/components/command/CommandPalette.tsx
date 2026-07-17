import { useState, useEffect, useRef, useCallback } from 'react'

interface Command {
  id: string
  label: string
  action: () => void
}

interface CommandPaletteProps {
  open: boolean
  onClose: () => void
  commands: Command[]
}

export function CommandPalette({ open, onClose, commands }: CommandPaletteProps) {
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const filtered = query
    ? commands.filter(c => c.label.toLowerCase().includes(query.toLowerCase()))
    : commands

  const execute = useCallback((idx: number) => {
    const cmd = filtered[idx]
    if (cmd) {
      cmd.action()
      onClose()
    }
  }, [filtered, onClose])

  useEffect(() => {
    if (open) {
      setQuery('')
      setSelected(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  useEffect(() => {
    setSelected(0)
  }, [query])

  useEffect(() => {
    if (!open) return
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { onClose(); return }
      if (e.key === 'ArrowDown') { e.preventDefault(); setSelected(i => Math.min(i + 1, filtered.length - 1)); return }
      if (e.key === 'ArrowUp') { e.preventDefault(); setSelected(i => Math.max(i - 1, 0)); return }
      if (e.key === 'Enter') { e.preventDefault(); execute(selected); return }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [open, filtered, selected, execute, onClose])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      style={{ background: 'rgba(0,0,0,0.6)' }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl"
        style={{
          background: 'rgba(14,14,14,0.95)',
          border: '1px solid rgba(255,255,255,0.08)',
          backdropFilter: 'blur(32px)',
          WebkitBackdropFilter: 'blur(32px)',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div className="px-4 py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <input
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Type a command..."
            className="w-full bg-transparent outline-none text-sm"
            style={{ color: '#e5e5e5' }}
          />
        </div>
        <div className="max-h-64 overflow-y-auto py-1">
          {filtered.length === 0 ? (
            <div className="px-4 py-3 text-xs" style={{ color: '#666' }}>No results</div>
          ) : (
            filtered.map((cmd, i) => (
              <button
                key={cmd.id}
                onClick={() => execute(i)}
                className="w-full text-left px-4 py-2.5 text-sm transition-colors duration-75"
                style={{
                  background: i === selected ? 'rgba(245,158,11,0.12)' : 'transparent',
                  color: i === selected ? '#f59e0b' : '#bbb',
                }}
                onMouseEnter={() => setSelected(i)}
              >
                {cmd.label}
              </button>
            ))
          )}
        </div>
        <div
          className="flex items-center gap-4 px-4 py-2.5 text-[11px]"
          style={{ color: '#555', borderTop: '1px solid rgba(255,255,255,0.06)' }}
        >
          <span><kbd className="font-mono" style={{ color: '#777' }}>↑↓</kbd> navigate</span>
          <span><kbd className="font-mono" style={{ color: '#777' }}>↵</kbd> select</span>
          <span><kbd className="font-mono" style={{ color: '#777' }}>esc</kbd> close</span>
        </div>
      </div>
    </div>
  )
}
