import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorBoundary, AppErrorFallback } from '../components/common/ErrorBoundary'

const Boom = () => { throw new Error('render crash') }

describe('ErrorBoundary', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should render children when no error', () => {
    render(
      <ErrorBoundary>
        <div>content</div>
      </ErrorBoundary>,
    )
    expect(screen.getByText('content')).toBeInTheDocument()
  })

  it('should show fallback UI on render error', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
    render(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>,
    )
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Try again')).toBeInTheDocument()
    consoleError.mockRestore()
  })

  it('should show custom fallback when provided', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
    render(
      <ErrorBoundary fallback={<div>custom fallback</div>}>
        <Boom />
      </ErrorBoundary>,
    )
    expect(screen.getByText('custom fallback')).toBeInTheDocument()
    consoleError.mockRestore()
  })

  it('AppErrorFallback shows reload button', () => {
    render(<AppErrorFallback />)
    expect(screen.getByText('Reload app')).toBeInTheDocument()
  })
})