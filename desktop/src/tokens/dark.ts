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
    accent: '#f59e0b',
    accentDim: '#b45309',
    accentGlow: 'rgba(245, 158, 11, 0.2)',
    warning: '#f97316',
    error: '#ef4444',
    success: '#22c55e',
    orb: {
      primary: '#442200',
      secondary: '#221100',
      accent: '#ffb800',
      glow: 'rgba(255, 184, 0, 0.12)',
      pulse: 'rgba(255, 140, 0, 0.35)',
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
