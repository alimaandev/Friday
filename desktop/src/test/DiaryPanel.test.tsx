import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { DiaryPanel } from '../components/sidebar/DiaryPanel'
import { getDiaryRecent, getDiaryPage, writeNightlyDigest } from '../core/api'

vi.mock('../core/api', () => {
  return {
    getDiaryRecent: vi.fn(),
    getDiaryPage: vi.fn(),
    writeNightlyDigest: vi.fn(),
  }
})

const mockedRecent = vi.mocked(getDiaryRecent)
const mockedPage = vi.mocked(getDiaryPage)
const mockedWrite = vi.mocked(writeNightlyDigest)

beforeEach(() => {
  vi.clearAllMocks()
  mockedRecent.mockResolvedValue({
    days: [
      { date: '2026-08-09', excerpt: 'Coffee fixed. Backlog triaged.' },
      { date: '2026-08-10', excerpt: 'Built the diary engine.' },
    ],
  })
  mockedPage.mockResolvedValue({ date: '2026-08-10', content: '## 21:00 — Nightly digest\n\nToday I carry 2 facts.' })
  mockedWrite.mockResolvedValue({ path: 'x.md', success: true })
})

describe('DiaryPanel', () => {
  it('loads and lists diary days', async () => {
    render(<DiaryPanel />)
    expect(await screen.findByText('2026-08-10')).toBeTruthy()
    expect(screen.getByText('2026-08-09')).toBeTruthy()
    expect(getDiaryRecent).toHaveBeenCalled()
  })

  it('renders markdown of the latest day by default', async () => {
    render(<DiaryPanel />)
    await waitFor(() => {
      expect(getDiaryPage).toHaveBeenCalledWith('2026-08-10')
    })
    expect(await screen.findByText(/Built the diary engine/)).toBeTruthy()
  })

  it('switches page when another day is selected', async () => {
    render(<DiaryPanel />)
    fireEvent.click(await screen.findByText('2026-08-09'))
    await waitFor(() => {
      expect(getDiaryPage).toHaveBeenCalledWith('2026-08-09')
    })
  })

  it('writes a nightly entry and refreshes', async () => {
    render(<DiaryPanel />)
    fireEvent.click(screen.getByText('✦ Tonight'))
    await waitFor(() => {
      expect(writeNightlyDigest).toHaveBeenCalled()
    })
    await waitFor(() => {
      expect(screen.getByText('✦ Tonight')).toBeTruthy()
    })
  })

  it('shows empty state when no days exist', async () => {
    mockedRecent.mockResolvedValue({ days: [] })
    render(<DiaryPanel />)
    expect(await screen.findByText(/No diary pages yet/)).toBeTruthy()
  })

  it('refetches when refreshToken changes', async () => {
    const { rerender } = render(<DiaryPanel refreshToken={0} />)
    await screen.findByText('2026-08-10')
    rerender(<DiaryPanel refreshToken={1} />)
    await waitFor(() => {
      expect(mockedRecent.mock.calls.length).toBe(2)
    })
  })
})