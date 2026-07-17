import { memo, useState } from 'react'
import { TypingIndicator } from './TypingIndicator'
import type { Message } from '../../types'

interface MessageBubbleProps {
  message: Message
  index: number
}

function ToolCallCard({ name, args, result }: { name: string; args: string; result: string }) {
  const [open, setOpen] = useState(false)
  const isErr = result.startsWith('{"error"')
  return (
    <div
      className="mt-2 rounded-xl text-xs font-mono overflow-hidden"
      style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left transition-colors hover:bg-[rgba(255,255,255,0.03)]"
        style={{ color: '#aaa' }}
      >
        <span style={{ color: open ? '#f59e0b' : '#666' }}>{open ? '\u25BC' : '\u25B6'}</span>
        <span style={{ color: isErr ? '#ef4444' : '#22c55e' }}>{isErr ? '\u2716' : '\u2713'}</span>
        <span className="font-medium" style={{ color: '#e5e5e5' }}>{name}</span>
        <span className="ml-auto opacity-50" style={{ color: '#888' }}>({args})</span>
      </button>
      {open && (
        <div className="px-3 pb-2 space-y-1">
          <div style={{ color: '#666' }}>args:</div>
          <div style={{ color: '#ccc', wordBreak: 'break-all' }}>{args}</div>
          <div style={{ color: '#666' }} className="mt-1">result:</div>
          <div
            style={{
              color: isErr ? '#ef4444' : '#aaa',
              wordBreak: 'break-all',
              maxHeight: 120,
              overflowY: 'auto',
            }}
          >
            {result.length > 200 ? result.slice(0, 200) + '...' : result}
          </div>
        </div>
      )}
    </div>
  )
}

function PlanDisplay({ tasks }: { tasks: string }) {
  return (
    <div
      className="mt-2 mb-3 rounded-xl px-4 py-3 text-xs"
      style={{
        background: 'rgba(245,158,11,0.06)',
        border: '1px solid rgba(245,158,11,0.12)',
      }}
    >
      <div className="mb-2 text-xs font-medium tracking-wider" style={{ color: '#f59e0b' }}>PLAN</div>
      <div className="whitespace-pre-wrap font-light leading-relaxed" style={{ color: '#999' }}>
        {tasks}
      </div>
    </div>
  )
}

export const MessageBubble = memo(function MessageBubble({ message: m, index: idx }: MessageBubbleProps) {
  return (
    <div
      className={`flex animate-fade-slide-in ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
      style={{ animationDelay: `${idx * 0.05}s` }}
    >
      {m.role === 'assistant' && (
        <div className="w-0.5 shrink-0 mr-4 rounded-full" style={{ background: 'rgba(245,158,11,0.15)' }} />
      )}
      <div
        className={`${m.role === 'user' ? 'max-w-[65%] px-4 py-3 rounded-2xl text-sm' : 'w-full text-sm leading-relaxed'}`}
        style={{
          background: m.role === 'user' ? 'rgba(245,158,11,0.1)' : 'transparent',
          color: m.role === 'user' ? '#e5e5e5' : '#ccc',
          border: m.role === 'user' ? '1px solid rgba(245,158,11,0.12)' : 'none',
          borderLeft: m.role === 'user' ? '2px solid rgba(245,158,11,0.3)' : 'none',
        }}
      >
        {m.plan && <PlanDisplay tasks={m.plan} />}
        <div className="whitespace-pre-wrap text-sm font-light leading-relaxed tracking-wide">
          {m.content}
          {m.streaming && !m.content && <TypingIndicator />}
          {m.streaming && m.content && (
            <span className="inline-block w-[1ch] animate-pulse" style={{ color: '#f59e0b' }}>\u258A</span>
          )}
        </div>
        {m.toolCalls && m.toolCalls.length > 0 && (
          <div className="mt-2 space-y-1">
            {m.toolCalls.map((tc, i) => (
              <ToolCallCard key={i} name={tc.name} args={tc.args} result={tc.result} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
})
