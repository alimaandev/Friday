import { memo, useRef, useEffect, useMemo } from 'react'
import * as THREE from 'three'
import type { OrbState } from '../../types'

/* ─── Three.js gold orb ─── */

const GOLD = { primary: '#D4A040', secondary: '#B8860B', accent: '#FFD700', glow: '#FFF8DC' }

function makeGlowTexture() {
  const c = document.createElement('canvas')
  c.width = 128; c.height = 128
  const ctx = c.getContext('2d')!
  const grad = ctx.createRadialGradient(64, 64, 0, 64, 64, 64)
  grad.addColorStop(0, 'rgba(255,215,0,0.7)')
  grad.addColorStop(0.3, 'rgba(212,160,64,0.3)')
  grad.addColorStop(0.6, 'rgba(184,134,11,0.1)')
  grad.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, 128, 128)
  return new THREE.CanvasTexture(c)
}

function GoldOrb({ orbState, handPosition }: { orbState: OrbState; handPosition: { x: number; y: number } | null }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)
  const camRef = useRef<THREE.PerspectiveCamera | null>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const cageRef = useRef<THREE.Mesh | null>(null)
  const innerRef = useRef<THREE.Mesh | null>(null)
  const glowRef = useRef<THREE.Sprite | null>(null)
  const dotsRef = useRef<THREE.Points | null>(null)
  const groupRef = useRef<THREE.Group | null>(null)
  const animRef = useRef<number>(0)
  const followRef = useRef({ x: 0, y: 0 })
  const handPosRef = useRef(handPosition)
  handPosRef.current = handPosition

  const glowTex = useMemo(makeGlowTexture, [])

  const pulseSpeed = orbState === 'idle' ? 0.5 : orbState === 'error' ? 2 : 1.2

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const w = container.clientWidth
    const h = container.clientHeight

    const scene = new THREE.Scene()
    sceneRef.current = scene

    const cam = new THREE.PerspectiveCamera(45, w / h, 0.1, 50)
    cam.position.z = 5
    camRef.current = cam

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
    renderer.setSize(w, h)
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
    renderer.setClearColor(0x000000, 0)
    container.appendChild(renderer.domElement)
    rendererRef.current = renderer

    const group = new THREE.Group()
    scene.add(group)
    groupRef.current = group

    /* Outer wireframe cage */
    const geo = new THREE.IcosahedronGeometry(0.7, 1)
    const mat = new THREE.MeshBasicMaterial({
      color: GOLD.secondary,
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    })
    const cage = new THREE.Mesh(geo, mat)
    group.add(cage)
    cageRef.current = cage

    /* Inner solid sphere (glow core) */
    const innerGeo = new THREE.IcosahedronGeometry(0.35, 1)
    const innerMat = new THREE.MeshBasicMaterial({
      color: GOLD.primary,
      transparent: true,
      opacity: 0.15,
      wireframe: true,
    })
    const inner = new THREE.Mesh(innerGeo, innerMat)
    group.add(inner)
    innerRef.current = inner

    /* Vertex dots on outer cage */
    const pos = geo.attributes.position
    const dotGeo = new THREE.BufferGeometry()
    dotGeo.setAttribute('position', pos.clone())
    const dotMat = new THREE.PointsMaterial({
      color: GOLD.accent,
      size: 0.03,
      transparent: true,
      opacity: 0.8,
      sizeAttenuation: true,
    })
    const dots = new THREE.Points(dotGeo, dotMat)
    group.add(dots)
    dotsRef.current = dots

    /* Glow sprite — kept in scene so it stays centered and doesn't tilt */
    const spriteMat = new THREE.SpriteMaterial({
      map: glowTex,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
    const sprite = new THREE.Sprite(spriteMat)
    sprite.scale.set(2.5, 2.5, 1)
    scene.add(sprite)
    glowRef.current = sprite

    /* Animation */
    let time = 0
    const animate = () => {
      time += 0.01
      const rot = time * 0.3

      /* Auto-rotate group, spin inner separately */
      group.rotation.x = rot * 0.7
      group.rotation.y = rot
      inner.rotation.x = -rot * 0.5
      inner.rotation.y = rot * 0.8
      dots.rotation.x = group.rotation.x
      dots.rotation.y = group.rotation.y

      /* Smooth hand follow — translate group in world space */
      const hp = handPosRef.current
      if (hp) {
        followRef.current.x += (hp.x * 0.4 - followRef.current.x) * 0.06
        followRef.current.y += (hp.y * 0.3 - followRef.current.y) * 0.06
      } else {
        followRef.current.x += (0 - followRef.current.x) * 0.03
        followRef.current.y += (0 - followRef.current.y) * 0.03
      }
      group.position.x = followRef.current.x
      group.position.y = followRef.current.y

      /* Pulse glow */
      const pulse = 0.6 + 0.4 * Math.sin(time * pulseSpeed)
      spriteMat.opacity = pulse

      renderer.render(scene, cam)
      animRef.current = requestAnimationFrame(animate)
    }
    animate()

    /* Resize */
    const resize = () => {
      const cw = container.clientWidth
      const ch = container.clientHeight
      cam.aspect = cw / ch
      cam.updateProjectionMatrix()
      renderer.setSize(cw, ch)
    }
    const ro = new ResizeObserver(resize)
    ro.observe(container)

    return () => {
      cancelAnimationFrame(animRef.current)
      ro.disconnect()
      container.removeChild(renderer.domElement)
      renderer.dispose()
      geo.dispose()
      mat.dispose()
      innerGeo.dispose()
      innerMat.dispose()
      dotGeo.dispose()
      dotMat.dispose()
      spriteMat.dispose()
    }
  }, [glowTex, pulseSpeed])

  return <div ref={containerRef} className="w-full h-full" />
}

/* ─── Command cards ─── */

const COMMANDS = [
  { id: 'code', label: 'Code', prompt: 'Write code to' },
  { id: 'research', label: 'Research', prompt: 'Research the topic' },
  { id: 'search', label: 'Search', prompt: 'Search the web for' },
  { id: 'analyze', label: 'Analyze', prompt: 'Analyze the following' },
  { id: 'execute', label: 'Execute', prompt: 'Execute a plan to' },
  { id: 'automate', label: 'Automate', prompt: 'Create an automated workflow to' },
]

const CommandCard = memo(function CommandCard({ label, prompt, onClick }: { label: string; prompt: string; onClick: (p: string) => void }) {
  return (
    <button
      onClick={() => onClick(prompt)}
      className="px-4 py-2.5 rounded-lg text-sm transition-all duration-200 active:scale-95 text-left"
      style={{
        background: '#0D0D0D',
        border: '1px solid rgba(255,255,255,0.06)',
        color: '#9E9E9E',
        fontFamily: 'Inter, sans-serif',
        fontWeight: 400,
        letterSpacing: '0.01em',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'rgba(212,160,64,0.3)';
        e.currentTarget.style.color = '#D4A040'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)';
        e.currentTarget.style.color = '#9E9E9E'
      }}
    >
      {label}
    </button>
  )
})

/* ─── AiCore component ─── */

interface AiCoreProps {
  orbState: OrbState
  metrics: { latency: number; model: string; provider: string; memory: number; tokenUsage: number }
  onCommand: (prompt: string) => void
  hasMessages: boolean
  handPosition?: { x: number; y: number } | null
}

export const AiCore = memo(function AiCore({ orbState, metrics, onCommand, hasMessages, handPosition = null }: AiCoreProps) {
  const isOnline = orbState !== 'offline'

  if (hasMessages) {
    /* Compact badge mode when conversation is active */
    return (
      <div className="flex items-center gap-4 mb-6 px-8 pt-6">
        <div className="w-12 h-12 shrink-0">
          <GoldOrb orbState={orbState} handPosition={handPosition} />
        </div>
        <div>
          <div className="text-lg font-light tracking-wider" style={{ color: '#D4A040', fontWeight: 200 }}>
            FRIDAY
          </div>
          <div className="flex items-center gap-2 text-[11px] mt-0.5" style={{ color: '#666' }}>
            <span className={`inline-block w-1.5 h-1.5 rounded-full ${isOnline ? 'animate-pulse-glow' : ''}`}
              style={{ background: isOnline ? '#D4A040' : '#666', boxShadow: isOnline ? '0 0 6px rgba(212,160,64,0.5)' : 'none' }}
            />
            <span style={{ color: isOnline ? '#D4A040' : '#666' }}>{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
            <span>{metrics.model}</span>
            <span>{metrics.latency}ms</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-8 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <GoldOrb orbState={orbState} handPosition={handPosition} />
      </div>
      <div className="text-[56px] font-thin tracking-[0.15em]" style={{ color: '#D4A040', fontWeight: 100, letterSpacing: '0.15em' }}>
        FRIDAY
      </div>

      <div className="flex items-center gap-3 mt-3 text-xs" style={{ color: '#666' }}>
        <div className="flex items-center gap-1.5">
          <span className={`inline-block w-1.5 h-1.5 rounded-full ${isOnline ? 'animate-pulse-glow' : ''}`}
            style={{ background: isOnline ? '#D4A040' : '#666', boxShadow: isOnline ? '0 0 6px rgba(212,160,64,0.5)' : 'none' }}
          />
          <span style={{ color: isOnline ? '#D4A040' : '#666' }}>{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
        <span className="w-px h-3 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }} />
        <span>{metrics.model}</span>
        <span className="w-px h-3 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }} />
        <span>{metrics.latency}ms latency</span>
        <span className="w-px h-3 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }} />
        <span>{metrics.memory}% RAM</span>
      </div>

      <div className="flex items-center gap-2 mt-8">
        {COMMANDS.map(c => (
          <CommandCard key={c.id} label={c.label} prompt={c.prompt} onClick={onCommand} />
        ))}
      </div>
    </div>
  )
})
