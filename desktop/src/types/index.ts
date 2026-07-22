export type OrbState = 'idle' | 'listening' | 'thinking' | 'reasoning' | 'executing' | 'searching' | 'coding' | 'speaking' | 'error' | 'offline'

export type ThemeMode = 'dark'

export interface SystemMetrics {
  cpu: number
  memory: number
  latency: number
  contextWindow: number
  tokenUsage: number
  model: string
  provider: string
}

export interface Session {
  id: string
  title: string
  messages: Message[]
  createdAt: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  plan?: string
  toolCalls?: ToolCall[]
  streaming?: boolean
  reflex?: string
}

export interface ToolCall {
  name: string
  args: string
  result: string
}

export interface NewsItem {
  title: string
  url: string
  image?: string
  source: string
  time: string
}

export interface WeatherData {
  temperature: number
  feels_like: number
  humidity: number
  wind_speed: number
  weather_code: number
  location: string
}

export interface SystemInfo {
  hostname: string
  os: string
  cpu_cores: number
  python_version: string
  uptime_seconds: number
  llm_calls: number
  tokens_used: number
  failures: number
  retries: number
  model: string
  provider: string
}

export const WEATHER_CODES: Record<number, { label: string; icon: string }> = {
  0:  { label: "Clear", icon: "☀️" },
  1:  { label: "Mainly clear", icon: "🌤️" },
  2:  { label: "Partly cloudy", icon: "⛅" },
  3:  { label: "Overcast", icon: "☁️" },
  45: { label: "Foggy", icon: "🌫️" },
  48: { label: "Depositing rime fog", icon: "🌫️" },
  51: { label: "Light drizzle", icon: "🌦️" },
  53: { label: "Moderate drizzle", icon: "🌦️" },
  55: { label: "Dense drizzle", icon: "🌧️" },
  61: { label: "Slight rain", icon: "🌦️" },
  63: { label: "Moderate rain", icon: "🌧️" },
  65: { label: "Heavy rain", icon: "🌧️" },
  71: { label: "Slight snow", icon: "🌨️" },
  73: { label: "Moderate snow", icon: "🌨️" },
  75: { label: "Heavy snow", icon: "❄️" },
  80: { label: "Slight rain showers", icon: "🌦️" },
  81: { label: "Moderate rain showers", icon: "🌧️" },
  82: { label: "Violent rain showers", icon: "🌧️" },
  95: { label: "Thunderstorm", icon: "⛈️" },
  96: { label: "Thunderstorm with slight hail", icon: "⛈️" },
  99: { label: "Thunderstorm with heavy hail", icon: "⛈️" },
}

export interface Earthquake {
  mag: number
  place: string
  time: string
  depth: number
  url: string
}

export interface CryptoData {
  symbol: string
  name: string
  price: number
  change_24h: number
  market_cap: number
}

export interface SpaceData {
  iss_lat: number
  iss_lon: number
  astronauts: number
  astronaut_names: string[]
}

export interface CalendarEvent {
  summary: string
  start: string
  end: string
  location?: string
}

export interface EmailMessage {
  id: string
  from: string
  subject: string
  date: string
  snippet: string
}

export interface ScreenData {
  image: string
  width: number
  height: number
  timestamp: number
}

export interface MemoryItem {
  id: string
  text: string
  score?: number
  metadata?: Record<string, any>
  created_at: number
}

export interface MemoryData {
  vector_memories: MemoryItem[]
  embedding_memories?: MemoryItem[]
  key_memories: { key: string; importance: number; score: number; summary: string }[]
  vector_count: number
  embedding_count?: number
  key_count: number
}

export interface CveItem {
  id: string
  severity: string
  score: number
  description: string
  published: string
}

export interface WorldClock {
  zone: string
  time: string
  offset: string
}

export interface ProactiveAlert {
  type: string
  title: string
  description: string
  severity: string
  action_label?: string
  action_payload?: Record<string, any>
  timestamp: number
}

export interface DesignTokens {
  colors: {
    bg: string
    surface: string
    surfaceElevated: string
    border: string
    text: string
    textSecondary: string
    textTertiary: string
    accent: string
    accentDim: string
    accentGlow: string
    warning: string
    error: string
    success: string
    orb: {
      primary: string
      secondary: string
      accent: string
      glow: string
      pulse: string
    }
    glass: string
    glassBorder: string
  }
  spacing: {
    xs: number
    sm: number
    md: number
    lg: number
    xl: number
    '2xl': number
  }
  radius: {
    sm: number
    md: number
    lg: number
    xl: number
    full: number
  }
  blur: {
    sm: string
    md: string
    lg: string
    xl: string
  }
  typography: {
    fontFamily: string
    fontMono: string
    sizes: {
      xs: string
      sm: string
      base: string
      lg: string
      xl: string
      '2xl': string
      '3xl': string
    }
  }
}
