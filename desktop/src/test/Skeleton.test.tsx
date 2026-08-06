import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { Skeleton, SkeletonSection } from '../components/common/Skeleton'

describe('Skeleton', () => {
  it('should render with default props', () => {
    const { container } = render(<Skeleton />)
    const el = container.firstChild as HTMLElement
    expect(el).toBeInTheDocument()
    expect(el.style.width).toBe('100%')
    expect(el.style.height).toBe('12px')
  })

  it('should render with custom dimensions', () => {
    const { container } = render(<Skeleton width="200px" height="40px" rounded="xl" />)
    const el = container.firstChild as HTMLElement
    expect(el.style.width).toBe('200px')
    expect(el.style.height).toBe('40px')
    expect(el.style.borderRadius).toBe('16px')
  })

  it('should apply className', () => {
    const { container } = render(<Skeleton className="foo" />)
    const el = container.firstChild as HTMLElement
    expect(el.classList.contains('foo')).toBe(true)
  })
})

describe('SkeletonSection', () => {
  it('should render 3 skeleton items', () => {
    const { container } = render(<SkeletonSection />)
    const skeletons = container.querySelectorAll('[style*="animation: shimmer"]')
    // 1 header + 3 groups of (icon + 2 bars) = 1 + 3*3 = 10 skeletons
    expect(skeletons.length).toBe(10)
  })
})
