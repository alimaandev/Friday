import { useState, useCallback, useEffect, useRef, lazy, Suspense } from 'react'
import { theme } from './core/ThemeEngine'
import { state, useStore } from './core/StateManager'
import { LeftSidebar } from './components/sidebar/LeftSidebar'
import { StatusRibbon } from './components/topbar/TopBar'
import { AiCore } from './components/center/AiCore'
import { MessageBubble } from './components/chat/MessageBubble'
import { InputBar } from './components/chat/InputBar'
import { CameraIndicator } from './components/common/CameraIndicator'
import { useCamera } from './hooks/useCamera'
import { useHandGesture } from './hooks/useHandGesture'
import { useVoiceInput } from './hooks/useVoiceInput'
import { useVoiceOutput } from './hooks/useVoiceOutput'
import { useWakeWord } from './hooks/useWakeWord'
import type { SystemInfo, NewsItem, WeatherData, Earthquake, CryptoData, SpaceData, CveItem, WorldClock, MemoryData, ScreenData, CalendarEvent, EmailMessage, ProactiveAlert } from './types'
import { AlertToast } from './components/chat/AlertToast'
const IntelligencePanel = lazy(() => import('./components/sidebar/IntelligencePanel'))
const CommandPalette = lazy(() => import('./components/command/CommandPalette'))
const SettingsPanel = lazy(() => import('./components/settings/SettingsPanel'))
import { fetchApi, streamChat, checkHealth, getSessions, getGoogleAuth, connectEventSource } from './core/api'
import type { ServerEvent } from './core/api'

let msgId = 0
const nextId = () => `m${++msgId}`
const LANG_CYCLE = ['en-US', 'hi-IN', 'ur-PK']

function showNativeNotification(title: string, body: string) {
  if ('Notification' in window) {
    if (Notification.permission === 'granted') {
      new Notification(title, { body })
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(p => {
        if (p === 'granted') new Notification(title, { body })
      })
    }
  }
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [commandOpen, setCommandOpen] = useState(false)
  const [camActive, setCamActive] = useState(false)
  const [backendOnline, setBackendOnline] = useState(true)
  const [outputDir, setOutputDir] = useState(() => localStorage.getItem('friday_output_dir') || '')
  const [dataLoaded, setDataLoaded] = useState(false)
  const [alerts, setAlerts] = useState<ProactiveAlert[]>([])
  const [settingsOpen, setSettingsOpen] = useState(false)

  // ─── Fine-grained Zustand selectors (before any hooks that use them) ───
  const sessions = useStore(s => s.sessions)
  const activeSessionId = useStore(s => s.activeSessionId)
  const loading = useStore(s => s.loading)
  const orb = useStore(s => s.orb)
  const voiceLanguage = useStore(s => s.voiceLanguage)
  const metricsState = useStore(s => s.metrics)
  const active = useStore(s => {
    const found = s.sessions.find(ses => ses.id === s.activeSessionId)
    return found || s.sessions[0]
  })

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

  const handleGoogleConnect = useCallback(() => {
    getGoogleAuth().then(d => {
      if (d.url) {
        const popup = window.open(d.url, '_blank')
        if (!popup || popup.closed) {
          alert('Please allow popups for this site to connect Google Calendar and Email.')
        }
      }
    }).catch(() => {})
  }, [])

  const { stream, status: camStatus, requestAccess, stop: stopCam } = useCamera()
  const { openness, position: handPosition } = useHandGesture(stream, camActive)

  const {
    isSupported: voiceInputSupported,
    status: voiceInputStatus,
    interimTranscript,
    startListening: startVoiceInput,
    stopListening: stopVoiceInput,
    resetTranscript,
  } = useVoiceInput()

  const {
    enabled: voiceOutputEnabled,
    setEnabled: setVoiceOutputEnabled,
    status: voiceOutputStatus,
    speak: speakResponse,
    stop: stopVoiceOutput,
  } = useVoiceOutput()

  const {
    active: wakeWordActive,
    start: startWakeWord,
    stop: stopWakeWord,
  } = useWakeWord(() => startVoiceInput(voiceLanguage))

  useEffect(() => {
    theme.init()
  }, [])

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

  // ─── Single SSE connection replaces all polling ───
  useEffect(() => {
    let cancelled = false

    const handleEvent = (ev: ServerEvent) => {
      if (cancelled) return
      switch (ev.type) {
        case 'metrics':
          state.setMetrics({
            latency: ev.data.latency || 0,
            tokenUsage: ev.data.tokenUsage || 0,
          })
          break
        case 'system_info':
          setSystemInfo(prev => ({ ...prev, ...ev.data }))
          break
        case 'memory':
          setMemoryData(prev => prev ? { ...prev, ...ev.data } : null)
          if (ev.data.vector_count != null) {
            state.setMetrics({ memory: ev.data.vector_count })
          }
          break
        case 'alert':
          setAlerts(prev => {
            const exists = prev.some(a => a.timestamp === ev.data.timestamp && a.title === ev.data.title)
            if (exists) return prev
            const next = [ev.data, ...prev].slice(0, 5)
            if (ev.data.severity === 'warning') {
              showNativeNotification(ev.data.title, ev.data.description)
            }
            return next
          })
          break
        case 'screen':
          setScreenData(ev.data)
          break
        case 'clocks':
          setClocks(ev.data.clocks || [])
          break
      }
    }

    const unsub = connectEventSource(handleEvent, () => {
      if (!cancelled) setBackendOnline(false)
    })

    return () => { cancelled = true; unsub() }
  }, [])

  // ─── Initial data fetch (one-shot, no polling) ───
  useEffect(() => {
    let cancelled = false
    const init = async () => {
      try {
        const [health, sessions] = await Promise.all([
          checkHealth(),
          getSessions(),
        ])
        if (cancelled) return
        setBackendOnline(health.status === 'ok')

        if (sessions.sessions.length > 0) {
          const synced = sessions.sessions.map((s: any) => ({
            id: s.id,
            title: s.language === 'hinglish' ? 'Hinglish session' : 'Session',
            messages: [],
            createdAt: Date.now(),
          }))
          state.set({ sessions: synced, activeSessionId: sessions.sessions[0].id })
        } else {
          const created = await fetchApi('/api/sessions', { method: 'POST', body: JSON.stringify({}) })
          if (!cancelled) {
            state.set({
              sessions: [{ id: created.session_id, title: 'Session', messages: [], createdAt: Date.now() }],
              activeSessionId: created.session_id,
            })
          }
        }

        // Batch-fetch remaining data once (fills panels until SSE updates arrive)
        const fetchRemaining = async () => {
          const [authResp] = await Promise.all([
            getGoogleAuth(),
            fetchApi('/api/news').then(d => setNews(d.articles || [])).catch(() => {}),
            fetchApi('/api/weather').then(d => setWeather(d)).catch(() => {}),
            fetchApi('/api/stocks').then(d => setStocks(d.stocks || [])).catch(() => {}),
            fetchApi('/api/github-trending').then(d => setRepos(d.repos || [])).catch(() => {}),
            fetchApi('/api/earthquakes').then(d => setEarthquakes(d.earthquakes || [])).catch(() => {}),
            fetchApi('/api/crypto').then(d => setCrypto(d.crypto || [])).catch(() => {}),
            fetchApi('/api/space').then(d => setSpace(d)).catch(() => {}),
            fetchApi('/api/cve').then(d => setCve(d.cve || [])).catch(() => {}),
            fetchApi('/api/memory').then(d => setMemoryData(d)).catch(() => {}),
            fetchApi('/api/screen').then(d => setScreenData(d)).catch(() => {}),
          ])
          const authStatus = authResp?.status || ''
          setCalendarAuth(authStatus)
          setEmailAuth(authStatus)
          if (authStatus === 'authenticated') {
            Promise.all([
              fetchApi('/api/calendar/events').then(d => setCalendarEvents(d.events || [])).catch(() => {}),
              fetchApi('/api/email/inbox').then(d => setEmailMessages(d.messages || [])).catch(() => {}),
              fetchApi('/api/email/unread').then(d => setEmailUnread(d.unread || 0)).catch(() => {}),
            ])
          }
        }
        await fetchRemaining()
        if (!cancelled) setDataLoaded(true)
      } catch {
        if (!cancelled) setBackendOnline(false)
      }
    }
    init()
    // Fallback: stop showing skeleton after 10s even if data never arrives
    const fallback = setTimeout(() => setDataLoaded(true), 10000)
    return () => { cancelled = true; clearTimeout(fallback) }
  }, [])

  const dismissAlert = useCallback((idx: number) => {
    setAlerts(prev => prev.filter((_, i) => i !== idx))
  }, [])

  const [memoryData, setMemoryData] = useState<MemoryData | null>(null)
  const [screenData, setScreenData] = useState<ScreenData | null>(null)
  const [calendarAuth, setCalendarAuth] = useState('')
  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([])
  const [emailAuth, setEmailAuth] = useState('')
  const [emailMessages, setEmailMessages] = useState<EmailMessage[]>([])
  const [emailUnread, setEmailUnread] = useState(0)

  // Fetch output dir on session change
  useEffect(() => {
    fetchApi(`/api/output-dir?session_id=${activeSessionId}`).then((d: any) => { if (d) setOutputDir(d.output_dir) }).catch(() => {})
  }, [activeSessionId])

  // Auto-speak assistant responses when voice output is enabled
  const lastMsgRef = useRef('')
  useEffect(() => {
    if (!voiceOutputEnabled) return
    const msgs = active.messages
    if (msgs.length === 0) return
    const lastMsg = msgs[msgs.length - 1]
    if (lastMsg.role === 'assistant' && !lastMsg.streaming && lastMsg.content) {
      const content = lastMsg.content
      if (content !== lastMsgRef.current && content.length > 10) {
        lastMsgRef.current = content
        speakResponse(content)
      }
    }
  }, [active.messages, voiceOutputEnabled, speakResponse])

  const toggleCamera = useCallback(() => {
    setCamActive(prev => {
      if (prev) { stopCam(); return false }
      return true
    })
  }, [stopCam])

  const handleNewSession = useCallback(async () => {
    const curSessions = state.get().sessions
    try {
      const data = await fetchApi('/api/sessions', { method: 'POST', body: JSON.stringify({}) })
      state.set({
        sessions: [...curSessions, { id: data.session_id, title: 'Session', messages: [], createdAt: Date.now() }],
        activeSessionId: data.session_id,
      })
    } catch {
      const id = `local_${Date.now()}`
      state.set({
        sessions: [...curSessions, { id, title: 'Session (offline)', messages: [], createdAt: Date.now() }],
        activeSessionId: id,
      })
    }
  }, [])

  const handleSetOutputDir = useCallback(async (path: string) => {
    setOutputDir(path)
    localStorage.setItem('friday_output_dir', path)
    try {
      await fetchApi('/api/output-dir', { method: 'PUT', body: JSON.stringify({ session_id: state.get().activeSessionId, path }) })
    } catch {}
  }, [])

  const handleDeleteSession = useCallback((id: string) => {
    fetchApi(`/api/sessions/${id}`, { method: 'DELETE' }).catch(() => {})
    const cur = state.get()
    const next = cur.sessions.filter(x => x.id !== id)
    state.set({ sessions: next, activeSessionId: cur.activeSessionId === id ? (next[0]?.id || 'default') : cur.activeSessionId })
  }, [])

  const abortRef = useRef<AbortController | null>(null)

  const handleStop = useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    state.setLoading(false)
    state.updateMessages(msgs => msgs.map(m => m.streaming ? { ...m, streaming: false } : m))
    state.setOrb('idle')
  }, [])

  const [searchQuery, setSearchQuery] = useState('')

  const filteredMessages = searchQuery
    ? active.messages.filter(m => m.content.toLowerCase().includes(searchQuery.toLowerCase()))
    : active.messages

  const [lastUserMsg, setLastUserMsg] = useState('')
  const lastUserMsgRef = useRef('')
  useEffect(() => { lastUserMsgRef.current = lastUserMsg })
  const handleSend = useCallback(async (text: string) => {
    if (loading) return
    setLastUserMsg(text)
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    state.setLoading(true)
    state.setOrb('thinking')

    state.updateMessages(msgs => [...msgs, { id: nextId(), role: 'user', content: text }])

    const aid = nextId()
    state.updateMessages(msgs => [...msgs, { id: aid, role: 'assistant', content: '', streaming: true, toolCalls: [] }])

    let acc = ''
    let lastFlush = 0
    const TOKEN_THROTTLE = 40
    const flushTokens = () => {
      lastFlush = performance.now()
      state.updateMessages(msgs => msgs.map(m => m.id === aid ? { ...m, content: acc } : m))
    }

    const chatController = streamChat(
      { message: text, session_id: activeSessionId },
      (ev) => {
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
          case 'fast':
            state.updateMessages(msgs => msgs.map(m =>
              m.id === aid ? { ...m, content: ev.content, streaming: false, reflex: ev.reflex } : m
            ))
            state.setOrb('idle')
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
      },
      (err) => {
        const isNetwork = err?.message?.includes('network') || err?.status === 0
        if (isNetwork) setBackendOnline(false)
        state.updateMessages(msgs => msgs.map(m =>
          m.id === aid ? { ...m, content: isNetwork
            ? 'Backend offline — start `python api_server.py` on port 8080'
            : `Error: ${err.message || JSON.stringify(err)}`, streaming: false } : m
        ))
        state.setOrb('error')
        setTimeout(() => state.setOrb('idle'), 2000)
      },
      () => {
        state.setLoading(false)
        abortRef.current = null
      },
    )
    abortRef.current = chatController
  }, [loading, activeSessionId])

  // Stable ref for handleSend so effects always have the latest version
  const handleSendRef = useRef<(text: string) => void>(null as any)
  useEffect(() => { handleSendRef.current = handleSend })

  // Gesture-to-voice: open palm = start listening, fist = send
  const prevOpennessRef = useRef<number | null>(null)
  const gestureVoiceActive = useRef(false)

  useEffect(() => {
    if (!camActive || openness == null) return

    const prev = prevOpennessRef.current
    prevOpennessRef.current = openness

    if (openness > 0.7 && (prev == null || prev <= 0.5) && !gestureVoiceActive.current) {
      gestureVoiceActive.current = true
      resetTranscript()
      startVoiceInput()
      return
    }

    if (openness < 0.3 && (prev != null && prev >= 0.5) && gestureVoiceActive.current) {
      gestureVoiceActive.current = false
      const transcript = stopVoiceInput()
      if (transcript.trim()) {
        handleSendRef.current(transcript.trim())
      }
    }
  }, [camActive, openness, startVoiceInput, stopVoiceInput, resetTranscript])

  const sendMessage = useCallback((text: string) => {
    if (!text.trim() || loading) return
    handleSend(text)
  }, [loading, handleSend])

  const handleRegenerate = useCallback(() => {
    const msg = lastUserMsgRef.current
    if (!msg || state.get().loading) return
    state.updateMessages(msgs => {
      const idx = msgs.findLastIndex(m => m.role === 'assistant')
      if (idx === -1) return msgs
      return msgs.slice(0, idx)
    })
    handleSendRef.current(msg)
  }, [])

  /* Collect recent tool calls for Agent Activity panel */
  const recentTools = active.messages.flatMap(m => (m.toolCalls || [])).slice(-8)

  const handleToggleVoiceOutput = useCallback(() => {
    const next = !voiceOutputEnabled
    setVoiceOutputEnabled(next)
    state.set({ voiceOutputEnabled: next })
    if (!next) stopVoiceOutput()
  }, [voiceOutputEnabled, setVoiceOutputEnabled, stopVoiceOutput])

  const handleCycleLanguage = useCallback(() => {
    const current = state.get().voiceLanguage
    const idx = LANG_CYCLE.indexOf(current)
    const next = LANG_CYCLE[(idx + 1) % LANG_CYCLE.length]
    state.setVoiceLanguage(next)
  }, [])

  const commandActions = [
    { id: 'new-session', label: 'New session', action: handleNewSession },
    { id: 'toggle-sidebar', label: 'Toggle sessions sidebar', action: () => setSidebarOpen(o => !o) },

    { id: 'toggle-camera', label: 'Gesture control', action: toggleCamera },
    { id: 'toggle-voice-output', label: 'Toggle voice output', action: handleToggleVoiceOutput },
    { id: 'cycle-language', label: `Voice language: ${voiceLanguage}`, action: handleCycleLanguage },
  ]

  if (voiceInputSupported) {
    commandActions.push(
      { id: 'voice-input', label: 'Voice input (hold mic)', action: () => startVoiceInput() },
    )
  }

  if (wakeWordActive) {
    commandActions.push(
      { id: 'stop-wake-word', label: 'Disable wake word', action: stopWakeWord },
    )
  } else if (voiceInputSupported) {
    commandActions.push(
      { id: 'start-wake-word', label: 'Enable wake word ("Hey Friday")', action: startWakeWord },
    )
  }

  return (
    <div className="h-full flex flex-col" style={{ background: 'var(--bg)' }}>
      {!backendOnline && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl text-xs"
          style={{ background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5' }}
        >
          Backend offline — start <code style={{ color: '#fbbf24' }}>python api_server.py</code> on port 8080
        </div>
      )}

      {/* Proactive alerts */}
      {alerts.length > 0 && (
        <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
          {alerts.map((a, i) => (
            <AlertToast key={a.timestamp + '-' + i} alert={a} onDismiss={() => dismissAlert(i)} />
          ))}
        </div>
      )}

      <CameraIndicator
        stream={camActive ? stream : null}
        active={camActive}
        openness={openness}
        onToggle={toggleCamera}
        voiceInputStatus={voiceInputStatus}
        voiceOutputStatus={voiceOutputStatus}
      />

      {camActive && camStatus === 'idle' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.6)' }}>
          <div className="rounded-2xl p-8 text-center max-w-sm w-full glass blue-glow">
            <p className="text-sm mb-2" style={{ color: '#e5e5e5' }}>Gesture Control</p>
            <p className="text-xs mb-3" style={{ color: '#a0a0a8' }}>Friday needs camera access to detect hand gestures.</p>
            <button
              onClick={requestAccess}
              className="px-6 py-2 rounded-xl text-sm transition-all hover:scale-105 active:scale-95"
              style={{
                background: 'linear-gradient(135deg, var(--gold), var(--gold-bright))',
                color: '#000',
                fontWeight: 500,
              }}
            >
              Grant Access
            </button>
          </div>
        </div>
      )}

      {camActive && camStatus === 'denied' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.6)' }}>
          <div className="rounded-2xl p-8 text-center max-w-sm w-full glass">
            <p className="text-sm mb-2" style={{ color: '#e5e5e5' }}>Camera Access Denied</p>
            <p className="text-xs mb-6" style={{ color: '#a0a0a8' }}>Allow camera access in browser settings and try again.</p>
            <button
              onClick={toggleCamera}
              className="px-6 py-2 rounded-xl text-sm transition-all hover:scale-105 active:scale-95 glass glass-hover"
              style={{ color: '#a0a0a8' }}
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      <div className="relative flex flex-col h-full" style={{ zIndex: 10 }}>
        <StatusRibbon
          systemInfo={systemInfo}
          latency={metricsState.latency}
          orbState={orb}
          memory={metricsState.memory}
          backendOnline={backendOnline}
          onCommandPalette={() => setCommandOpen(o => !o)}
          voiceOutputEnabled={voiceOutputEnabled}
          onToggleVoiceOutput={handleToggleVoiceOutput}
          voiceInputStatus={voiceInputStatus}
          voiceOutputStatus={voiceOutputStatus}
        />

        <div className="flex-1 flex min-h-0">
          {sidebarOpen && (
            <LeftSidebar
              sessions={sessions}
              activeId={activeSessionId}
              onSelect={id => state.set({ activeSessionId: id })}
              onNew={handleNewSession}
              onDelete={handleDeleteSession}
              onSettings={() => setSettingsOpen(true)}
              outputDir={outputDir}
              onSetOutputDir={handleSetOutputDir}
            />
          )}

          <main className="flex-1 flex flex-col min-w-0">
            <div className="flex-1 flex flex-col items-center relative min-h-0">
              <div className="w-full max-w-[720px] flex-1 flex flex-col">
                <AiCore
                  orbState={orb}
                  metrics={{
                    latency: metricsState.latency,
                    model: metricsState.model,
                    provider: metricsState.provider,
                    memory: metricsState.memory,
                    tokenUsage: metricsState.tokenUsage,
                  }}
                  onCommand={sendMessage}
                  hasMessages={active.messages.length > 0}
                  handPosition={handPosition}
                  voiceActivity={voiceInputStatus === 'listening' || voiceOutputStatus === 'speaking'}
                />

                {active.messages.length > 0 && (
                  <div className="w-full flex-1 overflow-y-auto space-y-6 px-8 pb-4">
                    {active.messages.length > 1 && (
                      <div className="sticky top-0 z-10 pb-2" style={{ background: 'var(--bg)' }}>
                        <input
                          value={searchQuery}
                          onChange={e => setSearchQuery(e.target.value)}
                          placeholder="Search messages..."
                          className="w-full rounded-xl px-3 py-2 text-xs outline-none transition-all"
                          style={{
                            background: 'rgba(255,255,255,0.04)',
                            border: searchQuery ? '1px solid rgba(212,160,64,0.2)' : '1px solid rgba(255,255,255,0.06)',
                            color: '#999',
                          }}
                        />
                      </div>
                    )}
                    {filteredMessages.length === 0 && searchQuery && (
                      <div className="text-center py-8 text-xs" style={{ color: '#666' }}>No messages match "{searchQuery}"</div>
                    )}
                    {filteredMessages.map((m, idx) => (
                      <MessageBubble
                        key={m.id}
                        message={m}
                        index={idx}
                        onRegenerate={m.role === 'assistant' && !m.streaming ? handleRegenerate : undefined}
                        onStop={m.role === 'assistant' && m.streaming ? handleStop : undefined}
                      />
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>
            </div>

            <InputBar
              onSend={sendMessage}
              loading={loading}
              onVoiceStart={() => { resetTranscript(); startVoiceInput(voiceLanguage) }}
              onVoiceStop={() => stopVoiceInput()}
              voiceStatus={voiceInputStatus}
              voiceInterim={interimTranscript}
              isVoiceSupported={voiceInputSupported}
              voiceLanguage={voiceLanguage}
              onCycleLanguage={handleCycleLanguage}
            />
          </main>

          <Suspense fallback={<div className="w-80 shrink-0" />}>
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
              memoryData={memoryData}
              screenData={screenData}
              calendarEvents={calendarEvents}
              calendarAuth={calendarAuth}
              emailMessages={emailMessages}
              emailUnread={emailUnread}
              emailAuth={emailAuth}
              onCalendarConnect={handleGoogleConnect}
              onEmailConnect={handleGoogleConnect}
            />
          </Suspense>
        </div>
      </div>

      <Suspense fallback={null}>
        <CommandPalette
          open={commandOpen}
          onClose={() => setCommandOpen(false)}
          commands={commandActions}
        />
      </Suspense>

      {settingsOpen && (
        <Suspense fallback={null}>
        <SettingsPanel
          onClose={() => setSettingsOpen(false)}
          voiceOutputEnabled={voiceOutputEnabled}
          onToggleVoiceOutput={handleToggleVoiceOutput}
          voiceLanguage={voiceLanguage}
          onCycleLanguage={handleCycleLanguage}
          wakeWordActive={wakeWordActive}
          onToggleWakeWord={wakeWordActive ? stopWakeWord : startWakeWord}
          camActive={camActive}
          onToggleCamera={toggleCamera}
          backendOnline={backendOnline}
          calendarAuth={calendarAuth}
          emailAuth={emailAuth}
          onGoogleConnect={handleGoogleConnect}
        />
        </Suspense>
      )}
    </div>
  )
}

export default App
