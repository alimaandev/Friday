import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchApi, setApiKey, checkHealth } from '../core/api'

const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

beforeEach(() => {
  mockFetch.mockReset()
  localStorage.clear()
})

describe('fetchApi', () => {
  it('should make a GET request and return JSON', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'ok' }),
    })
    const result = await fetchApi('/health')
    expect(result).toEqual({ status: 'ok' })
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8080/api/v1/health',
      expect.objectContaining({
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
      }),
    )
  })

  it('should throw ApiError on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({ error: 'not found' }),
    })
    await expect(fetchApi('/missing')).rejects.toMatchObject({
      status: 404,
      message: 'not found',
    })
  })

  it('should include api key header when set', async () => {
    setApiKey('secret-123')
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({}),
    })
    await fetchApi('/test')
    const callHeaders = mockFetch.mock.calls[0][1].headers
    expect(callHeaders['X-API-Key']).toBe('secret-123')
  })

  it('should abort on timeout', async () => {
    mockFetch.mockImplementationOnce((_url: string, options: RequestInit) => {
      return new Promise((_, reject) => {
        const signal = (options as any)?.signal as AbortSignal
        if (signal) {
          signal.addEventListener('abort', () => {
            reject(new DOMException('Aborted', 'AbortError'))
          })
        }
      })
    })
    await expect(fetchApi('/slow', {}, 50)).rejects.toThrow('Aborted')
  })
})

describe('checkHealth', () => {
  it('should call GET /health', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'ok', sessions: 3 }),
    })
    const result = await checkHealth()
    expect(result).toEqual({ status: 'ok', sessions: 3 })
  })
})
