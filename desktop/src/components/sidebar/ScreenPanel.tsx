import { memo, useState } from 'react'
import type { ScreenData } from '../../types'
import type { ComputerStatus, ComputerWindow } from '../../core/api'
import { getComputerSummary } from '../../core/api'
import { Skeleton } from '../common/Skeleton'

interface ScreenPanelProps {
  data: ScreenData | null
  loading?: boolean
  computerStatus?: ComputerStatus | null
  onRefreshComputer?: () => void
}

export const ScreenPanel = memo(function ScreenPanel({
  data,
  loading,
  computerStatus,
  onRefreshComputer,
}: ScreenPanelProps) {
  const [expanded, setExpanded] = useState(false)
  const [tab, setTab] = useState<'screen' | 'control'>('screen')
  const [windows, setWindows] = useState<ComputerWindow[] | null>(null)
  const [loadingWindows, setLoadingWindows] = useState(false)

  const loadWindows = async () => {
    if (windows !== null || loadingWindows) return
    setLoadingWindows(true)
    try {
      const res = await getComputerSummary()
      setWindows(res.windows ?? [])
    } catch {
      setWindows([])
    } finally {
      setLoadingWindows(false)
    }
  }

  return (
    <div className="rounded-xl overflow-hidden" style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}>
      <div className="flex items-center justify-between px-3 py-2.5">
        <div className="flex items-center gap-1">
          {(['screen', 'control'] as const).map(t => (
            <button
              key={t}
              onClick={() => { setTab(t); if (t === 'control') loadWindows() }}
              className="px-2 py-1 rounded text-[10px] font-mono tracking-wider transition-colors"
              style={{
                color: tab === t ? '#fff' : '#666',
                background: tab === t ? 'rgba(255,255,255,0.08)' : 'transparent',
              }}
            >
              {t.toUpperCase()}
            </button>
          ))}
        </div>
        <div className="text-[10px]" style={{ color: '#555' }}>
          {tab === 'screen'
            ? (loading ? 'loading…' : data ? `${data.width}x${data.height}` : 'offline')
            : (computerStatus?.mouse_keyboard && computerStatus.window_management ? 'online' : 'partial')}
          <span className="ml-2" onClick={() => setExpanded(!expanded)}>{expanded ? '\u25BC' : '\u25B6'}</span>
        </div>
      </div>

      {expanded && tab === 'screen' && loading && (
        <div className="p-2 space-y-2">
          <Skeleton width="100%" height="160px" rounded="lg" />
          <div className="flex justify-center">
            <Skeleton width="120px" height="10px" rounded="md" />
          </div>
        </div>
      )}
      {expanded && tab === 'screen' && !loading && data?.image && (
        <div className="p-2">
          <img
            src={`data:image/png;base64,${data.image}`}
            alt="Screen capture"
            className="w-full rounded-lg"
            style={{ imageRendering: 'auto', maxHeight: 320, objectFit: 'contain' }}
          />
          <div className="mt-1 text-[10px] text-center" style={{ color: '#555' }}>
            {new Date(data.timestamp * 1000).toLocaleTimeString()}
          </div>
        </div>
      )}
      {expanded && tab === 'screen' && !loading && !data && (
        <div className="text-center py-6 text-xs" style={{ color: '#555' }}>
          Backend offline
        </div>
      )}

      {expanded && tab === 'control' && (
        <div className="p-2 space-y-2">
          <div className="flex flex-wrap gap-3 text-[10px] font-mono" style={{ color: '#888' }}>
            <span>OS: {computerStatus?.platform ?? 'unknown'}</span>
            <span style={{ color: computerStatus?.mouse_keyboard ? '#9ACD9A' : '#666' }}>MOUSE/KB {computerStatus?.mouse_keyboard ? 'ON' : 'OFF'}</span>
            <span style={{ color: computerStatus?.window_management ? '#9ACD9A' : '#666' }}>WINDOWS {computerStatus?.window_management ? 'ON' : 'OFF'}</span>
            <button
              onClick={() => { setWindows(null); onRefreshComputer?.(); loadWindows() }}
              className="underline hover:text-white"
              style={{ color: '#888' }}
            >
              refresh
            </button>
          </div>
          <div className="text-[10px] font-mono tracking-wider" style={{ color: '#666' }}>OPEN WINDOWS</div>
          {loadingWindows && <Skeleton width="100%" height="40px" rounded="md" />}
          {!loadingWindows && windows !== null && windows.length === 0 && (
            <div className="text-center py-4 text-[10px]" style={{ color: '#555' }}>No windows detected (pywin32 required)</div>
          )}
          {!loadingWindows && (windows ?? []).length > 0 && (
            <div className="max-h-40 overflow-y-auto space-y-1">
              {(windows ?? []).slice(0, 20).map(w => (
                <div key={w.handle} className="flex items-center gap-2 px-2 py-1 rounded text-[11px]" style={{ background: 'rgba(255,255,255,0.03)', color: '#aaa' }}>
                  <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: '#555' }} />
                  <span className="truncate">{w.title}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
})
