import { memo } from 'react'

interface SkeletonProps {
  width?: string
  height?: string
  rounded?: string
  className?: string
}

export const Skeleton = memo(function Skeleton({ width = '100%', height = '12px', rounded = 'md', className = '' }: SkeletonProps) {
  const radii: Record<string, string> = { sm: '4px', md: '8px', lg: '12px', xl: '16px', full: '9999px' }
  return (
    <div
      className={className}
      style={{
        width,
        height,
        borderRadius: radii[rounded] || '8px',
        background: 'linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0.03) 75%)',
        backgroundSize: '200% 100%',
        animation: 'shimmer 1.5s ease-in-out infinite',
      }}
    />
  )
})

export function SkeletonSection() {
  return (
    <div className="space-y-2 px-4">
      <Skeleton width="80px" height="10px" />
      <div className="space-y-2">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex items-center gap-2">
            <Skeleton width="28px" height="28px" rounded="md" />
            <div className="flex-1 space-y-1">
              <Skeleton width="80%" height="10px" />
              <Skeleton width="40%" height="8px" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
