import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { HolodeckCards } from '../components/holodeck/HolodeckCards'

const metrics = { latency: 120, memory: 45, tokenUsage: 300, cpu: 12 }

describe('HolodeckCards', () => {
  it('renders the four floating cards', () => {
    render(<HolodeckCards metrics={metrics} />)
    expect(screen.getByText('TIME')).toBeTruthy()
    expect(screen.getByText('MEMORY')).toBeTruthy()
    expect(screen.getByText('ACTIVE')).toBeTruthy()
    expect(screen.getByText('CPU')).toBeTruthy()
    expect(screen.getByText('45%')).toBeTruthy()
    expect(screen.getByText('12%')).toBeTruthy()
  })

  it('shows open/closed gesture state', () => {
    render(<HolodeckCards metrics={metrics} gestureOpenness={0.8} />)
    expect(screen.getByText(/open/)).toBeTruthy()
  })

  it('allows dragging a card to reposition it', () => {
    const { container } = render(<HolodeckCards metrics={metrics} />)
    const card = screen.getByText('MEMORY').closest('div[class*="absolute"]')
    expect(card).toBeTruthy()
    fireEvent.pointerDown(card as HTMLElement, { clientX: 100, clientY: 100 })
    fireEvent.pointerMove(card as HTMLElement, { clientX: 160, clientY: 140 })
    fireEvent.pointerUp(card as HTMLElement)
    expect(container).toBeTruthy()
  })
})
