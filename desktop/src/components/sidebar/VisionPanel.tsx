import { memo, useState } from 'react'

interface VisionResult {
  description: string
  text: string | null
  timestamp: number
}

interface VisionPanelProps {
  screenResult: VisionResult | null
  cameraResult: VisionResult | null
  onCaptureCamera: () => void
  onCaptureScreen: () => void
  analyzing: boolean
}

function formatTime(ts: number): string {
  return new Date(ts * 1000).toLocaleTimeString()
}

export const VisionPanel = memo(function VisionPanel({
  screenResult, cameraResult, onCaptureCamera, onCaptureScreen, analyzing,
}: VisionPanelProps) {
  const [expanded, setExpanded] = useState(true)

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}
    >
      <div
        className="px-3 py-2.5 text-xs font-medium tracking-wider flex items-center justify-between cursor-pointer select-none"
        style={{ color: '#888', borderBottom: '1px solid rgba(255,255,255,0.04)' }}
        onClick={() => setExpanded(e => !e)}
      >
        <span>👁 VISION</span>
        <span className="text-[10px]" style={{ color: '#666' }}>{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div className="px-2 py-2 space-y-3">
          {/* Control buttons */}
          <div className="flex gap-2 px-1">
            <button
              onClick={onCaptureScreen}
              disabled={analyzing}
              className="flex-1 text-[10px] py-1.5 rounded-lg transition-all hover:bg-white/[.05] disabled:opacity-40"
              style={{
                background: 'rgba(0,168,255,0.08)',
                border: '1px solid rgba(0,168,255,0.15)',
                color: '#00a8ff',
              }}
            >
              {analyzing ? 'Analyzing…' : '📺 Analyze Screen'}
            </button>
            <button
              onClick={onCaptureCamera}
              disabled={analyzing}
              className="flex-1 text-[10px] py-1.5 rounded-lg transition-all hover:bg-white/[.05] disabled:opacity-40"
              style={{
                background: 'rgba(124,58,237,0.08)',
                border: '1px solid rgba(124,58,237,0.15)',
                color: '#7c3aed',
              }}
            >
              {analyzing ? 'Analyzing…' : '📷 Capture Camera'}
            </button>
          </div>

          {/* Screen result */}
          {screenResult && (
            <div className="rounded-lg px-2 py-2" style={{ background: 'rgba(255,255,255,0.02)' }}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-medium tracking-wider" style={{ color: '#00a8ff' }}>SCREEN</span>
                <span className="text-[9px]" style={{ color: '#555' }}>{formatTime(screenResult.timestamp)}</span>
              </div>
              <p className="text-[11px] leading-relaxed" style={{ color: '#bbb' }}>{screenResult.description}</p>
              {screenResult.text && (
                <div className="mt-1 pt-1" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
                  <span className="text-[9px]" style={{ color: '#666' }}>OCR:</span>
                  <p className="text-[10px] font-mono mt-0.5" style={{ color: '#888' }}>{screenResult.text.slice(0, 200)}</p>
                </div>
              )}
            </div>
          )}

          {/* Camera result */}
          {cameraResult && (
            <div className="rounded-lg px-2 py-2" style={{ background: 'rgba(255,255,255,0.02)' }}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-medium tracking-wider" style={{ color: '#7c3aed' }}>CAMERA</span>
                <span className="text-[9px]" style={{ color: '#555' }}>{formatTime(cameraResult.timestamp)}</span>
              </div>
              <p className="text-[11px] leading-relaxed" style={{ color: '#bbb' }}>{cameraResult.description}</p>
              {cameraResult.text && (
                <div className="mt-1 pt-1" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
                  <span className="text-[9px]" style={{ color: '#666' }}>OCR:</span>
                  <p className="text-[10px] font-mono mt-0.5" style={{ color: '#888' }}>{cameraResult.text.slice(0, 200)}</p>
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {!screenResult && !cameraResult && (
            <div className="px-2 py-4 text-center">
              <p className="text-[11px]" style={{ color: '#555' }}>
                Capture your screen or camera to analyze.
              </p>
              <p className="text-[9px] mt-1" style={{ color: '#444' }}>
                Also try "what's on my screen" in chat.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
})