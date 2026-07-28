import { memo, useRef, useEffect, useState, useCallback } from 'react'
import { HolodeckScene, HolodeckMetrics } from './HolodeckScene'

interface HolodeckPanelProps {
  metrics: HolodeckMetrics
  gesturePosition?: { x: number; y: number }
  gestureOpenness?: number
  expanded?: boolean
  onToggle?: () => void
}

export const HolodeckPanel = memo(function HolodeckPanel({
  metrics, gesturePosition, gestureOpenness, expanded = true, onToggle,
}: HolodeckPanelProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sceneRef = useRef<HolodeckScene | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [ready, setReady] = useState(false)

  // Init scene once
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const scene = new HolodeckScene(canvas)
    sceneRef.current = scene
    setReady(true)
    return () => {
      scene.dispose()
      sceneRef.current = null
    }
  }, [])

  // Resize observer
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect
      if (width > 0 && height > 0 && sceneRef.current) {
        sceneRef.current.resize(width, height)
      }
    })
    ro.observe(container)
    return () => ro.disconnect()
  }, [])

  // Update metrics
  useEffect(() => {
    if (sceneRef.current) {
      sceneRef.current.updateMetrics(metrics)
    }
  }, [metrics])

  // Update gesture
  useEffect(() => {
    if (sceneRef.current && gesturePosition) {
      sceneRef.current.updateGesture(gesturePosition.x, gestureOpenness ?? 0.5)
    }
  }, [gesturePosition, gestureOpenness])

  const handleResetView = useCallback(() => {
    // Will be reset by next render cycle
  }, [])

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}
    >
      <div
        className="px-3 py-2.5 text-xs font-medium tracking-wider flex items-center justify-between cursor-pointer select-none"
        style={{ color: '#888', borderBottom: '1px solid rgba(255,255,255,0.04)' }}
        onClick={onToggle}
      >
        <span>🌀 HOLODECK</span>
        <div className="flex items-center gap-2">
          {ready && (
            <span className="flex items-center gap-1.5" style={{ color: '#00a8ff' }}>
              <span className="inline-block w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: '#00a8ff', boxShadow: '0 0 6px #00a8ff' }} />
              <span className="text-[9px]">LIVE</span>
            </span>
          )}
          <span className="text-[10px]" style={{ color: '#666' }}>{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      {expanded && (
        <div ref={containerRef} className="relative" style={{ height: 280 }}>
          <canvas ref={canvasRef} className="w-full h-full block" />

          {/* Overlay stats */}
          <div className="absolute top-2 left-2 flex gap-2 text-[9px] font-mono" style={{ color: '#666' }}>
            <span style={{ color: '#00a8ff' }}>CPU {metrics.cpu ?? '-'}%</span>
            <span style={{ color: '#7c3aed' }}>RAM {metrics.memory}%</span>
            <span style={{ color: '#d4a040' }}>{metrics.latency}ms</span>
            <span style={{ color: '#22c55e' }}>{metrics.tokenUsage}t</span>
          </div>

          {/* Gesture hint */}
          {gesturePosition && (
            <div className="absolute bottom-2 right-2 text-[9px]" style={{ color: '#444' }}>
              ✋ gesture control active
            </div>
          )}

          {/* Empty / init overlay */}
          {!ready && (
            <div className="absolute inset-0 flex items-center justify-center text-xs" style={{ color: '#555' }}>
              Initializing Holodeck…
            </div>
          )}
        </div>
      )}
    </div>
  )
})