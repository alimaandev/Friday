import { memo, useCallback, useEffect, useState } from 'react'
import type { DiaryDay } from '../../types'
import { getDiaryPage, getDiaryRecent, writeNightlyDigest } from '../../core/api'
import { MarkdownBlock } from '../chat/MarkdownBlock'

interface DiaryPanelProps {
  refreshToken?: number
}

const fmtDay = (iso: string) => {
  const [y, m, d] = iso.split('-')
  return `${y}-${m}-${d}`
}

export const DiaryPanel = memo(function DiaryPanel({ refreshToken = 0 }: DiaryPanelProps) {
  const [days, setDays] = useState<DiaryDay[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [writing, setWriting] = useState(false)
  const [error, setError] = useState('')

  const loadDays = useCallback(() => {
    getDiaryRecent()
      .then(d => {
        setDays(d.days || [])
        if (d.days?.length > 0) {
          setSelected(prev => prev ?? d.days[d.days.length - 1].date)
        }
        setError('')
      })
      .catch(() => setError('Diary unavailable'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(loadDays, [loadDays, refreshToken])

  useEffect(() => {
    if (!selected) return
    getDiaryPage(selected)
      .then(p => setContent(p.content || ''))
      .catch(() => setContent(''))
  }, [selected])

  const handleWriteNightly = useCallback(() => {
    setWriting(true)
    writeNightlyDigest()
      .then(() => {
        const today = new Date().toISOString().slice(0, 10)
        setSelected(today)
        loadDays()
      })
      .catch(() => setError('Could not write entry'))
      .finally(() => setWriting(false))
  }, [loadDays])

  const hasEntry = content.length > 0

  return (
    <div className="rounded-xl overflow-hidden" style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}>
      <div className="px-3 py-2.5 text-xs font-medium tracking-wider flex items-center justify-between" style={{ color: '#888', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
        <span>📖 DIARY {days.length > 0 ? `(${days.length})` : ''}</span>
        <button
          onClick={handleWriteNightly}
          disabled={writing}
          className="px-2 py-0.5 rounded text-[10px] transition-all hover:bg-[rgba(212,160,64,0.15)] disabled:opacity-50"
          style={{ color: '#D4A040', border: '1px solid rgba(212,160,64,0.25)' }}
          title="Write tonight's closing entry"
        >
          {writing ? 'Writing…' : '✦ Tonight'}
        </button>
      </div>

      {loading ? (
        <div className="p-3 space-y-2">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-9 rounded-lg animate-pulse" style={{ background: 'rgba(255,255,255,0.03)' }} />
          ))}
        </div>
      ) : error && days.length === 0 ? (
        <div className="text-center py-6 text-xs" style={{ color: '#555' }}>{error}</div>
      ) : days.length === 0 ? (
        <div className="text-center py-6 text-xs px-3" style={{ color: '#555' }}>
          No diary pages yet — Friday writes here after conversations and each night.
        </div>
      ) : (
        <div className="flex gap-2 p-2">
          <div className="flex-1 max-h-[220px] overflow-y-auto space-y-1 pr-1" style={{ scrollbarWidth: 'thin' }}>
            {days.map(d => (
              <button
                key={d.date}
                onClick={() => setSelected(d.date)}
                className="w-full text-left px-2.5 py-1.5 rounded-lg transition-all"
                style={{
                  background: selected === d.date ? 'rgba(245,158,11,0.08)' : 'rgba(255,255,255,0.02)',
                  border: selected === d.date ? '1px solid rgba(245,158,11,0.25)' : '1px solid transparent',
                }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono" style={{ color: selected === d.date ? '#f59e0b' : '#aaa' }}>
                    {fmtDay(d.date)}
                  </span>
                  {d.date === new Date().toISOString().slice(0, 10) && (
                    <span className="text-[9px]" style={{ color: '#f59e0b' }}>today</span>
                  )}
                </div>
                {d.excerpt && (
                  <div className="text-[10px] mt-0.5 truncate" style={{ color: '#666' }}>{d.excerpt}</div>
                )}
              </button>
            ))}
          </div>
          <div className="flex-[2] min-w-0 max-h-[220px] overflow-y-auto pr-1 intel-scroll" style={{ scrollbarWidth: 'thin' }}>
            {selected && (
              hasEntry ? (
                <MarkdownBlock content={content} />
              ) : (
                <div className="text-xs italic py-6 text-center" style={{ color: '#555' }}>
                  No entries for {fmtDay(selected)}
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  )
})