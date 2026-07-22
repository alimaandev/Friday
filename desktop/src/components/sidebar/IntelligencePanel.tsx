import { memo } from 'react'
import type { MemoryData, NewsItem, WeatherData, SystemInfo, Earthquake, CryptoData, SpaceData, CveItem, WorldClock, ScreenData, CalendarEvent, EmailMessage } from '../../types'
import { WEATHER_CODES } from '../../types'
import { SkeletonSection } from '../common/Skeleton'
import { MemoryPanel } from './MemoryPanel'
import { ScreenPanel } from './ScreenPanel'
import { CalendarPanel } from './CalendarPanel'
import { EmailPanel } from './EmailPanel'

interface StockData {
  symbol: string; price: number; change: number; change_pct: number; sparkline: number[]
}
interface RepoData {
  name: string; url: string; description: string; stars: number; language: string
}
interface ToolCallEntry {
  name: string; args: string; result: string
}

interface IntelligencePanelProps {
  news: NewsItem[]
  weather: WeatherData | null
  stocks: StockData[]
  repos: RepoData[]
  systemInfo: SystemInfo
  recentTools: ToolCallEntry[]
  loading?: boolean
  earthquakes?: Earthquake[]
  crypto?: CryptoData[]
  space?: SpaceData | null
  cve?: CveItem[]
  clocks?: WorldClock[]
  memoryData?: MemoryData | null
  screenData?: ScreenData | null
  calendarEvents?: CalendarEvent[]
  calendarAuth?: string
  emailMessages?: EmailMessage[]
  emailUnread?: number
  emailAuth?: string
  onCalendarConnect?: () => void
  onEmailConnect?: () => void
}

const timeAgo = (dateStr: string) => {
  const diff = Date.now() - new Date(dateStr).getTime()
  if (diff < 60000) return 'now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`
  return `${Math.floor(diff / 86400000)}d`
}

const LANG_COLORS: Record<string, string> = {
  TypeScript: '#3178c6', JavaScript: '#f1e05a', Python: '#3572A5', Go: '#00ADD8',
  Rust: '#dea584', 'C++': '#f34b7d', Java: '#b07219',
}

function Label({ children }: { children: React.ReactNode }) {
  return <div className="text-[10px] tracking-[0.2em] mb-2 px-3" style={{ color: '#666' }}>{children}</div>
}

/* ─── World Clocks ─── */

const ClocksSection = memo(function ClocksSection({ clocks }: { clocks: WorldClock[] }) {
  if (clocks.length === 0) return null
  return (
    <>
      <Label>🕐 WORLD CLOCKS</Label>
      <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 px-2 text-[11px]">
        {clocks.map(c => (
          <div key={c.zone} className="flex items-center justify-between px-2 py-1 rounded" style={{ background: 'rgba(255,255,255,0.02)' }}>
            <span style={{ color: '#888' }}>{c.zone}</span>
            <span className="font-mono" style={{ color: '#ccc' }}>{c.time}</span>
          </div>
        ))}
      </div>
    </>
  )
})

/* ─── Earthquakes ─── */

const EarthquakesSection = memo(function EarthquakesSection({ earthquakes }: { earthquakes: Earthquake[] }) {
  if (earthquakes.length === 0) return null
  return (
    <>
      <Label>🌍 EARTHQUAKES</Label>
      <div className="space-y-0.5 px-2 text-xs">
        {earthquakes.map((eq, i) => (
          <a key={i} href={eq.url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 px-2 py-1 rounded-lg transition-all hover:bg-white/[.03]"
          >
            <span className="font-mono shrink-0" style={{ color: eq.mag >= 5 ? '#ef4444' : eq.mag >= 4 ? '#f59e0b' : '#888' }}>
              M{eq.mag.toFixed(1)}
            </span>
            <span className="flex-1 truncate" style={{ color: '#ccc' }}>{eq.place}</span>
            <span className="text-[10px] shrink-0" style={{ color: '#666' }}>{timeAgo(eq.time)}</span>
          </a>
        ))}
      </div>
    </>
  )
})

/* ─── Crypto ─── */

const CryptoSections = memo(function CryptoSections({ crypto }: { crypto: CryptoData[] }) {
  if (crypto.length === 0) return null
  return (
    <>
      <Label>₿ CRYPTO</Label>
      <div className="space-y-0.5 px-2">
        {crypto.map(c => {
          const up = c.change_24h >= 0
          return (
            <div key={c.symbol} className="flex items-center gap-2 px-2 py-1 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)' }}>
              <span className="text-xs w-14 shrink-0 font-medium" style={{ color: '#ccc' }}>{c.symbol}</span>
              <span className="text-xs font-mono flex-1" style={{ color: '#e5e5e5' }}>${c.price.toLocaleString()}</span>
              <span className="text-[11px] font-mono" style={{ color: up ? '#22c55e' : '#ef4444' }}>
                {up ? '+' : ''}{c.change_24h}%
              </span>
            </div>
          )
        })}
      </div>
    </>
  )
})

/* ─── Space ─── */

const SpaceSection = memo(function SpaceSection({ space }: { space: SpaceData | null }) {
  if (!space) return null
  return (
    <>
      <Label>🛰 SPACE</Label>
      <div className="px-2 space-y-1 text-[11px]">
        <div className="flex items-center justify-between px-2 py-1 rounded" style={{ background: 'rgba(255,255,255,0.02)' }}>
          <span style={{ color: '#888' }}>ISS</span>
          <span className="font-mono" style={{ color: '#ccc' }}>{space.iss_lat.toFixed(1)}°N {space.iss_lon.toFixed(1)}°E</span>
        </div>
        <div className="flex items-center justify-between px-2 py-1 rounded" style={{ background: 'rgba(255,255,255,0.02)' }}>
          <span style={{ color: '#888' }}>Astronauts</span>
          <span className="font-mono" style={{ color: '#ccc' }}>{space.astronauts}</span>
        </div>
      </div>
    </>
  )
})

/* ─── CVE ─── */

const CveSection = memo(function CveSection({ cve }: { cve: CveItem[] }) {
  if (cve.length === 0) return null
  return (
    <>
      <Label>🔐 SECURITY</Label>
      <div className="space-y-0.5 px-2">
        {cve.map(c => (
          <div key={c.id} className="flex items-center gap-2 px-2 py-1 rounded-lg text-xs" style={{ background: 'rgba(255,255,255,0.02)' }}>
            <span className="font-mono shrink-0 text-[10px]" style={{
              color: c.severity === 'CRITICAL' ? '#ef4444' : c.severity === 'HIGH' ? '#f59e0b' : '#888'
            }}>
              {c.severity === 'CRITICAL' ? 'CRIT' : c.severity}
            </span>
            <span className="font-mono shrink-0 text-[10px]" style={{ color: '#666' }}>{c.score}</span>
            <span className="flex-1 truncate" style={{ color: '#aaa' }} title={c.description}>{c.id}</span>
          </div>
        ))}
      </div>
    </>
  )
})

/* ─── World News ─── */

const NewsSection = memo(function NewsSection({ news }: { news: NewsItem[] }) {
  if (news.length === 0) return null
  return (
    <>
      <Label>📰 WORLD NEWS</Label>
      <div className="space-y-0.5 px-2">
        {news.slice(0, 5).map((item, i) => (
          <a key={i} href={item.url} target="_blank" rel="noopener noreferrer"
            className="flex items-start gap-2.5 rounded-lg px-2 py-1.5 transition-all hover:bg-white/[.03]"
          >
            {item.image ? (
              <img src={item.image} alt="" className="w-7 h-7 rounded object-cover shrink-0 mt-0.5"
                onError={e => { (e.target as HTMLImageElement).style.display = 'none' }} />
            ) : (
              <div className="w-7 h-7 rounded shrink-0 mt-0.5 flex items-center justify-center text-[10px]"
                style={{ background: 'rgba(255,255,255,0.04)' }}>📰</div>
            )}
            <div className="min-w-0 flex-1">
              <div className="text-xs leading-snug line-clamp-2" style={{ color: '#ccc' }}>{item.title}</div>
              <div className="flex items-center gap-2 text-[10px] mt-0.5" style={{ color: '#666' }}>
                <span style={{ color: '#D4A040' }}>{item.source}</span>
                <span>{timeAgo(item.time)}</span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </>
  )
})

/* ─── Markets ─── */

const MarketsSection = memo(function MarketsSection({ stocks }: { stocks: StockData[] }) {
  if (stocks.length === 0) return null
  return (
    <>
      <Label>📈 MARKETS</Label>
      <div className="space-y-0.5 px-2">
        {stocks.map(s => {
          const up = s.change >= 0
          return (
            <div key={s.symbol} className="flex items-center gap-2 px-2 py-1 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)' }}>
              <span className="text-xs w-12 shrink-0" style={{ color: '#ccc' }}>{s.symbol}</span>
              <span className="text-xs font-mono flex-1" style={{ color: '#e5e5e5' }}>${s.price.toFixed(2)}</span>
              <span className="text-[11px] font-mono" style={{ color: up ? '#22c55e' : '#ef4444' }}>
                {up ? '+' : ''}{s.change_pct.toFixed(1)}%
              </span>
            </div>
          )
        })}
      </div>
    </>
  )
})

/* ─── GitHub ─── */

const GitHubSection = memo(function GitHubSection({ repos }: { repos: RepoData[] }) {
  if (repos.length === 0) return null
  return (
    <>
      <Label>💻 GITHUB</Label>
      <div className="space-y-0.5 px-2">
        {repos.slice(0, 5).map(r => (
          <a key={r.name} href={r.url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 px-2 py-1 rounded-lg transition-all hover:bg-white/[.03]"
          >
            <span className="text-xs flex-1 truncate" style={{ color: '#ccc' }}>{r.name}</span>
            {r.language && (
              <span className="flex items-center gap-1 text-[10px]" style={{ color: '#888' }}>
                <span className="w-2 h-2 rounded-full inline-block" style={{ background: LANG_COLORS[r.language] || '#666' }} />
                {r.language}
              </span>
            )}
            <span className="text-[10px]" style={{ color: '#D4A040' }}>★{r.stars.toLocaleString()}</span>
          </a>
        ))}
      </div>
    </>
  )
})

/* ─── Weather ─── */

const WeatherSection = memo(function WeatherSection({ weather }: { weather: WeatherData | null }) {
  if (!weather) return null
  const wc = WEATHER_CODES[weather.weather_code]
  return (
    <>
      <Label>🌤 WEATHER</Label>
      <div className="flex items-center gap-3 px-2 py-2 mx-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)' }}>
        <span className="text-2xl">{wc?.icon || '☀️'}</span>
        <div>
          <div className="text-base font-light" style={{ color: '#e5e5e5' }}>{Math.round(weather.temperature)}°C</div>
          <div className="text-[11px]" style={{ color: '#888' }}>{wc?.label || 'Unknown'}</div>
        </div>
        <div className="ml-auto text-[10px] space-y-0.5 text-right" style={{ color: '#777' }}>
          <div>{Math.round(weather.feels_like)}° feels</div>
          <div>{weather.humidity}% hum</div>
          <div>{weather.wind_speed} km/h</div>
        </div>
      </div>
    </>
  )
})

/* ─── System ─── */

const SystemSection = memo(function SystemSection({ info }: { info: SystemInfo }) {
  return (
    <>
      <Label>🖧 SYSTEM</Label>
      <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[11px] px-3">
        <span style={{ color: '#888' }}>Host</span>
        <span className="text-right font-mono truncate" style={{ color: '#ccc' }}>{info.hostname}</span>
        <span style={{ color: '#888' }}>Uptime</span>
        <span className="text-right font-mono" style={{ color: '#ccc' }}>{Math.round(info.uptime_seconds / 60)}m</span>
        <span style={{ color: '#888' }}>CPU</span>
        <span className="text-right font-mono" style={{ color: '#ccc' }}>{info.cpu_cores}c</span>
        <span style={{ color: '#888' }}>Model</span>
        <span className="text-right font-mono truncate" style={{ color: '#ccc' }}>{info.model}</span>
        <span style={{ color: '#888' }}>Calls</span>
        <span className="text-right font-mono" style={{ color: '#ccc' }}>{info.llm_calls}</span>
        <span style={{ color: '#888' }}>Tokens</span>
        <span className="text-right font-mono" style={{ color: '#ccc' }}>{info.tokens_used.toLocaleString()}</span>
      </div>
    </>
  )
})

/* ─── Agent Activity ─── */

const toolIcon = (name: string) => {
  const n = name.toLowerCase()
  if (n.includes('search') || n.includes('web')) return '🌐'
  if (n.includes('code') || n.includes('file') || n.includes('write')) return '📝'
  if (n.includes('read') || n.includes('browse')) return '📖'
  if (n.includes('analyze') || n.includes('parse')) return '🔍'
  if (n.includes('execute') || n.includes('cmd') || n.includes('bash')) return '⚡'
  return '🔧'
}

const AgentActivitySection = memo(function AgentActivitySection({ tools }: { tools: ToolCallEntry[] }) {
  if (tools.length === 0) return null
  return (
    <>
      <Label>⚡ AGENT</Label>
      <div className="space-y-0.5 max-h-[160px] overflow-y-auto px-2" style={{ scrollbarWidth: 'thin' }}>
        {tools.slice(-6).reverse().map((t, i) => {
          const isErr = t.result.startsWith('{"error"')
          return (
            <div key={i} className="flex items-center gap-2 px-2 py-1 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)' }}>
              <span className="text-[11px] shrink-0">{toolIcon(t.name)}</span>
              <span className="text-[11px] flex-1 truncate" style={{ color: '#ccc' }}>{t.name}</span>
              <span className="text-[10px] shrink-0" style={{ color: isErr ? '#ef4444' : '#22c55e' }}>{isErr ? '✗' : '✓'}</span>
            </div>
          )
        })}
      </div>
    </>
  )
})

/* ─── Intelligence Panel ─── */
function PanelCell({ children, index = 0 }: { children: React.ReactNode; index?: number }) {
  const delay = Math.min(index * 40, 200)
  return (
    <div
      className="rounded-lg py-3 glass animate-slide-in-up"
      style={{ border: '1px solid var(--glass-border)', animationDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}

export const IntelligencePanel = memo(function IntelligencePanel({
  news, weather, stocks, repos, systemInfo, recentTools, loading,
  earthquakes, crypto, space, cve, clocks, memoryData, screenData,
  calendarEvents, calendarAuth, emailMessages, emailUnread, emailAuth,
  onCalendarConnect, onEmailConnect,
}: IntelligencePanelProps) {
  return (
    <div
      className="w-[640px] flex flex-col h-full shrink-0 overflow-y-auto glass"
      style={{
        borderLeft: '1px solid var(--glass-border)',
        scrollbarWidth: 'thin',
      }}
    >
      <div className="flex items-center justify-between px-5 h-10 shrink-0" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <span className="text-[11px] font-medium tracking-[0.2em]" style={{ color: '#666' }}>
          INTELLIGENCE
        </span>
      </div>

      <div className="flex-1 p-4 overflow-y-auto intel-scroll" style={{ scrollbarWidth: 'thin' }}>
        {loading ? (
          <div className="grid grid-cols-2 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonSection key={i} />)}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {!news.length && !weather && !stocks.length && !repos.length && !earthquakes?.length && !crypto?.length && !space && !cve?.length && !clocks?.length && (
              <div className="col-span-2 flex flex-col items-center justify-center py-16 text-xs" style={{ color: '#666' }}>
                <span className="text-2xl mb-2">📡</span>
                <span>Connect backend on port 8080</span>
                <span className="text-[10px] mt-1" style={{ color: '#444' }}>python api_server.py</span>
              </div>
            )}
            <div className="space-y-4">
              <PanelCell><ClocksSection clocks={clocks || []} /></PanelCell>
              <PanelCell><NewsSection news={news} /></PanelCell>
              <PanelCell><MarketsSection stocks={stocks} /></PanelCell>
              <PanelCell><SystemSection info={systemInfo} /></PanelCell>
            </div>
            <div className="space-y-4">
              <PanelCell><EarthquakesSection earthquakes={earthquakes || []} /></PanelCell>
              <PanelCell><CryptoSections crypto={crypto || []} /></PanelCell>
              <PanelCell>
                <SpaceSection space={space || null} />
                <div className="h-3" />
                <WeatherSection weather={weather} />
              </PanelCell>
              <PanelCell>
                <GitHubSection repos={repos} />
                <div className="h-3" />
                <CveSection cve={cve || []} />
              </PanelCell>
              <PanelCell>
                <CalendarPanel events={calendarEvents || []} authStatus={calendarAuth || ''} onConnect={onCalendarConnect} />
              </PanelCell>
              <PanelCell>
                <EmailPanel messages={emailMessages || []} unread={emailUnread || 0} authStatus={emailAuth || ''} onConnect={onEmailConnect} />
              </PanelCell>
              <PanelCell><AgentActivitySection tools={recentTools} /></PanelCell>
            </div>
          </div>
        )}
        {screenData !== undefined && (
          <div className="mt-4">
            <ScreenPanel data={screenData} />
          </div>
        )}
        {memoryData !== undefined && (
          <div className="mt-4">
            <MemoryPanel data={memoryData} />
          </div>
        )}
      </div>
    </div>
  )
})
