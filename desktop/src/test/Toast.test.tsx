import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { ToastContainer } from '../components/common/Toast'
import { toast, clearToasts } from '../core/ToastStore'

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    clearToasts()
  })

  afterEach(() => {
    clearToasts()
    vi.useRealTimers()
  })

  it('should render a success toast', () => {
    render(<ToastContainer />)
    act(() => { toast('success', 'Saved') })
    expect(screen.getByText('Saved')).toBeInTheDocument()
  })

  it('should render error and warning toasts', () => {
    render(<ToastContainer />)
    act(() => {
      toast('error', 'Failed')
      toast('warning', 'Careful')
    })
    expect(screen.getByText('Failed')).toBeInTheDocument()
    expect(screen.getByText('Careful')).toBeInTheDocument()
  })

  it('should remove toast after ttl', () => {
    render(<ToastContainer />)
    act(() => { toast('info', 'Brief', 100) })
    expect(screen.getByText('Brief')).toBeInTheDocument()
    act(() => { vi.advanceTimersByTime(150) })
    expect(screen.queryByText('Brief')).not.toBeInTheDocument()
  })

  it('should dismiss toast on close click', () => {
    render(<ToastContainer />)
    act(() => { toast('info', 'Dismiss me') })
    const close = screen.getByText('\u2715')
    act(() => { close.click() })
    expect(screen.queryByText('Dismiss me')).not.toBeInTheDocument()
  })
})