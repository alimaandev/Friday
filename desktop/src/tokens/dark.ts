import type { DesignTokens } from '../types'

export const darkTokens: DesignTokens = {
  colors: {
    bg: '#000000',
    surface: '#0a0a0a',
    surfaceElevated: '#141414',
    border: '#1a1a1a',
    text: '#ffffff',
    textSecondary: '#888888',
    textTertiary: '#444444',
    accent: '#00a8ff',
    accentDim: '#0066cc',
    accentGlow: 'rgba(0, 168, 255, 0.2)',
    warning: '#f97316',
    error: '#ef4444',
    success: '#22c55e',
    orb: {
      primary: '#0033aa',
      secondary: '#001a55',
      accent: '#00bbff',
      glow: 'rgba(0, 180, 255, 0.15)',
      pulse: 'rgba(0, 100, 255, 0.35)',
    },
    glass: 'rgba(10, 10, 10, 0.5)',
    glassBorder: 'rgba(255, 255, 255, 0.04)',
  },
  spacing: { xs: 4, sm: 8, md: 16, lg: 24, xl: 32, '2xl': 48 },
  radius: { sm: 4, md: 8, lg: 12, xl: 16, full: 9999 },
  blur: { sm: 'blur(4px)', md: 'blur(12px)', lg: 'blur(24px)', xl: 'blur(48px)' },
  typography: {
    fontFamily: "'Inter', -apple-system, system-ui, sans-serif",
    fontMono: "'JetBrains Mono', 'Fira Code', monospace",
    sizes: { xs: '10px', sm: '12px', base: '14px', lg: '16px', xl: '20px', '2xl': '28px', '3xl': '36px' },
  },
}
