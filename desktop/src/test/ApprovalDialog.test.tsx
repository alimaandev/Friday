import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ApprovalDialog } from '../components/chat/ApprovalDialog'
import type { ApprovalRequest } from '../types'

const request: ApprovalRequest = {
  id: 'req-1',
  tool: 'delete_file',
  args: { path: 'rm -rf project' },
}

describe('ApprovalDialog', () => {
  it('should render tool name and arguments', () => {
    render(<ApprovalDialog request={request} onResolve={() => {}} />)
    expect(screen.getByText('Confirm tool call')).toBeInTheDocument()
    expect(screen.getByText('delete_file')).toBeInTheDocument()
    expect(screen.getByText(/rm -rf project/)).toBeInTheDocument()
  })

  it('should show "(no arguments)" when args are missing', () => {
    render(<ApprovalDialog request={{ id: 'req-2', tool: 'shutdown' }} onResolve={() => {}} />)
    expect(screen.getByText(/no arguments/)).toBeInTheDocument()
  })

  it('should call onResolve with true on Allow', () => {
    const onResolve = vi.fn()
    render(<ApprovalDialog request={request} onResolve={onResolve} />)
    screen.getByText('Allow').click()
    expect(onResolve).toHaveBeenCalledWith('req-1', true)
  })

  it('should call onResolve with false on Deny', () => {
    const onResolve = vi.fn()
    render(<ApprovalDialog request={request} onResolve={onResolve} />)
    screen.getByText('Deny').click()
    expect(onResolve).toHaveBeenCalledWith('req-1', false)
  })
})