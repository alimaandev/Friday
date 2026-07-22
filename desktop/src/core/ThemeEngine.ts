import type { DesignTokens, ThemeMode } from '../types'
import { darkTokens } from '../tokens/dark'
import { EventBus } from './EventBus'

class ThemeEngine {
  private mode: ThemeMode = 'dark'
  private tokens: DesignTokens = darkTokens

  init() {
    this.set('dark')
  }

  get(): DesignTokens {
    return this.tokens
  }

  getMode(): ThemeMode {
    return this.mode
  }

  set(mode: ThemeMode) {
    this.mode = mode
    this.tokens = darkTokens
    if (typeof document !== 'undefined') {
      document.documentElement.classList.add('dark')
      localStorage.setItem('friday-theme', mode)
    }
    this.applyCSSVariables()
    EventBus.get().emit('theme:change', mode)
  }

  private applyCSSVariables() {
    if (typeof document === 'undefined') return
    const c = this.tokens.colors
    const root = document.documentElement
    const set = (name: string, val: string) => root.style.setProperty(`--${name}`, val)
    set('bg', c.bg)
    set('surface', c.surface)
    set('surface-elevated', c.surfaceElevated)
    set('border', c.border)
    set('text', c.text)
    set('text-secondary', c.textSecondary)
    set('text-tertiary', c.textTertiary)
    set('accent', c.accent)
    set('accent-dim', c.accentDim)
    set('accent-glow', c.accentGlow)
    set('warning', c.warning)
    set('error', c.error)
    set('success', c.success)
    set('glass', c.glass)
    set('glass-border', c.glassBorder)
    set('orb-primary', c.orb.primary)
    set('orb-secondary', c.orb.secondary)
    set('orb-accent', c.orb.accent)
    set('orb-glow', c.orb.glow)
    set('orb-pulse', c.orb.pulse)
  }
}

export const theme = new ThemeEngine()
