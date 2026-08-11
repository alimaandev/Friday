import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SettingsPanel } from '../components/settings/SettingsPanel'

vi.mock('../core/api', () => ({
  getPlugins: vi.fn().mockResolvedValue([
    { name: 'run_command', builtin: true, installed: true, enabled: true, description: '' },
    { name: 'fun', builtin: false, installed: false, enabled: false, description: 'Community tool plugin.' },
  ]),
  installPlugin: vi.fn().mockResolvedValue({ success: true, message: 'installed fun' }),
  uninstallPlugin: vi.fn().mockResolvedValue({ success: true, message: 'uninstalled fun' }),
}))

const baseProps = {
  onClose: () => {},
  voiceOutputEnabled: false,
  onToggleVoiceOutput: () => {},
  voiceLanguage: 'English',
  onCycleLanguage: () => {},
  wakeWordActive: false,
  onToggleWakeWord: () => {},
  camActive: false,
  onToggleCamera: () => {},
  backendOnline: true,
  calendarAuth: '',
  emailAuth: '',
  onGoogleConnect: () => {},
  persona: 'friday',
  onSetPersona: () => {},
}

describe('SettingsPanel', () => {
  it('renders plugin marketplace section', async () => {
    render(<SettingsPanel {...baseProps} />)
    expect(screen.getByText('PLUGINS')).toBeTruthy()
    expect(await screen.findByText('fun')).toBeTruthy()
    expect(screen.getByText('Install')).toBeTruthy()
    expect(screen.getByText('active')).toBeTruthy()
  })
})
