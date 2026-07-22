const API_BASE = 'http://localhost:8080'

const AUTH_KEY = 'friday_api_secret'

function getApiKey(): string {
  return localStorage.getItem(AUTH_KEY) || ''
}

export function setApiKey(key: string) {
  localStorage.setItem(AUTH_KEY, key)
}

function authHeaders(): Record<string, string> {
  const key = getApiKey()
  return key ? { 'X-API-Key': key } : {}
}

export interface ApiError {
  status: number
  message: string
  body?: any
}

/* ─── Low-level fetch with auth + base URL ─── */
export async function fetchApi<T = any>(
  path: string,
  options: RequestInit = {},
  timeoutMs = 15_000,
): Promise<T> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
        ...options.headers,
      },
    })

    if (!res.ok) {
      const body = await res.json().catch(() => null)
      throw { status: res.status, message: body?.error || res.statusText, body } as ApiError
    }

    return await res.json() as T
  } finally {
    clearTimeout(timer)
  }
}

/* ─── SSE streaming helper ─── */
export function streamChat(
  body: { message: string; session_id?: string },
  onEvent: (event: any) => void,
  onError: (err: any) => void,
  onDone: () => void,
): AbortController {
  const controller = new AbortController()

  ;(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders(),
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => null)
        onError({ status: res.status, message: data?.error || res.statusText })
        onDone()
        return
      }

      const reader = res.body?.getReader()
      if (!reader) {
        onError({ message: 'No response body' })
        onDone()
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.trim()) continue
          try {
            const event = JSON.parse(line)
            onEvent(event)
          } catch {
            // skip malformed lines
          }
        }
      }
      onDone()
    } catch (err: any) {
      if (err?.name !== 'AbortError') {
        onError(err)
        onDone()
      }
    }
  })()

  return controller
}

/* ─── Typed endpoint helpers ─── */

export async function checkHealth(): Promise<{ status: string; sessions: number }> {
  return fetchApi('/api/health')
}

export async function getMetrics(): Promise<any> {
  return fetchApi('/api/metrics')
}

export async function getSessions(): Promise<{ sessions: { id: string; language: string }[] }> {
  return fetchApi('/api/sessions')
}

export async function createSession(language = 'english') {
  return fetchApi('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({ language }),
  })
}

export async function deleteSession(sessionId: string) {
  return fetchApi(`/api/sessions/${sessionId}`, { method: 'DELETE' })
}

export async function getOutputDir(sessionId = 'default') {
  return fetchApi<{ output_dir: string }>(`/api/output-dir?session_id=${sessionId}`)
}

export async function setOutputDir(path: string, sessionId = 'default') {
  return fetchApi('/api/output-dir', {
    method: 'PUT',
    body: JSON.stringify({ session_id: sessionId, path }),
  })
}

export async function getSystemInfo(): Promise<any> {
  return fetchApi('/api/system-info')
}

export async function getNews(): Promise<{ articles: any[] }> {
  return fetchApi('/api/news')
}

export async function getWeather(): Promise<any> {
  return fetchApi('/api/weather')
}

export async function getStocks(symbols = 'AAPL,GOOG,MSFT,NVDA,BTC-USD'): Promise<any> {
  return fetchApi(`/api/stocks?symbols=${encodeURIComponent(symbols)}`)
}

export async function getGithubTrending(): Promise<any> {
  return fetchApi('/api/github-trending')
}

export async function getEarthquakes(): Promise<any> {
  return fetchApi('/api/earthquakes')
}

export async function getCrypto(): Promise<any> {
  return fetchApi('/api/crypto')
}

export async function getSpace(): Promise<any> {
  return fetchApi('/api/space')
}

export async function getGlobalTime(): Promise<any> {
  return fetchApi('/api/global-time')
}

export async function getCve(): Promise<any> {
  return fetchApi('/api/cve')
}

export async function getScreen(): Promise<any> {
  return fetchApi('/api/screen')
}

export async function getMemory(): Promise<any> {
  return fetchApi('/api/memory')
}

export async function searchMemory(query: string, topK = 5): Promise<any> {
  return fetchApi('/api/memory/search', {
    method: 'POST',
    body: JSON.stringify({ query, top_k: topK }),
  })
}

export async function clearMemory() {
  return fetchApi('/api/memory', { method: 'DELETE' })
}

export async function getGoogleAuth(): Promise<any> {
  return fetchApi('/api/auth/google')
}

export async function getCalendarEvents(): Promise<any> {
  return fetchApi('/api/calendar/events')
}

export async function getEmailInbox(): Promise<any> {
  return fetchApi('/api/email/inbox')
}

export async function getEmailUnread(): Promise<any> {
  return fetchApi('/api/email/unread')
}

export async function getAlerts(): Promise<{ alerts: any[]; count: number }> {
  return fetchApi('/api/alerts')
}

/* ─── SSE EventSource connection ─── */
export type ServerEvent = {
  type: string
  data: any
}

export function connectEventSource(
  onEvent: (event: ServerEvent) => void,
  onError?: () => void,
): () => void {
  const key = getApiKey()
  const url = key ? `${API_BASE}/api/events?key=${encodeURIComponent(key)}` : `${API_BASE}/api/events`
  const es = new EventSource(url)

  es.onmessage = (msg) => {
    try {
      const parsed = JSON.parse(msg.data)
      onEvent(parsed)
    } catch {
      // skip malformed messages
    }
  }

  es.onerror = () => {
    onError?.()
  }

  return () => {
    es.close()
  }
}
