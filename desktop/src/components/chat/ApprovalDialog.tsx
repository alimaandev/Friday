import type { ApprovalRequest } from '../../types'

interface ApprovalDialogProps {
  request: ApprovalRequest
  onResolve: (requestId: string, allowed: boolean) => void
}

function argSummary(args: Record<string, unknown> | undefined): string {
  if (!args) return '(no arguments)'
  const parts = Object.entries(args).map(
    ([k, v]) => `${k}=${typeof v === 'object' ? JSON.stringify(v) : String(v)}`,
  )
  return parts.join('\n') || '(no arguments)'
}

export function ApprovalDialog({ request, onResolve }: ApprovalDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div
        className="mx-4 w-full max-w-md rounded-2xl p-5"
        style={{ background: '#141416', border: '1px solid rgba(212,160,64,0.35)' }}
      >
        <div className="flex items-start gap-3">
          <div
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-lg"
            style={{ background: 'rgba(239,68,68,0.12)', color: '#EF4444' }}
          >
            {'\u26A0'}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-sm font-medium" style={{ color: '#e5e5e5' }}>
              Confirm tool call
            </div>
            <div className="mt-0.5 text-xs" style={{ color: '#999' }}>
              The assistant requested approval to run a potentially destructive action:
            </div>
          </div>
        </div>

        <div
          className="mt-4 rounded-lg px-3 py-2.5 font-mono text-xs whitespace-pre-wrap"
          style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(255,255,255,0.08)', color: '#D4A040' }}
        >
          <span style={{ color: '#e5e5e5' }}>{request.tool}</span>({'\n'}{argSummary(request.args)}{'\n'})
        </div>

        <div className="mt-5 flex justify-end gap-2.5">
          <button
            onClick={() => onResolve(request.id, false)}
            className="rounded-lg px-4 py-2 text-xs font-medium transition-colors hover:bg-white/[.06]"
            style={{ color: '#999', border: '1px solid rgba(255,255,255,0.12)' }}
          >
            Deny
          </button>
          <button
            onClick={() => onResolve(request.id, true)}
            className="rounded-lg px-4 py-2 text-xs font-medium transition-all hover:scale-105"
            style={{ background: '#D4A040', color: '#0a0a0a' }}
          >
            Allow
          </button>
        </div>
      </div>
    </div>
  )
}