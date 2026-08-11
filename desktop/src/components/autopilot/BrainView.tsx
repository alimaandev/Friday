import { memo, useMemo } from 'react'
import type { AutopilotRun, AutopilotStep } from '../../types'

/* ─── Monochrome palette ─── */
const DOT_DIM = 'rgba(255,255,255,0.12)'
const DOT_ACTIVE = 'rgba(255,255,255,0.9)'
const DOT_OK = 'rgba(191,196,204,0.9)'
const DOT_FAIL = 'rgba(180,180,180,0.5)'

const STATUS_LABEL: Record<AutopilotStep['status'], string> = {
  pending: 'queued',
  running: 'working',
  completed: 'done',
  failed: 'failed',
  skipped: 'skipped',
}

function statusStyle(status: AutopilotStep['status']) {
  switch (status) {
    case 'running':
      return { dot: DOT_ACTIVE, pulse: `box-shadow: 0 0 10px 2px ${DOT_ACTIVE}` }
    case 'completed':
      return { dot: DOT_OK, pulse: '' }
    case 'failed':
      return { dot: DOT_FAIL, pulse: '' }
    default:
      return { dot: DOT_DIM, pulse: '' }
  }
}

interface BrainViewProps {
  run: AutopilotRun | null
  size?: number
}

/**
 * Minimal monochrome brain-view: a ring of pulse nodes around the orb that
 * lights up as the autopilot plans -> executes -> verifies each step.
 * Deliberately cheap (pure divs, no extra WebGL context).
 */
export const BrainView = memo(function BrainView({ run, size = 260 }: BrainViewProps) {
  const steps: AutopilotStep[] = useMemo(() => run?.steps.slice(0, 10) ?? [], [run])

  if (!run || run.phase === 'idle' || steps.length === 0) return null

  const caption =
    run.phase === 'planning'
      ? 'planning…'
      : run.phase === 'aborted'
        ? `stopped — ${run.abortedReason || 'blocked'}`
        : run.phase === 'done'
          ? (run.stats && `${run.stats.completed} done · ${run.stats.failed} failed · ${run.stats.skipped} skipped`) ||
            'complete'
          : steps.find(s => s.status === 'running')?.description || run.goal

  return (
    <div
      className="absolute inset-0 flex items-center justify-center pointer-events-none"
      style={{ zIndex: 5 }}
    >
      <div
        className="relative rounded-full"
        style={{ width: size, height: size, border: `1px solid rgba(255,255,255,0.06)` }}
      >
        {steps.map((s, i) => {
          const angle = (i / Math.max(steps.length, 1)) * Math.PI * 2 - Math.PI / 2
          const style = statusStyle(s.status)
          const isRunning = s.status === 'running'
          return (
            <div
              key={s.id + i}
              title={`${s.description} — ${STATUS_LABEL[s.status]}${s.tool ? ` via ${s.tool}` : ''}`}
              className="absolute rounded-full transition-all duration-500"
              style={{
                left: `${50 + Math.cos(angle) * 50}%`,
                top: `${50 + Math.sin(angle) * 50}%`,
                width: isRunning ? 10 : 7,
                height: isRunning ? 10 : 7,
                transform: 'translate(-50%, -50%)',
                background: style.dot,
                boxShadow: style.pulse || 'none',
                animation: isRunning ? 'brain-pulse 1.2s ease-in-out infinite' : undefined,
              }}
            />
          )
        })}
        <div
          className="absolute left-1/2 bottom-[-34px] -translate-x-1/2 text-[11px] tracking-wider truncate max-w-full px-2"
          style={{ color: 'rgba(255,255,255,0.45)' }}
        >
          {caption}
        </div>
      </div>
    </div>
  )
})