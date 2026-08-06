import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { AlertToast } from '../components/chat/AlertToast'
import type { ProactiveAlert } from '../types'

const alert: ProactiveAlert = {
  type: 'system',
  title: 'CPU High',
  description: 'CPU usage at 95%',
  severity: 'warning',
  timestamp: Date.now(),
}

describe('AlertToast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should render with title and description', () => {
    render(<AlertToast alert={alert} onDismiss={() => {}} />)
    expect(screen.getByText('CPU High')).toBeInTheDocument()
    expect(screen.getByText('CPU usage at 95%')).toBeInTheDocument()
  })

  it('should show action button when action_label is present', () => {
    const alertWithAction = { ...alert, action_label: 'Fix it' }
    render(<AlertToast alert={alertWithAction} onDismiss={() => {}} />)
    expect(screen.getByText('Fix it')).toBeInTheDocument()
  })

  it('should call onDismiss after 6 seconds', () => {
    const onDismiss = vi.fn()
    render(<AlertToast alert={alert} onDismiss={onDismiss} />)
    act(() => { vi.advanceTimersByTime(6300) })
    expect(onDismiss).toHaveBeenCalled()
  })

  it('should dismiss on close button click', () => {
    const onDismiss = vi.fn()
    render(<AlertToast alert={alert} onDismiss={onDismiss} />)
    const closeBtn = screen.getByText('\u2715')
    closeBtn.click()
    act(() => { vi.advanceTimersByTime(400) })
    expect(onDismiss).toHaveBeenCalled()
  })
})
