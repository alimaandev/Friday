import { memo, useState } from 'react'
import type { ScreenData } from '../../types'
import { Skeleton } from '../common/Skeleton'

interface ScreenPanelProps {
  data: ScreenData | null
  loading?: boolean
}

export const ScreenPanel = memo(function ScreenPanel({ data, loading }: ScreenPanelProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-xl overflow-hidden" style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2.5 text-xs font-medium tracking-wider transition-colors hover:bg-[rgba(255,255,255,0.02)]"
        style={{ color: '#888', borderBottom: '1px solid rgba(255,255,255,0.04)' }}
      >
        <span>SCREEN</span>
        <span className="text-[10px]" style={{ color: '#555' }}>
          {loading ? 'loading…' : data ? `${data.width}x${data.height}` : 'offline'}
          <span className="ml-2">{expanded ? '\u25BC' : '\u25B6'}</span>
        </span>
      </button>
      {expanded && loading && (
        <div className="p-2 space-y-2">
          <Skeleton width="100%" height="160px" rounded="lg" />
          <div className="flex justify-center">
            <Skeleton width="120px" height="10px" rounded="md" />
          </div>
        </div>
      )}
      {expanded && !loading && data?.image && (
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
      {expanded && !loading && !data && (
        <div className="text-center py-6 text-xs" style={{ color: '#555' }}>
          Backend offline
        </div>
      )}
    </div>
  )
})
