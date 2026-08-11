import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ScreenPanel } from '../components/sidebar/ScreenPanel'
import type { ScreenData } from '../types'

vi.mock('../core/api', () => ({
  getComputerSummary: vi.fn().mockResolvedValue({
    windows: [
      { handle: 1, title: 'Notepad' },
      { handle: 2, title: 'Chrome' },
    ],
    count: 2,
  }),
  getComputerStatus: vi.fn(),
}))

const screenData: ScreenData = {
  image: 'iVBORw0KGgo=',
  width: 1920,
  height: 1080,
  timestamp: 1700000000,
}

const status = { platform: 'Windows', mouse_keyboard: true, window_management: true }

const expand = () => {
  const toggle = screen.getByText('\u25B6')
  fireEvent.click(toggle)
}

const openControl = () => {
  expand()
  fireEvent.click(screen.getByText('CONTROL'))
}

describe('ScreenPanel', () => {
  it('shows CONTROL and SCREEN tabs', () => {
    render(<ScreenPanel data={null} loading={false} computerStatus={status} />)
    expect(screen.getByText('SCREEN')).toBeTruthy()
    expect(screen.getByText('CONTROL')).toBeTruthy()
  })

  it('renders screen image when expanded', () => {
    render(<ScreenPanel data={screenData} loading={false} computerStatus={status} />)
    expand()
    expect(screen.getByAltText('Screen capture')).toBeTruthy()
  })

  it('shows control status chips in control tab', async () => {
    render(<ScreenPanel data={null} loading={false} computerStatus={status} />)
    openControl()
    expect(await screen.findByText(/Windows/)).toBeTruthy()
    expect(screen.getByText(/MOUSE\/KB ON/)).toBeTruthy()
    expect(screen.getByText(/OPEN WINDOWS/)).toBeTruthy()
  })

  it('shows partial control when capabilities are missing', () => {
    render(<ScreenPanel data={null} loading={false} computerStatus={{ ...status, window_management: false }} />)
    openControl()
    expect(screen.getByText(/WINDOWS OFF/)).toBeTruthy()
  })
})
