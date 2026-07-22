import { memo, useState } from 'react'
import type { MemoryData } from '../../types'
import { Skeleton } from '../common/Skeleton'

interface MemoryPanelProps {
  data: MemoryData | null
}

export const MemoryPanel = memo(function MemoryPanel({ data }: MemoryPanelProps) {
  const [search, setSearch] = useState('')
  const [tab, setTab] = useState<'semantic' | 'embedding'>('embedding')

  const memories = tab === 'embedding'
    ? (data?.embedding_memories || data?.vector_memories || [])
    : (data?.vector_memories || [])
  const count = tab === 'embedding'
    ? (data?.embedding_count ?? data?.vector_count ?? 0)
    : (data?.vector_count ?? 0)

  const filtered = search
    ? memories.filter(m => m.text.toLowerCase().includes(search.toLowerCase()))
    : memories

  return (
    <div className="rounded-xl overflow-hidden" style={{ background: '#0D0D0D', border: '1px solid rgba(255,255,255,0.06)' }}>
      <div className="px-3 py-2.5 text-xs font-medium tracking-wider flex items-center justify-between" style={{ color: '#888', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
        <span>MEMORY {data ? `(${count})` : ''}</span>
        {data && (
          <div className="flex gap-1 text-[10px]">
            <button
              onClick={() => setTab('embedding')}
              className="px-1.5 py-0.5 rounded transition-all"
              style={{ color: tab === 'embedding' ? '#f59e0b' : '#555', background: tab === 'embedding' ? 'rgba(245,158,11,0.1)' : 'transparent' }}
            >
              TF-IDF
            </button>
            <button
              onClick={() => setTab('semantic')}
              className="px-1.5 py-0.5 rounded transition-all"
              style={{ color: tab === 'semantic' ? '#f59e0b' : '#555', background: tab === 'semantic' ? 'rgba(245,158,11,0.1)' : 'transparent' }}
            >
              jaccard
            </button>
          </div>
        )}
      </div>

      {data === null ? (
        <div className="space-y-2 p-3">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="flex items-center gap-2">
              <Skeleton width="28px" height="28px" rounded="md" />
              <div className="flex-1 space-y-1">
                <Skeleton width="80%" height="10px" />
                <Skeleton width="40%" height="8px" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          <div className="px-3 py-2">
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search memories..."
              className="w-full rounded-lg px-2.5 py-1.5 text-xs outline-none transition-all"
              style={{
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.06)',
                color: '#999',
              }}
            />
          </div>

          <div className="max-h-[240px] overflow-y-auto px-1 pb-2">
            {filtered.length === 0 && (
              <div className="text-center py-6 text-xs" style={{ color: '#555' }}>
                {search ? `No memories match "${search}"` : 'No memories yet'}
              </div>
            )}
            {filtered.slice(0, 20).map((mem, i) => (
              <div
                key={mem.id || i}
                className="px-2.5 py-2 mx-1 rounded-lg text-xs leading-relaxed transition-colors hover:bg-[rgba(255,255,255,0.03)]"
                style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}
              >
                <div className="line-clamp-2" style={{ color: '#bbb' }}>{mem.text}</div>
                <div className="mt-1 flex items-center gap-2 text-[10px]" style={{ color: '#555' }}>
                  {mem.score != null && <span>score: {mem.score.toFixed(3)}</span>}
                  <span>{new Date(mem.created_at * 1000).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
})
