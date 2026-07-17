import type { DesignTokens } from '../types'

export const lightTokens: DesignTokens = {
  colors: {
    bg: '#f5f5f5',
    surface: '#ffffff',
    surfaceElevated: '#ffffff',
    border: '#e0e0e0',
    text: '#000000',
    textSecondary: '#666666',
    textTertiary: '#999999',
    accent: '#d97706',
    accentDim: '#b45309',
    accentGlow: 'rgba(217, 119, 6, 0.12)',
    warning: '#f97316',
    error: '#dc2626',
    success: '#16a34a',
    orb: {
      primary: '#fef3c7',
      secondary: '#fde68a',
      accent: '#f59e0b',
      glow: 'rgba(245, 158, 11, 0.1)',
      pulse: 'rgba(245, 158, 11, 0.2)',
    },
    glass: 'rgba(255, 255, 255, 0.4)',
    glassBorder: 'rgba(0, 0, 0, 0.04)',
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
