import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Onboarding } from '../components/zen/Onboarding'

describe('Onboarding', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('shows greeting and flagship suggestions on first launch', () => {
    render(<Onboarding onDismiss={() => {}} onSuggest={() => {}} />)
    expect(screen.getByText(/Hello, I'm Friday/)).toBeTruthy()
    expect(screen.getByText('GET STARTED')).toBeTruthy()
    expect(screen.getByText(/organize my desktop/)).toBeTruthy()
  })

  it('persists dismissal to localStorage', () => {
    render(<Onboarding onDismiss={() => {}} onSuggest={() => {}} />)
    fireEvent.click(screen.getByText('GET STARTED'))
    expect(localStorage.getItem('friday_onboarded')).toBe('1')
  })

  it('does not render if already onboarded', () => {
    localStorage.setItem('friday_onboarded', '1')
    const { container } = render(<Onboarding onDismiss={() => {}} onSuggest={() => {}} />)
    expect(container.firstChild).toBeNull()
  })

  it('fires onSuggest with the selected suggestion', () => {
    const onSuggest = vi.fn()
    render(<Onboarding onDismiss={() => {}} onSuggest={onSuggest} />)
    fireEvent.click(screen.getByText(/organize my desktop/))
    expect(onSuggest).toHaveBeenCalledWith('Autopilot: organize my desktop and summarize')
  })
})
