import { memo } from 'react'
import type { CalendarEvent } from '../../types'
import { Skeleton } from '../common/Skeleton'

interface CalendarPanelProps {
  events: CalendarEvent[]
  authStatus: string
  onConnect?: () => void
}

export const CalendarPanel = memo(function CalendarPanel({ events, authStatus, onConnect }: CalendarPanelProps) {
  const needsAuth = authStatus === 'not_authenticated' || authStatus === 'missing_credentials' || authStatus === 'needs_auth'
  return (
    <div className="rounded-xl overflow-hidden" style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}>
      <div className="px-3 py-2.5 text-xs font-medium tracking-wider flex items-center justify-between" style={{ color: '#888', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
        <span>CALENDAR</span>
        {authStatus === 'authenticated' && <span className="text-[10px]" style={{ color: '#22c55e' }}>connected</span>}
        {authStatus === '' && <span className="text-[10px] animate-pulse" style={{ color: '#888' }}>loading...</span>}
      </div>
      {authStatus === '' ? (
        <div className="space-y-2 p-3">
          {[1, 2].map(i => (
            <div key={i} className="flex items-center gap-2">
              <div className="flex-1 space-y-1">
                <Skeleton width="70%" height="10px" />
                <Skeleton width="50%" height="8px" />
              </div>
            </div>
          ))}
        </div>
      ) : needsAuth ? (
        <div className="text-center py-4 text-xs" style={{ color: '#555' }}>
          <button
            onClick={onConnect}
            className="underline cursor-pointer"
            style={{ color: '#D4A040', background: 'none', border: 'none', fontSize: 'inherit' }}
          >
            Connect Google Calendar
          </button>
        </div>
      ) : (
        <div className="max-h-[200px] overflow-y-auto px-1 pb-2">
          {events.length === 0 && (
            <div className="text-center py-4 text-xs" style={{ color: '#555' }}>No upcoming events</div>
          )}
          {events.slice(0, 8).map((ev, i) => (
            <div
              key={i}
              className="px-2.5 py-2 mx-1 rounded-lg text-xs leading-relaxed transition-colors hover:bg-[rgba(255,255,255,0.03)]"
              style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}
            >
              <div className="font-medium truncate" style={{ color: '#ccc' }}>{ev.summary}</div>
              <div className="mt-0.5 text-[11px] flex items-center gap-2" style={{ color: '#666' }}>
                <span>{new Date(ev.start).toLocaleDateString()} {new Date(ev.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                {ev.location && <span className="truncate">{ev.location}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
})
