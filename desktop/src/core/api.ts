import type { DiaryDay, DiaryPage } from '../types'

const API_BASE = 'http://localhost:8080/api/v1'

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
async function streamEndpoint(
  path: string,
  body: Record<string, unknown>,
  onEvent: (event: any) => void,
  onError: (err: any) => void,
  onDone: () => void,
  controller: AbortController,
) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
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
}

export function streamChat(
  body: { message: string; session_id?: string; persona?: string },
  onEvent: (event: any) => void,
  onError: (err: any) => void,
  onDone: () => void,
): AbortController {
  const controller = new AbortController()
  streamEndpoint('/chat', body, onEvent, onError, onDone, controller)
  return controller
}

export function streamAutopilot(
  body: { goal: string; session_id?: string },
  onEvent: (event: any) => void,
  onError: (err: any) => void,
  onDone: () => void,
): AbortController {
  const controller = new AbortController()
  streamEndpoint('/autopilot', body, onEvent, onError, onDone, controller)
  return controller
}

/* ─── Typed endpoint helpers ─── */

export async function checkHealth(): Promise<{ status: string; sessions: number }> {
  return fetchApi('/health')
}

export async function getMetrics(): Promise<any> {
  return fetchApi('/metrics')
}

export async function getSessions(): Promise<{ sessions: { id: string; language: string }[] }> {
  return fetchApi('/sessions')
}

export async function createSession(language = 'english') {
  return fetchApi('/sessions', {
    method: 'POST',
    body: JSON.stringify({ language }),
  })
}

export async function deleteSession(sessionId: string) {
  return fetchApi(`/sessions/${sessionId}`, { method: 'DELETE' })
}

export async function getOutputDir(sessionId = 'default') {
  return fetchApi<{ output_dir: string }>(`/output-dir?session_id=${sessionId}`)
}

export async function setOutputDir(path: string, sessionId = 'default') {
  return fetchApi('/output-dir', {
    method: 'PUT',
    body: JSON.stringify({ session_id: sessionId, path }),
  })
}

/* ─── Tool call approvals ──────────────────────────────────────── */

export async function getApprovals(): Promise<{ approvals: any[] }> {
  return fetchApi('/approvals')
}

export async function resolveApproval(requestId: string, allowed: boolean) {
  return fetchApi(`/approvals/${encodeURIComponent(requestId)}`, {
    method: 'POST',
    body: JSON.stringify({ allowed }),
  })
}

export async function getSystemInfo(): Promise<any> {
  return fetchApi('/system-info')
}

export async function getNews(): Promise<{ articles: any[] }> {
  return fetchApi('/news')
}

export async function getWeather(): Promise<any> {
  return fetchApi('/weather')
}

export async function getStocks(symbols = 'AAPL,GOOG,MSFT,NVDA,BTC-USD'): Promise<any> {
  return fetchApi(`/stocks?symbols=${encodeURIComponent(symbols)}`)
}

export async function getGithubTrending(): Promise<any> {
  return fetchApi('/github-trending')
}

export async function getEarthquakes(): Promise<any> {
  return fetchApi('/earthquakes')
}

export async function getCrypto(): Promise<any> {
  return fetchApi('/crypto')
}

export async function getSpace(): Promise<any> {
  return fetchApi('/space')
}

export async function getGlobalTime(): Promise<any> {
  return fetchApi('/global-time')
}

export async function getCve(): Promise<any> {
  return fetchApi('/cve')
}

export async function getScreen(): Promise<any> {
  return fetchApi('/screen')
}

export async function getMemory(): Promise<any> {
  return fetchApi('/memory')
}

export async function searchMemory(query: string, topK = 5): Promise<any> {
  return fetchApi('/memory/search', {
    method: 'POST',
    body: JSON.stringify({ query, top_k: topK }),
  })
}

export async function clearMemory() {
  return fetchApi('/memory', { method: 'DELETE' })
}

export async function deleteMemory(entryId: string) {
  return fetchApi(`/memory/${encodeURIComponent(entryId)}`, { method: 'DELETE' })
}

/* ─── Knowledge graph API ─────────────────────────────────────── */

export interface KnowledgeEntity {
  name: string
  type: string
  mentions: number
  source?: string
  first_seen?: number
  last_seen?: number
}

export async function getKnowledge(): Promise<{ entities: KnowledgeEntity[]; count: number }> {
  return fetchApi('/knowledge')
}

export async function storeKnowledge(text: string): Promise<{ added: KnowledgeEntity[]; count: number }> {
  return fetchApi('/knowledge', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export async function queryKnowledge(term: string): Promise<{ results: KnowledgeEntity[]; count: number }> {
  return fetchApi('/knowledge/query', {
    method: 'POST',
    body: JSON.stringify({ term }),
  })
}

export async function getKnowledgeContinuity(): Promise<{ continuity: string }> {
  return fetchApi('/knowledge/continuity')
}

/* ─── Computer control API ─────────────────────────────────────── */

export interface ComputerStatus {
  platform: string
  mouse_keyboard: boolean
  window_management: boolean
  note?: string
}

export async function getComputerStatus(): Promise<ComputerStatus> {
  return fetchApi('/computer/status')
}

export interface ComputerWindow {
  handle: number
  title: string
}

export interface ComputerWindows {
  windows: ComputerWindow[]
  count: number
}

export async function getComputerWindows(): Promise<ComputerWindows> {
  return fetchApi('/computer/windows')
}

export interface ComputerSummary extends ComputerStatus {
  windows: ComputerWindow[]
  count: number
  size: { success: boolean; width?: number; height?: number; error?: string }
}

export async function getComputerSummary(): Promise<ComputerSummary> {
  return fetchApi('/computer/summary')
}

/* ─── Diary API ───────────────────────────────────────────────── */

export async function getDiaryRecent(): Promise<{ days: DiaryDay[] }> {
  return fetchApi('/diary/recent')
}

export async function getDiaryPage(dateStr?: string): Promise<DiaryPage> {
  const q = dateStr ? `?date=${encodeURIComponent(dateStr)}` : ''
  return fetchApi(`/diary${q}`)
}

export async function writeNightlyDigest(): Promise<{ path: string; success: boolean }> {
  return fetchApi('/diary/nightly', { method: 'POST' })
}

export async function getGoogleAuth(): Promise<any> {
  return fetchApi('/auth/google')
}

export async function getCalendarEvents(): Promise<any> {
  return fetchApi('/calendar/events')
}

export async function getEmailInbox(): Promise<any> {
  return fetchApi('/email/inbox')
}

export async function getEmailUnread(): Promise<any> {
  return fetchApi('/email/unread')
}

export async function getAlerts(): Promise<{ alerts: any[]; count: number }> {
  return fetchApi('/alerts')
}

/* ─── Automations API ─────────────────────────────────────────── */

export async function getAutomations(): Promise<{ automations: any[] }> {
  return fetchApi('/automations')
}

export async function createAutomation(data: {
  name: string; trigger_type: string; trigger_config: Record<string, any>;
  action: string; action_params?: Record<string, any>;
}): Promise<any> {
  return fetchApi('/automations', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateAutomation(id: string, data: Record<string, any>): Promise<any> {
  return fetchApi(`/automations/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteAutomation(id: string): Promise<any> {
  return fetchApi(`/automations/${id}`, { method: 'DELETE' })
}

export async function toggleAutomation(id: string): Promise<any> {
  return fetchApi(`/automations/${id}/toggle`, { method: 'POST' })
}

export async function triggerAutomation(id: string): Promise<any> {
  return fetchApi(`/automations/${id}/trigger`, { method: 'POST' })
}

/* ─── Vision API ──────────────────────────────────────────────── */

export async function analyzeVisionImage(image: string, prompt?: string): Promise<{
  description: string; text: string | null; timestamp: number
}> {
  return fetchApi('/vision/analyze', {
    method: 'POST',
    body: JSON.stringify({ image, prompt }),
  })
}

export async function getVisionScreen(): Promise<{
  description: string; text: string | null; width: number; height: number; timestamp: number
}> {
  return fetchApi('/vision/screen')
}

/* ─── SSE EventSource connection ─── */
export type ServerEvent = {
  type: string
  data: any
}

export function connectEventSource(
  onEvent: (event: ServerEvent) => void,
  onError?: () => void,
  onStatus?: (connected: boolean) => void,
): () => void {
  let es: EventSource | null = null
  let closed = false
  let retryDelay = 1000
  const MAX_RETRY = 30000

  function connect() {
    if (closed) return
    const key = getApiKey()
    const url = key ? `${API_BASE}/events?key=${encodeURIComponent(key)}` : `${API_BASE}/events`
    es = new EventSource(url)

    es.onmessage = (msg) => {
      try {
        const parsed = JSON.parse(msg.data)
        onEvent(parsed)
      } catch {
        // skip malformed messages
      }
    }

    es.onopen = () => {
      retryDelay = 1000
      onStatus?.(true)
    }

    es.onerror = () => {
      es?.close()
      es = null
      onStatus?.(false)
      onError?.()
      if (closed) return
      const delay = retryDelay
      retryDelay = Math.min(retryDelay * 2, MAX_RETRY)
      setTimeout(connect, delay)
    }
  }

  connect()

  return () => {
    closed = true
    es?.close()
    es = null
  }
}
