import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ShareMoment } from '../components/zen/ShareMoment'

const baseProps = {
  open: true,
  onClose: vi.fn(),
  orbState: 'thinking' as const,
  persona: 'friday',
  message: 'Scanning the datacore, sir.',
  time: '11:59:00',
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ShareMoment', () => {
  it('renders nothing when closed', () => {
    render(<ShareMoment {...baseProps} open={false} />)
    expect(screen.queryByText('FRIDAY')).toBeNull()
  })

  it('renders greeting, state, persona, and message', () => {
    render(<ShareMoment {...baseProps} />)
    expect(screen.getByText('FRIDAY')).toBeTruthy()
    expect(screen.getByText('THINKING')).toBeTruthy()
    expect(screen.getByText(/FRIDAY · 11:59:00/)).toBeTruthy()
    expect(screen.getByText('Scanning the datacore, sir.')).toBeTruthy()
    expect(screen.getByText(/github.com\/alimaandev\/Friday/)).toBeTruthy()
  })

  it('closes via the close button', () => {
    render(<ShareMoment {...baseProps} />)
    fireEvent.click(screen.getByText('Close'))
    expect(baseProps.onClose).toHaveBeenCalled()
  })

  it('triggers a PNG download', () => {
    const click = vi.fn()
    Object.defineProperty(HTMLAnchorElement.prototype, 'click', { configurable: true, value: click })
    const ctxStub = {
      fillStyle: '', strokeStyle: '', lineWidth: 0, font: '', textAlign: '',
      fillRect: vi.fn(), strokeRect: vi.fn(), fillText: vi.fn(), stroke: vi.fn(),
      beginPath: vi.fn(), arc: vi.fn(),
    } as any
    Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
      configurable: true,
      value: vi.fn(() => ctxStub),
    })
    render(<ShareMoment {...baseProps} />)
    fireEvent.click(screen.getByText('Download PNG'))
    expect(click).toHaveBeenCalled()
  })
})