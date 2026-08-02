import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { InputBar } from '../components/chat/InputBar'

const defaultProps = {
  onSend: vi.fn(),
  loading: false,
  onVoiceStart: vi.fn(),
  onVoiceStop: vi.fn(() => ''),
  voiceStatus: 'idle' as const,
  voiceInterim: '',
  isVoiceSupported: false,
  voiceLanguage: 'en-US',
  onCycleLanguage: vi.fn(),
}

describe('InputBar', () => {
  it('should render textarea with placeholder', () => {
    render(<InputBar {...defaultProps} />)
    const textarea = screen.getByPlaceholderText('Message Friday...')
    expect(textarea).toBeInTheDocument()
  })

  it('should render suggestion chips when not loading and no input', () => {
    render(<InputBar {...defaultProps} />)
    expect(screen.getByText('Explain')).toBeInTheDocument()
    expect(screen.getByText('Search')).toBeInTheDocument()
    expect(screen.getByText('Code')).toBeInTheDocument()
    expect(screen.getByText('Summarize')).toBeInTheDocument()
  })

  it('should disable send button when empty', () => {
    render(<InputBar {...defaultProps} />)
    const sendBtn = screen.getByText('\u2191')
    expect(sendBtn).toBeDisabled()
  })

  it('should hide suggestions when loading', () => {
    render(<InputBar {...defaultProps} loading={true} />)
    expect(screen.queryByText('Explain')).not.toBeInTheDocument()
  })

  it('should show voice button when supported', () => {
    render(<InputBar {...defaultProps} isVoiceSupported={true} />)
    const voiceBtn = screen.getByTitle('Hold to speak')
    expect(voiceBtn).toBeInTheDocument()
  })

  it('should show voice language label when supported', () => {
    render(<InputBar {...defaultProps} isVoiceSupported={true} voiceLanguage='hi-IN' />)
    expect(screen.getByText('HI')).toBeInTheDocument()
  })

  it('should show listening indicator when voice is active', () => {
    render(<InputBar {...defaultProps} isVoiceSupported={true} voiceStatus='listening' voiceInterim='testing' />)
    expect(screen.getByText('testing')).toBeInTheDocument()
    const voiceBtn = screen.getByTitle('Release to send')
    expect(voiceBtn).toBeInTheDocument()
  })

  it('should render file attachment button', () => {
    render(<InputBar {...defaultProps} />)
    const attachBtn = screen.getByTitle('Attach file')
    expect(attachBtn).toBeInTheDocument()
  })

  it('should render with QuickActions', () => {
    const { container } = render(<InputBar {...defaultProps} />)
    // QuickActions should render (it's always included)
    expect(container.querySelector('[class*="max-w-\\[720px\\]"]')).toBeTruthy()
  })
})
