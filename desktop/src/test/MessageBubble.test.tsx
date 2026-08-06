import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageBubble } from '../components/chat/MessageBubble'
import type { Message } from '../types'

describe('MessageBubble', () => {
  const userMsg: Message = {
    id: '1',
    role: 'user',
    content: 'Hello Friday',
  }

  const assistantMsg: Message = {
    id: '2',
    role: 'assistant',
    content: 'Hello! How can I help?',
  }

  const streamingMsg: Message = {
    id: '3',
    role: 'assistant',
    content: 'Thinking...',
    streaming: true,
  }

  const msgWithTools: Message = {
    id: '4',
    role: 'assistant',
    content: 'Let me check that.',
    toolCalls: [
      { name: 'web_fetch', args: 'url=https://example.com', result: '{"status": 200}' },
    ],
  }

  const msgWithPlan: Message = {
    id: '5',
    role: 'assistant',
    content: 'I have a plan.',
    plan: 'Step 1: Search\nStep 2: Analyze',
  }

  const msgWithReflex: Message = {
    id: '6',
    role: 'assistant',
    content: 'Quick response',
    reflex: 'time',
  }

  it('should render user message', () => {
    const { container } = render(<MessageBubble message={userMsg} index={0} />)
    expect(screen.getByText('Hello Friday')).toBeInTheDocument()
    expect(container.querySelector('[class*="justify-end"]')).toBeTruthy()
  })

  it('should render assistant message', () => {
    render(<MessageBubble message={assistantMsg} index={0} />)
    expect(screen.getByText('Hello! How can I help?')).toBeInTheDocument()
  })

  it('should show streaming indicator', () => {
    render(<MessageBubble message={streamingMsg} index={0} />)
    const cursor = screen.getByText('\u258A')
    expect(cursor).toBeInTheDocument()
  })

  it('should show tool calls collapsible', () => {
    render(<MessageBubble message={msgWithTools} index={0} />)
    expect(screen.getByText('web_fetch')).toBeInTheDocument()
  })

  it('should show plan display', () => {
    render(<MessageBubble message={msgWithPlan} index={0} />)
    expect(screen.getByText('PLAN')).toBeInTheDocument()
    expect(screen.getByText(/Step 1: Search/)).toBeInTheDocument()
  })

  it('should show reflex badge', () => {
    render(<MessageBubble message={msgWithReflex} index={0} />)
    expect(screen.getByText(msgWithReflex.reflex!)).toBeInTheDocument()
    expect(screen.getByText('system-1')).toBeInTheDocument()
  })

  it('should show copy button on hover', () => {
    render(<MessageBubble message={assistantMsg} index={0} />)
    const copyBtn = screen.getByTitle('Copy message')
    expect(copyBtn).toBeInTheDocument()
  })

  it('should show stop button for streaming assistant message', () => {
    const onStop = vi.fn()
    render(<MessageBubble message={streamingMsg} index={0} onStop={onStop} />)
    const stopBtn = screen.getByTitle('Stop generation')
    expect(stopBtn).toBeInTheDocument()
  })

  it('should show regenerate button for non-streaming assistant message', () => {
    const onRegenerate = vi.fn()
    render(<MessageBubble message={assistantMsg} index={0} onRegenerate={onRegenerate} />)
    const regenBtn = screen.getByTitle('Regenerate response')
    expect(regenBtn).toBeInTheDocument()
  })
})
