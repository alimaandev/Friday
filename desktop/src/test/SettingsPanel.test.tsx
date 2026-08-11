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
  getCustomTools: vi.fn().mockResolvedValue([
    { name: 'dir_size', description: 'Returns size of a directory', parameters: { type: 'object', properties: {}, required: [] }, body: 'def run(**kwargs):\n    return {}', source: 'size of a folder' },
  ]),
  createCustomTool: vi.fn().mockResolvedValue({ tool: { name: 'new_tool', description: 'd' } }),
  deleteCustomTool: vi.fn().mockResolvedValue({ success: true }),
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

  it('renders custom tool builder section', async () => {
    render(<SettingsPanel {...baseProps} />)
    expect(screen.getByText('CUSTOM TOOLS')).toBeTruthy()
    expect(await screen.findByText('dir_size')).toBeTruthy()
    expect(screen.getByText('Build tool')).toBeTruthy()
  })
})
