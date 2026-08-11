import { memo, useRef, useState } from 'react'
import type { HolodeckMetrics } from './HolodeckScene'

interface HolodeckCardsProps {
  metrics: HolodeckMetrics
  gestureOpenness?: number | null
}

interface CardPos {
  x: number
  y: number
}

/**
 * Holodeck v2 — floating monochrome cards that orbit the 3D scene.
 * Each card is draggable; the whole constellation lifts/scales when a
 * hand is opened (gesture openness → z-translate), previewing Holodeck-v2
 * gesture interactions from the v4 plan.
 */
export const HolodeckCards = memo(function HolodeckCards({ metrics, gestureOpenness }: HolodeckCardsProps) {
  const [cards, setCards] = useState<Record<string, CardPos>>({
    time: { x: 14, y: 12 },
    mem: { x: 60, y: 8 },
    tool: { x: 76, y: 40 },
    cpu: { x: 26, y: 62 },
  })
  const dragRef = useRef<{ id: string; dx: number; dy: number } | null>(null)

  const openness = gestureOpenness ?? 0.5
  const lift = (openness - 0.5) * 60

  const cardDefs = [
    { id: 'time', label: 'TIME', value: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) },
    { id: 'mem', label: 'MEMORY', value: `${metrics.memory}%` },
    { id: 'tool', label: 'ACTIVE', value: metrics.tokenUsage > 0 ? `${metrics.tokenUsage} tokens` : 'idle' },
    { id: 'cpu', label: 'CPU', value: metrics.cpu != null ? `${metrics.cpu}%` : '—' },
  ]

  const onPointerDown = (e: React.PointerEvent, id: string) => {
    const pos = cards[id]
    dragRef.current = { id, dx: e.clientX - pos.x, dy: e.clientY - pos.y }
    ;(e.target as HTMLElement).setPointerCapture?.(e.pointerId)
  }

  const onPointerMove = (e: React.PointerEvent) => {
    if (!dragRef.current) return
    const { id, dx, dy } = dragRef.current
    setCards(prev => ({ ...prev, [id]: { x: e.clientX - dx, y: e.clientY - dy } }))
  }

  const onPointerUp = () => {
    dragRef.current = null
  }

  return (
    <div className="absolute inset-0 pointer-events-none" style={{ perspective: '600px' }}>
      {cardDefs.map(card => {
        const pos = cards[card.id]
        return (
          <div
            key={card.id}
            onPointerDown={e => onPointerDown(e, card.id)}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            className="absolute pointer-events-auto cursor-grab select-none rounded-lg px-2.5 py-1.5"
            style={{
              left: `${pos.x}%`,
              top: `${pos.y}%`,
              transform: `translate(-50%, -50%) translateZ(${lift}px) scale(${1 + (openness - 0.5) * 0.4})`,
              background: 'rgba(13,13,13,0.92)',
              border: '1px solid rgba(255,255,255,0.1)',
              boxShadow: `0 8px 24px rgba(0,0,0,0.5), 0 0 12px rgba(0,168,255,${0.05 + openness * 0.08})`,
              transition: 'box-shadow 200ms ease, transform 150ms ease',
            }}
          >
            <div className="text-[8px] font-mono tracking-widest" style={{ color: '#666' }}>{card.label}</div>
            <div className="text-[11px] font-mono" style={{ color: '#ddd' }}>{card.value}</div>
          </div>
        )
      })}
      {gestureOpenness != null && (
        <div className="absolute bottom-2 right-2 text-[9px]" style={{ color: '#444' }}>
          ✋ {gestureOpenness > 0.65 ? 'open' : 'closed'}
        </div>
      )}
    </div>
  )
})
