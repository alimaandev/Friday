import { memo } from 'react'

interface Briefing {
  summary: string
  sections: string[]
  greeting: string
  yesterday?: string
}

interface BriefingCardProps {
  briefing: Briefing | null
  onPlay: () => void
  voiceOutputEnabled: boolean
}

export const BriefingCard = memo(function BriefingCard({ briefing, onPlay, voiceOutputEnabled }: BriefingCardProps) {
  if (!briefing) return null

  return (
    <div
      className="col-span-2 rounded-xl p-4 mb-2 animate-slide-in-up"
      style={{
        background: 'rgba(0,168,255,0.04)',
        border: '1px solid rgba(0,168,255,0.12)',
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-[11px] font-medium mb-2" style={{ color: '#00a8ff' }}>
            <span>☕</span>
            <span>MORNING BRIEFING</span>
          </div>
          <p className="text-xs leading-relaxed" style={{ color: '#d0d0d0' }}>
            {briefing.summary}
          </p>
          {briefing.yesterday && (
            <div className="mt-2 text-[11px] leading-relaxed" style={{ color: '#8a8a92', borderTop: '1px solid rgba(0,168,255,0.1)', paddingTop: '6px' }}>
              <span style={{ color: '#00a8ff' }}>📖 From yesterday's diary:</span>
              <span className="line-clamp-3 inline"> {briefing.yesterday}</span>
            </div>
          )}
        </div>
        {voiceOutputEnabled && (
          <button
            onClick={onPlay}
            className="shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-all hover:scale-105 active:scale-95"
            style={{
              background: 'rgba(0,168,255,0.1)',
              border: '1px solid rgba(0,168,255,0.2)',
              color: '#33ccff',
            }}
            title="Play briefing aloud"
          >
            ▶ Play
          </button>
        )}
      </div>
    </div>
  )
})