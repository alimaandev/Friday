import { useState, useCallback, useEffect, useRef } from 'react'
import { theme } from './core/ThemeEngine'
import { state } from './core/StateManager'
import { LeftSidebar } from './components/sidebar/LeftSidebar'
import { StatusRibbon } from './components/topbar/TopBar'
import { IntelligencePanel } from './components/sidebar/IntelligencePanel'
import { AiCore } from './components/center/AiCore'
import { MessageBubble } from './components/chat/MessageBubble'
import { InputBar } from './components/chat/InputBar'
import { CommandPalette } from './components/command/CommandPalette'
import { CameraIndicator } from './components/common/CameraIndicator'
import { useCamera } from './hooks/useCamera'
import { useHandGesture } from './hooks/useHandGesture'
import type { SystemInfo, NewsItem, WeatherData, Earthquake, CryptoData, SpaceData, CveItem, WorldClock } from './types'

const API_BASE = 'http://localhost:8080'

let msgId = 0
const nextId = () => `m${++msgId}`

function useForceUpdate() {
  const [, set] = useState(0)
  return useCallback(() => set(n => n + 1), [])
}

function App() {
  const forceUpdate = useForceUpdate()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [commandOpen, setCommandOpen] = useState(false)
  const [camActive, setCamActive] = useState(false)
  const [backendOnline, setBackendOnline] = useState(true)
  const [outputDir, setOutputDir] = useState('')
  const [dataLoaded, setDataLoaded] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setDataLoaded(true), 2000)
    return () => clearTimeout(timer)
  }, [])

  const markLoaded = useCallback(() => setDataLoaded(true), [])

  const [systemInfo, setSystemInfo] = useState<SystemInfo>({
    hostname: '-', os: '-', cpu_cores: 0, python_version: '-',
    uptime_seconds: 0, llm_calls: 0, tokens_used: 0, failures: 0, retries: 0,
    model: '-', provider: '-',
  })
  const [news, setNews] = useState<NewsItem[]>([])
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [stocks, setStocks] = useState<any[]>([])
  const [repos, setRepos] = useState<any[]>([])
  const [earthquakes, setEarthquakes] = useState<Earthquake[]>([])
  const [crypto, setCrypto] = useState<CryptoData[]>([])
  const [space, setSpace] = useState<SpaceData | null>(null)
  const [cve, setCve] = useState<CveItem[]>([])
  const [clocks, setClocks] = useState<WorldClock[]>([])

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { stream, status: camStatus, requestAccess, stop: stopCam } = useCamera()
  const { openness, position: handPosition } = useHandGesture(stream, camActive)

  useEffect(() => {
    theme.init()
    const unsub = state.subscribe(forceUpdate)
    return () => { unsub() }
  }, [forceUpdate])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  })

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandOpen(o => !o)
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [])

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/health`)
        setBackendOnline(res.ok)
      } catch { setBackendOnline(false) }
    }
    check()
  }, [])

  // Sync sessions from backend on mount
  useEffect(() => {
    let cancelled = false
    const sync = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/sessions`)
        if (!res.ok) return
        const data = await res.json()
        if (cancelled) return
        if (data.sessions.length > 0) {
          const synced = data.sessions.map((s: any) => ({
            id: s.id,
            title: s.language === 'hinglish' ? 'Hinglish session' : 'Session',
            messages: [],
            createdAt: Date.now(),
          }))
          state.set({ sessions: synced, activeSessionId: data.sessions[0].id })
        } else {
          const cre = await fetch(`${API_BASE}/api/sessions`, { method: 'POST' })
          const created = await cre.json()
          if (!cancelled) {
            state.set({
              sessions: [{ id: created.session_id, title: 'Session', messages: [], createdAt: Date.now() }],
              activeSessionId: created.session_id,
            })
          }
        }
      } catch { /* backend offline */ }
    }
    sync()
    return () => { cancelled = true }
  }, [])

  // Poll metrics from backend
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/metrics`)
        if (!res.ok) return
        const data = await res.json()
        const durations = data.avg_tool_duration_ms || {}
        const vals = Object.values(durations) as number[]
        const avgLatency = vals.length > 0 ? Math.round(vals.reduce((a: number, b: number) => a + b, 0) / vals.length) : 0
        state.setMetrics({
          latency: avgLatency,
          tokenUsage: data.tokens_used || 0,
        })
      } catch { /* ignore */ }
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const s = state.get()
  const active = state.activeSession

  // Fetch output dir on session change
  useEffect(() => {
    fetch(`${API_BASE}/api/output-dir?session_id=${s.activeSessionId}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setOutputDir(d.output_dir) })
      .catch(() => {})
  }, [s.activeSessionId])

  // Fetch system info every 30s
  useEffect(() => {
    const fetchSys = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/system-info`)
        if (res.ok) setSystemInfo(await res.json())
      } catch {}
    }
    fetchSys()
    const id = setInterval(fetchSys, 30000)
    return () => clearInterval(id)
  }, [])

  // Fetch news every 5 min
  useEffect(() => {
    const fetchNews = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/news`)
        if (res.ok) {
          const data = await res.json()
          setNews(data.articles || [])
        }
      } catch {}
    }
    fetchNews()
    const id = setInterval(fetchNews, 300000)
    return () => clearInterval(id)
  }, [])

  // Fetch weather every 10 min
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/weather`)
        if (res.ok) setWeather(await res.json())
      } catch {}
    }
    fetchWeather()
    const id = setInterval(fetchWeather, 600000)
    return () => clearInterval(id)
  }, [])

  // Fetch stocks every 60s
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/stocks?symbols=AAPL,GOOG,MSFT,NVDA,BTC-USD`)
        if (res.ok) {
          const data = await res.json()
          setStocks(data.stocks || [])
          markLoaded()
        }
      } catch {}
    }
    fetchStocks()
    const id = setInterval(fetchStocks, 60000)
    return () => clearInterval(id)
  }, [markLoaded])

  // Fetch GitHub trending every 5 min
  useEffect(() => {
    const fetchGH = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/github-trending`)
        if (res.ok) {
          const data = await res.json()
          setRepos(data.repos || [])
          markLoaded()
        }
      } catch {}
    }
    fetchGH()
    const id = setInterval(fetchGH, 300000)
    return () => clearInterval(id)
  }, [markLoaded])

  // Fetch earthquakes every 2 min
  useEffect(() => {
    const fetchEq = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/earthquakes`)
        if (res.ok) { const d = await res.json(); setEarthquakes(d.earthquakes || []) }
      } catch {}
    }
    fetchEq()
    const id = setInterval(fetchEq, 120000)
    return () => clearInterval(id)
  }, [])

  // Fetch crypto every 2 min
  useEffect(() => {
    const fetchCrypto = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/crypto`)
        if (res.ok) { const d = await res.json(); setCrypto(d.crypto || []); markLoaded() }
      } catch {}
    }
    fetchCrypto()
    const id = setInterval(fetchCrypto, 120000)
    return () => clearInterval(id)
  }, [markLoaded])

  // Fetch space data every 60s
  useEffect(() => {
    const fetchSpace = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/space`)
        if (res.ok) { setSpace(await res.json()); markLoaded() }
      } catch {}
    }
    fetchSpace()
    const id = setInterval(fetchSpace, 60000)
    return () => clearInterval(id)
  }, [markLoaded])

  // Fetch CVE every 10 min
  useEffect(() => {
    const fetchCve = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/cve`)
        if (res.ok) { const d = await res.json(); setCve(d.cve || []) }
      } catch {}
    }
    fetchCve()
    const id = setInterval(fetchCve, 600000)
    return () => clearInterval(id)
  }, [])

  // Fetch world clocks every 30s
  useEffect(() => {
    const fetchClocks = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/global-time`)
        if (res.ok) { const d = await res.json(); setClocks(d.clocks || []) }
      } catch {}
    }
    fetchClocks()
    const id = setInterval(fetchClocks, 30000)
    return () => clearInterval(id)
  }, [])

  const toggleCamera = useCallback(() => {
    setCamActive(prev => {
      if (prev) { stopCam(); return false }
      return true
    })
  }, [stopCam])

  const handleNewSession = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/sessions`, { method: 'POST' })
      if (!res.ok) throw new Error('Failed')
      const data = await res.json()
      state.set({
        sessions: [...s.sessions, { id: data.session_id, title: 'Session', messages: [], createdAt: Date.now() }],
        activeSessionId: data.session_id,
      })
    } catch {
      const id = `local_${Date.now()}`
      state.set({
        sessions: [...s.sessions, { id, title: 'Session (offline)', messages: [], createdAt: Date.now() }],
        activeSessionId: id,
      })
    }
  }, [s.sessions])

  const handleSetOutputDir = useCallback(async (path: string) => {
    setOutputDir(path)
    try {
      await fetch(`${API_BASE}/api/output-dir`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: s.activeSessionId, path }),
      })
    } catch {}
  }, [s.activeSessionId])

  const handleDeleteSession = useCallback((id: string) => {
    fetch(`${API_BASE}/api/sessions/${id}`, { method: 'DELETE' }).catch(() => {})
    const next = s.sessions.filter(x => x.id !== id)
    state.set({ sessions: next, activeSessionId: s.activeSessionId === id ? (next[0]?.id || 'default') : s.activeSessionId })
  }, [s.sessions, s.activeSessionId])

  const handleSend = useCallback(async (text: string) => {
    if (s.loading) return
    state.setLoading(true)
    state.setOrb('thinking')

    state.updateMessages(msgs => [...msgs, { id: nextId(), role: 'user', content: text }])

    const aid = nextId()
    state.updateMessages(msgs => [...msgs, { id: aid, role: 'assistant', content: '', streaming: true, toolCalls: [] }])

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: s.activeSessionId }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const reader = res.body?.getReader()
      if (!reader) throw new Error('No response body')
      const decoder = new TextDecoder()
      let acc = ''
      let lastFlush = 0
      const TOKEN_THROTTLE = 40
      const flushTokens = () => {
        lastFlush = performance.now()
        state.updateMessages(msgs => msgs.map(m => m.id === aid ? { ...m, content: acc } : m))
      }
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        for (const line of decoder.decode(value, { stream: true }).split('\n').filter(Boolean)) {
          try {
            const ev = JSON.parse(line)
            switch (ev.type) {
              case 'plan':
                state.updateMessages(msgs => msgs.map(m =>
                  m.id === aid ? { ...m, plan: ev.tasks.map((t: any, i: number) => `${i + 1}. ${t.description}`).join('\n') } : m
                ))
                state.setOrb('thinking')
                break
              case 'task_start': {
                const desc = (ev.task?.description || '').toLowerCase()
                if (desc.includes('search') || desc.includes('browse')) state.setOrb('searching')
                else if (desc.includes('code') || desc.includes('parse') || desc.includes('lint') || desc.includes('format')) state.setOrb('coding')
                else state.setOrb('reasoning')
                break
              }
              case 'tokens':
                acc += ev.content
                if (performance.now() - lastFlush >= TOKEN_THROTTLE) flushTokens()
                break
              case 'tool_result':
                flushTokens()
                state.updateMessages(msgs => msgs.map(m =>
                  m.id === aid ? { ...m, toolCalls: [...(m.toolCalls || []), ...(ev.tools || [])] } : m
                ))
                state.setOrb('executing')
                break
              case 'task_done':
                flushTokens()
                state.setOrb('reasoning')
                break
              case 'done':
                flushTokens()
                if (ev.final) {
                  state.updateMessages(msgs => msgs.map(m =>
                    m.id === aid ? { ...m, content: ev.content || acc, streaming: false } : m
                  ))
                  state.setOrb('idle')
                }
                break
            }
          } catch { /* skip malformed line */ }
        }
      }
    } catch (err) {
      state.updateMessages(msgs => msgs.map(m =>
        m.id === aid ? { ...m, content: `Error: ${err}`, streaming: false } : m
      ))
      state.setOrb('error')
      setTimeout(() => state.setOrb('idle'), 2000)
    }
    state.setLoading(false)
  }, [s.loading, s.activeSessionId])

  const sendMessage = useCallback((text: string) => {
    if (!text.trim() || s.loading) return
    handleSend(text)
  }, [s.loading, handleSend])

  /* Collect recent tool calls for Agent Activity panel */
  const recentTools = active.messages.flatMap(m => (m.toolCalls || [])).slice(-8)

  const commandActions = [
    { id: 'new-session', label: 'New session', action: handleNewSession },
    { id: 'toggle-sidebar', label: 'Toggle sessions sidebar', action: () => setSidebarOpen(o => !o) },
    { id: 'toggle-theme', label: 'Toggle theme', action: () => theme.toggle() },
    { id: 'toggle-camera', label: 'Gesture control', action: toggleCamera },
  ]

  return (
    <div className="h-full flex flex-col" style={{ background: '#050505' }}>
      {!backendOnline && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl text-xs"
          style={{ background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5' }}
        >
          Backend offline — start <code style={{ color: '#fbbf24' }}>python api_server.py</code> on port 8080
        </div>
      )}

      <CameraIndicator stream={camActive ? stream : null} active={camActive} openness={openness} onToggle={toggleCamera} />

      {camActive && camStatus === 'idle' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.6)' }}>
          <div
            className="rounded-2xl p-8 text-center max-w-sm w-full"
            style={{
              background: '#0D0D0D',
              border: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <p className="text-sm mb-2" style={{ color: '#e5e5e5' }}>Gesture Control</p>
            <p className="text-xs mb-3" style={{ color: '#888' }}>Friday needs camera access to detect hand gestures.</p>
            <button
              onClick={requestAccess}
              className="px-6 py-2 rounded-xl text-sm transition-all hover:scale-105 active:scale-95"
              style={{
                background: 'linear-gradient(135deg, #D4A040, #B8860B)',
                color: '#000',
              }}
            >
              Grant Access
            </button>
          </div>
        </div>
      )}

      {camActive && camStatus === 'denied' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.6)' }}>
          <div
            className="rounded-2xl p-8 text-center max-w-sm w-full"
            style={{
              background: '#0D0D0D',
              border: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <p className="text-sm mb-2" style={{ color: '#e5e5e5' }}>Camera Access Denied</p>
            <p className="text-xs mb-6" style={{ color: '#888' }}>Please allow camera access in your browser settings and try again.</p>
            <button
              onClick={toggleCamera}
              className="px-6 py-2 rounded-xl text-sm transition-all hover:scale-105 active:scale-95"
              style={{ background: 'rgba(255,255,255,0.06)', color: '#999', border: '1px solid rgba(255,255,255,0.08)' }}
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      <div className="relative flex flex-col h-full" style={{ zIndex: 10 }}>
        <StatusRibbon
          systemInfo={systemInfo}
          latency={s.metrics.latency}
          orbState={s.orb}
          memory={s.metrics.memory}
          backendOnline={backendOnline}
          onCommandPalette={() => setCommandOpen(o => !o)}
        />

        <div className="flex-1 flex min-h-0">
          {sidebarOpen && (
            <LeftSidebar
              sessions={s.sessions}
              activeId={s.activeSessionId}
              onSelect={id => state.set({ activeSessionId: id })}
              onNew={handleNewSession}
              onDelete={handleDeleteSession}
              onSettings={() => state.set({ settingsOpen: true })}
              onToggleTheme={() => theme.toggle()}
              outputDir={outputDir}
              onSetOutputDir={handleSetOutputDir}
            />
          )}

          <main className="flex-1 flex flex-col min-w-0">
            <div className="flex-1 flex flex-col items-center relative min-h-0">
              <div className="w-full max-w-[720px] flex-1 flex flex-col">
                <AiCore
                  orbState={s.orb}
                  metrics={{
                    latency: s.metrics.latency,
                    model: s.metrics.model,
                    provider: s.metrics.provider,
                    memory: s.metrics.memory,
                    tokenUsage: s.metrics.tokenUsage,
                  }}
                  onCommand={sendMessage}
                  hasMessages={active.messages.length > 0}
                  handPosition={handPosition}
                />

                {active.messages.length > 0 && (
                  <div className="w-full flex-1 overflow-y-auto space-y-6 px-8 pb-4">
                    {active.messages.map((m, idx) => (
                      <MessageBubble key={m.id} message={m} index={idx} />
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>
            </div>

            <InputBar onSend={sendMessage} loading={s.loading} />
          </main>

          <IntelligencePanel
            news={news}
            weather={weather}
            stocks={stocks}
            repos={repos}
            systemInfo={systemInfo}
            recentTools={recentTools}
            loading={!dataLoaded}
            earthquakes={earthquakes}
            crypto={crypto}
            space={space}
            cve={cve}
            clocks={clocks}
          />
        </div>
      </div>

      <CommandPalette
        open={commandOpen}
        onClose={() => setCommandOpen(false)}
        commands={commandActions}
      />
    </div>
  )
}

export default App
