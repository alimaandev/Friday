import { memo, useState } from 'react'
import type { Automation } from '../../types'

interface AutomationSectionProps {
  automations: Automation[]
  onToggle: (id: string) => void
  onDelete: (id: string) => void
  onTrigger: (id: string) => void
}

function cronLabel(config: Record<string, any>): string {
  const cron = config.cron || ''
  if (!cron) return 'Manual'
  const parts = cron.split(' ')
  if (parts.length !== 5) return cron
  if (cron === '0 8 * * *') return 'Daily 8:00 AM'
  if (cron === '0 9 * * 1-5') return 'Weekdays 9:00 AM'
  if (parts[1] === '*' && parts[0] === '0') return 'Every hour'
  if (parts[0].startsWith('*/')) return `Every ${parts[0].slice(2)} min`
  if (parts[4] !== '*') {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    const d = parseInt(parts[4])
    if (!isNaN(d)) return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')} ${days[d] || ''}`
  }
  return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')}`
}

function actionIcon(action: string): string {
  if (action === 'notification') return '🔔'
  if (action === 'briefing') return '📋'
  if (action === 'tool_call') return '🔧'
  return '⚡'
}

export const AutomationSection = memo(function AutomationSection({
  automations, onToggle, onDelete, onTrigger,
}: AutomationSectionProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}
    >
      <div
        className="px-3 py-2.5 text-xs font-medium tracking-wider flex items-center justify-between"
        style={{ color: '#888', borderBottom: '1px solid rgba(255,255,255,0.04)' }}
      >
        <span>⏰ AUTOMATIONS</span>
        <span className="text-[10px]" style={{ color: '#666' }}>{automations.length}</span>
      </div>

      {automations.length === 0 ? (
        <div className="px-3 py-6 text-center text-[11px]" style={{ color: '#555' }}>
          No automations yet. Say "create automation" in chat.
        </div>
      ) : (
        <div className="max-h-[300px] overflow-y-auto px-1 pb-2" style={{ scrollbarWidth: 'thin' }}>
          {automations.map(auto => (
            <div key={auto.id} className="rounded-lg mx-1 my-1" style={{ background: 'rgba(255,255,255,0.02)' }}>
              <div className="flex items-center gap-2 px-2 py-2">
                <span className="text-xs shrink-0">{actionIcon(auto.action)}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-[11px] truncate" style={{ color: '#ccc' }}>{auto.name}</div>
                  <div className="text-[10px]" style={{ color: '#666' }}>{cronLabel(auto.trigger_config)}</div>
                </div>
                <button
                  onClick={() => onTrigger(auto.id)}
                  className="text-[10px] px-1.5 py-0.5 rounded transition-all hover:bg-white/[.05]"
                  style={{ color: '#888' }}
                  title="Run now"
                >
                  ▶
                </button>
                <button
                  onClick={() => setExpandedId(expandedId === auto.id ? null : auto.id)}
                  className="text-[10px] px-1.5 py-0.5 rounded transition-all hover:bg-white/[.05]"
                  style={{ color: '#666' }}
                >
                  {expandedId === auto.id ? '▲' : '▼'}
                </button>
              </div>

              {expandedId === auto.id && (
                <div className="px-2 pb-2 space-y-1">
                  <div className="flex items-center gap-2 text-[10px]" style={{ color: '#888' }}>
                    <span>Action: {auto.action}</span>
                    {auto.last_run && (
                      <span>Last: {new Date(auto.last_run * 1000).toLocaleTimeString()}</span>
                    )}
                    {auto.run_count > 0 && <span>Runs: {auto.run_count}</span>}
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onToggle(auto.id)}
                      className="relative w-8 h-4 rounded-full transition-all"
                      style={{
                        background: auto.enabled ? 'rgba(0,168,255,0.3)' : 'rgba(255,255,255,0.08)',
                        border: auto.enabled ? '1px solid rgba(0,168,255,0.4)' : '1px solid rgba(255,255,255,0.1)',
                      }}
                    >
                      <span
                        className="absolute top-0.5 w-3 h-3 rounded-full transition-all"
                        style={{
                          left: auto.enabled ? '18px' : '2px',
                          background: auto.enabled ? '#00a8ff' : '#666',
                        }}
                      />
                    </button>
                    <span className="text-[10px]" style={{ color: auto.enabled ? '#22c55e' : '#666' }}>
                      {auto.enabled ? 'Active' : 'Disabled'}
                    </span>
                    <button
                      onClick={() => onDelete(auto.id)}
                      className="ml-auto text-[10px] px-1.5 py-0.5 rounded transition-all hover:bg-white/[.05]"
                      style={{ color: '#ef4444' }}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
})