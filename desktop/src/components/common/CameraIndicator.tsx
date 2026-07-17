import { memo, useRef, useEffect } from 'react'

interface CameraIndicatorProps {
  stream: MediaStream | null
  active: boolean
  openness: number | null
  onToggle: () => void
}

export const CameraIndicator = memo(function CameraIndicator({ stream, active, openness, onToggle }: CameraIndicatorProps) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (videoRef.current) videoRef.current.srcObject = stream
  }, [stream])

  if (!active) return null

  return (
    <div
      className="fixed bottom-4 right-4 z-50 cursor-pointer group rounded-xl overflow-hidden transition-all duration-300 hover:scale-105 active:scale-95"
      style={{ width: 76, height: 56 }}
      onClick={onToggle}
      title="Click to disable gesture control"
    >
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover rounded-xl pointer-events-none"
        style={{ transform: 'scaleX(-1)' }}
      />
      <div
        className="absolute inset-0 rounded-xl pointer-events-none"
        style={{
          border: '1px solid rgba(255,255,255,0.1)',
          background: 'linear-gradient(to bottom, transparent 50%, rgba(0,0,0,0.4) 100%)',
        }}
      />
      <div className="absolute top-1 left-1.5 flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_4px_rgba(74,222,128,0.6)]" />
        <span className="text-[7px] font-medium tracking-widest text-white/50">CAM</span>
      </div>

      <div className="absolute bottom-1 right-1.5 flex items-center gap-1">
        <span
          className="text-[8px] font-bold tracking-wider"
          style={{ color: openness != null ? '#f59e0b' : '#444' }}
        >
          {openness != null ? (openness > 0.5 ? 'OPEN' : 'FIST') : '--'}
        </span>
      </div>
    </div>
  )
})
