import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  message: string
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, message: '' }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, message: error.message }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Friday crashed a component:', error, info.componentStack)
  }

  private reset = () => {
    this.setState({ hasError: false, message: '' })
  }

  render() {
    if (!this.state.hasError) return this.props.children

    if (this.props.fallback) return this.props.fallback

    return (
      <div
        className="flex min-h-[200px] items-center justify-center rounded-xl p-6"
        style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)' }}
      >
        <div className="max-w-sm text-center">
          <div className="text-2xl">{'\u26A0'}</div>
          <div className="mt-2 text-sm font-medium" style={{ color: '#e5e5e5' }}>
            Something went wrong
          </div>
          <div className="mt-1 text-xs text-muted" style={{ color: '#999' }}>
            {this.state.message || 'An unexpected error occurred in this section.'}
          </div>
          <button
            onClick={this.reset}
            className="mt-4 rounded-lg px-4 py-1.5 text-xs font-medium transition-all hover:scale-105"
            style={{ background: 'rgba(239,68,68,0.15)', color: '#EF4444' }}
          >
            Try again
          </button>
        </div>
      </div>
    )
  }
}

export function AppErrorFallback() {
  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center"
      style={{ background: '#0a0a0c' }}
    >
      <div className="mx-4 max-w-md rounded-2xl border border-red-500/25 p-6 text-center glass red-glow">
        <div className="text-3xl">{'\u26A0'}</div>
        <h1 className="mt-3 text-base font-semibold" style={{ color: '#e5e5e5' }}>
          Friday hit an unexpected error
        </h1>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 rounded-lg px-5 py-2 text-xs font-medium transition-all hover:scale-105"
          style={{ background: 'linear-gradient(135deg, var(--gold), var(--gold-bright))', color: '#000' }}
        >
          Reload app
        </button>
      </div>
    </div>
  )
}