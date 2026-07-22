import { memo } from 'react'
import type { EmailMessage } from '../../types'
import { Skeleton } from '../common/Skeleton'

interface EmailPanelProps {
  messages: EmailMessage[]
  unread: number
  authStatus: string
  onConnect?: () => void
}

export const EmailPanel = memo(function EmailPanel({ messages, unread, authStatus, onConnect }: EmailPanelProps) {
  const needsAuth = authStatus === 'not_authenticated' || authStatus === 'missing_credentials' || authStatus === 'needs_auth'
  return (
    <div className="rounded-xl overflow-hidden" style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}>
      <div className="px-3 py-2.5 text-xs font-medium tracking-wider flex items-center justify-between" style={{ color: '#888', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
        <span>EMAIL {unread > 0 && <span style={{ color: '#ef4444' }}>({unread})</span>}</span>
        {authStatus === 'authenticated' && <span className="text-[10px]" style={{ color: '#22c55e' }}>connected</span>}
        {authStatus === '' && <span className="text-[10px] animate-pulse" style={{ color: '#888' }}>loading...</span>}
      </div>
      {authStatus === '' ? (
        <div className="space-y-2 p-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex items-center gap-2">
              <div className="flex-1 space-y-1">
                <Skeleton width="75%" height="10px" />
                <Skeleton width="45%" height="8px" />
                <Skeleton width="60%" height="8px" />
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
            Connect Gmail
          </button>
        </div>
      ) : (
        <div className="max-h-[240px] overflow-y-auto px-1 pb-2">
          {messages.length === 0 && (
            <div className="text-center py-4 text-xs" style={{ color: '#555' }}>Inbox empty</div>
          )}
          {messages.slice(0, 8).map((msg, i) => (
            <div
              key={msg.id || i}
              className="px-2.5 py-2 mx-1 rounded-lg text-xs leading-relaxed transition-colors hover:bg-[rgba(255,255,255,0.03)]"
              style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}
            >
              <div className="flex items-center gap-2">
                <span className="font-medium truncate" style={{ color: '#ccc' }}>{msg.subject || '(no subject)'}</span>
              </div>
              <div className="mt-0.5 text-[11px]" style={{ color: '#666' }}>{msg.from}</div>
              <div className="mt-0.5 text-[11px] truncate" style={{ color: '#555' }}>{msg.snippet}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
})
