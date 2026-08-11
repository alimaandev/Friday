import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrainView } from '../components/autopilot/BrainView'
import type { AutopilotRun } from '../types'

const base: AutopilotRun = {
  goal: 'build a website',
  phase: 'running',
  steps: [
    { id: 't1', description: 'Scaffold the project', tool: 'write_file', status: 'completed' },
    { id: 't2', description: 'Write index.html', tool: 'write_file', status: 'running' },
    { id: 't3', description: 'Serve the site', tool: 'run_command', status: 'pending' },
  ],
}

describe('BrainView', () => {
  it('renders nothing for idle runs', () => {
    const { container } = render(<BrainView run={null} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders one pulse node per step', () => {
    const { container } = render(<BrainView run={base} />)
    const nodes = container.querySelectorAll('.absolute.rounded-full')
    expect(nodes.length).toBe(3)
  })

  it('shows the running step description as caption', () => {
    render(<BrainView run={base} />)
    expect(screen.getByText('Write index.html')).toBeTruthy()
  })

  it('shows stats caption when done', () => {
    const done: AutopilotRun = {
      ...base,
      phase: 'done',
      stats: { total: 3, completed: 2, failed: 1, skipped: 0 },
      steps: base.steps.map(s => ({ ...s, status: 'completed' as const })),
    }
    render(<BrainView run={done} />)
    expect(screen.getByText(/2 done/)).toBeTruthy()
  })

  it('shows aborted reason', () => {
    const aborted: AutopilotRun = { ...base, phase: 'aborted', abortedReason: 'blocked by sandbox' }
    render(<BrainView run={aborted} />)
    expect(screen.getByText(/blocked by sandbox/)).toBeTruthy()
  })

  it('caps the ring at 10 nodes', () => {
    const many: AutopilotRun = {
      ...base,
      steps: Array.from({ length: 14 }, (_, i) => ({
        id: `s${i}`,
        description: `step ${i}`,
        status: 'pending' as const,
      })),
    }
    const { container } = render(<BrainView run={many} />)
    const nodes = container.querySelectorAll('.absolute.rounded-full')
    expect(nodes.length).toBe(10)
  })
})