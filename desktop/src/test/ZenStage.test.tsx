import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ZenStage } from '../components/zen/ZenStage'

vi.mock('../components/center/AiCore', () => ({
  JarvisOrb: () => <div data-testid="orb" />,
}))

const baseProps = {
  orbState: 'idle' as const,
  metrics: { latency: 42, model: 'openrouter/free', provider: 'OpenRouter', memory: 34, tokenUsage: 0 },
  messages: [],
  autopilotRun: null,
  onSend: vi.fn(),
  onStop: vi.fn(),
  onRegenerate: vi.fn(),
  loading: false,
  voiceInputSupported: true,
  voiceStatus: 'idle' as const,
  voiceInterim: '',
  voiceLanguage: 'en-US',
  onVoiceStart: vi.fn(),
  onVoiceStop: vi.fn().mockReturnValue(''),
  onCycleLanguage: vi.fn(),
  onToggleDashboard: vi.fn(),
  temperature: null,
  time: '10:00:00',
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ZenStage', () => {
  it('renders the orb and input, without dashboard chrome', () => {
    render(<ZenStage {...baseProps} />)
    expect(screen.getByTestId('orb')).toBeTruthy()
    expect(screen.getByPlaceholderText('Message Friday...')).toBeTruthy()
  })

  it('sends a message via input', () => {
    render(<ZenStage {...baseProps} />)
    const input = screen.getByPlaceholderText('Message Friday...')
    fireEvent.change(input, { target: { value: 'hello friday' } })
    fireEvent.click(screen.getByText('↑'))
    expect(baseProps.onSend).toHaveBeenCalledWith('hello friday')
  })

  it('shows ambient widget chips when data is present', () => {
    render(<ZenStage {...baseProps} temperature={22} location="Karachi" />)
    expect(screen.getByText('TEMP')).toBeTruthy()
    expect(screen.getByText('22°C')).toBeTruthy()
  })

  it('renders chat messages below the orb when present', () => {
    render(<ZenStage {...baseProps} messages={[
      { id: 'u1', role: 'user', content: 'hi' },
      { id: 'a1', role: 'assistant', content: 'hello' },
    ]} />)
    expect(screen.getByText('hi')).toBeTruthy()
    expect(screen.getByText('hello')).toBeTruthy()
  })

  it('toggles dashboard via the stage button', () => {
    render(<ZenStage {...baseProps} />)
    fireEvent.click(screen.getByTitle('Toggle dashboard (⌘B)'))
    expect(baseProps.onToggleDashboard).toHaveBeenCalled()
  })

  it('toggles hands-free listening', () => {
    const onToggle = vi.fn()
    render(<ZenStage {...baseProps} handsFree={false} onToggleHandsFree={onToggle} />)
    fireEvent.click(screen.getByTitle(/Hands-free listening off/))
    expect(onToggle).toHaveBeenCalled()
  })

  it('shows AMBIENT badge when ambient is active', () => {
    render(<ZenStage {...baseProps} ambientActive handsFree />)
    expect(screen.getByText('AMBIENT')).toBeTruthy()
  })

  it('shows continuity hint when no messages yet', () => {
    render(<ZenStage {...baseProps} continuity="Context from previous sessions — you last worked on: Friday." />)
    expect(screen.getByText(/you last worked on: Friday/)).toBeTruthy()
  })

  it('does not show continuity once messages exist', () => {
    render(<ZenStage {...baseProps} continuity="Context from previous sessions" messages={[
      { id: 'u1', role: 'user', content: 'hi' },
    ]} />)
    expect(screen.queryByText(/Context from previous sessions/)).toBeNull()
  })
})