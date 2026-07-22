import { memo, useRef, useEffect, useMemo } from 'react'
import * as THREE from 'three'
import type { OrbState } from '../../types'
import {
  createCoreMaterial,
  createInnerCoreMaterial,
  createHoloMaterial,
  createRingMaterial,
  makeGlowTexture,
} from './shaders'

/* ─── Monochrome palette (orb only) ─── */
const C_DARK = '#2B2F36'
const C_MEDIUM = '#6E737C'
const C_LIGHT = '#BFC4CC'
const C_WHITE = '#FFFFFF'

const ACCENT = '#00a8ff'

/* ─── State configuration ─── */
interface StateConfig {
  pulseFreq: number
  glowIntensity: number
  ringSpeed: number
  coreSpeed: number
  particleActivity: number
  scanSpeed: number
  distortionStrength: number
  opacity: number
  holoOpacity: number
}

const STATE_CFG: Record<string, StateConfig> = {
  idle: {
    pulseFreq: 0.5,
    glowIntensity: 0.4,
    ringSpeed: 0.3,
    coreSpeed: 0.25,
    particleActivity: 0.3,
    scanSpeed: 1.5,
    distortionStrength: 0.03,
    opacity: 0.7,
    holoOpacity: 0.08,
  },
  listening: {
    pulseFreq: 0.9,
    glowIntensity: 0.55,
    ringSpeed: 0.5,
    coreSpeed: 0.35,
    particleActivity: 0.5,
    scanSpeed: 2.0,
    distortionStrength: 0.04,
    opacity: 0.75,
    holoOpacity: 0.12,
  },
  thinking: {
    pulseFreq: 1.4,
    glowIntensity: 0.7,
    ringSpeed: 0.7,
    coreSpeed: 0.5,
    particleActivity: 0.8,
    scanSpeed: 3.0,
    distortionStrength: 0.06,
    opacity: 0.8,
    holoOpacity: 0.18,
  },
  speaking: {
    pulseFreq: 1.8,
    glowIntensity: 0.8,
    ringSpeed: 0.6,
    coreSpeed: 0.4,
    particleActivity: 0.6,
    scanSpeed: 2.5,
    distortionStrength: 0.05,
    opacity: 0.85,
    holoOpacity: 0.15,
  },
  offline: {
    pulseFreq: 0.2,
    glowIntensity: 0.1,
    ringSpeed: 0.05,
    coreSpeed: 0.05,
    particleActivity: 0.05,
    scanSpeed: 0.3,
    distortionStrength: 0.01,
    opacity: 0.2,
    holoOpacity: 0.02,
  },
}

/* ─── Orbiting node paths ─── */
interface NodePath {
  radius: number
  inclination: number
  phase: number
  speed: number
}

function generateNodePaths(count: number): NodePath[] {
  const paths: NodePath[] = []
  for (let i = 0; i < count; i++) {
    paths.push({
      radius: 1.3 + Math.random() * 0.5,
      inclination: (Math.random() - 0.5) * Math.PI * 0.6,
      phase: Math.random() * Math.PI * 2,
      speed: 0.15 + Math.random() * 0.25,
    })
  }
  return paths
}

/* ─── JarvisOrb ─── */
function JarvisOrb({ orbState, handPosition, voiceActivity }: { orbState: OrbState; handPosition: { x: number; y: number } | null; voiceActivity?: boolean }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)
  const camRef = useRef<THREE.PerspectiveCamera | null>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const groupRef = useRef<THREE.Group | null>(null)
  const coreRef = useRef<THREE.Mesh | null>(null)
  const innerCoreRef = useRef<THREE.Mesh | null>(null)
  const holoShellRef = useRef<THREE.Mesh | null>(null)
  const wireframeRef = useRef<THREE.Mesh | null>(null)
  const dotsRef = useRef<THREE.Points | null>(null)
  const ringMeshesRef = useRef<{ mesh: THREE.Mesh; speed: number; axis: string }[]>([])
  const particlesRef = useRef<THREE.Points | null>(null)
  const nodesRef = useRef<THREE.Points | null>(null)
  const spriteRef = useRef<THREE.Sprite | null>(null)
  const animRef = useRef<number>(0)
  const followRef = useRef({ x: 0, y: 0 })
  const handPosRef = useRef(handPosition)
  handPosRef.current = handPosition
  const stateRef = useRef(orbState)
  stateRef.current = orbState
  const voiceRef = useRef(voiceActivity)
  voiceRef.current = voiceActivity

  const glowTex = useMemo(() => makeGlowTexture(), [])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const w = container.clientWidth
    const h = container.clientHeight

    /* ─── Scene ─── */
    const scene = new THREE.Scene()
    sceneRef.current = scene

    /* ─── Camera — slight offset for parallax ─── */
    const cam = new THREE.PerspectiveCamera(40, w / h, 0.1, 50)
    cam.position.set(0, 0.15, 4.8)
    cam.lookAt(0, 0, 0)
    camRef.current = cam

    /* ─── Renderer ─── */
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
    renderer.setSize(w, h)
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
    renderer.setClearColor(0x000000, 0)
    container.appendChild(renderer.domElement)
    rendererRef.current = renderer

    /* ─── Main group ─── */
    const group = new THREE.Group()
    scene.add(group)
    groupRef.current = group

    /* ================================================================
       1. Core Energy Sphere — ShaderMaterial with noise + Fresnel
       ================================================================ */
    const coreMat = createCoreMaterial()
    const coreGeo = new THREE.IcosahedronGeometry(0.65, 3)
    const core = new THREE.Mesh(coreGeo, coreMat)
    group.add(core)
    coreRef.current = core

    /* ================================================================
       2. Internal Core — smaller, opposite rotation, brighter
       ================================================================ */
    const innerMat = createInnerCoreMaterial()
    const innerGeo = new THREE.IcosahedronGeometry(0.3, 2)
    const innerCore = new THREE.Mesh(innerGeo, innerMat)
    group.add(innerCore)
    innerCoreRef.current = innerCore

    /* ================================================================
       3. Wireframe Shell — icosahedron edges
       ================================================================ */
    const shellGeo = new THREE.IcosahedronGeometry(0.85, 1)
    const shellMat = new THREE.MeshBasicMaterial({
      color: C_DARK,
      wireframe: true,
      transparent: true,
      opacity: 0.2,
    })
    const shell = new THREE.Mesh(shellGeo, shellMat)
    group.add(shell)
    wireframeRef.current = shell

    /* Vertex dots on wireframe */
    const shellPos = shellGeo.attributes.position
    const dotGeo = new THREE.BufferGeometry()
    dotGeo.setAttribute('position', shellPos.clone())
    const dotMat = new THREE.PointsMaterial({
      color: C_LIGHT,
      size: 0.025,
      transparent: true,
      opacity: 0.5,
      sizeAttenuation: true,
    })
    const dots = new THREE.Points(dotGeo, dotMat)
    group.add(dots)
    dotsRef.current = dots

    /* ================================================================
       4. Holographic Outer Shell — hex grid + scanlines shader
       ================================================================ */
    const holoMat = createHoloMaterial()
    const holoGeo = new THREE.SphereGeometry(1.1, 48, 32)
    const holoMesh = new THREE.Mesh(holoGeo, holoMat)
    group.add(holoMesh)
    holoShellRef.current = holoMesh

    /* ================================================================
       5. Orbital Rings — 4 rings with gradient shader
       ================================================================ */
    const ringDefs = [
      { r: 1.0, t: 0.01, c: C_LIGHT, o: 0.25, rx: Math.PI / 3, rz: 0, sp: 0.3, ax: 'z' },
      { r: 1.15, t: 0.007, c: C_MEDIUM, o: 0.15, rx: -Math.PI / 4, rz: Math.PI / 7, sp: 0.2, ax: 'y' },
      { r: 1.3, t: 0.005, c: C_WHITE, o: 0.1, rx: Math.PI / 5, rz: -Math.PI / 5, sp: 0.15, ax: 'x' },
      { r: 1.45, t: 0.004, c: C_LIGHT, o: 0.07, rx: Math.PI / 6, rz: Math.PI / 3, sp: 0.1, ax: 'z' },
    ]
    const ringEntries: { mesh: THREE.Mesh; speed: number; axis: string }[] = []
    for (const d of ringDefs) {
      const mat = createRingMaterial(d.c, d.o)
      const geo = new THREE.TorusGeometry(d.r, d.t, 16, 96)
      const mesh = new THREE.Mesh(geo, mat)
      mesh.rotation.x = d.rx
      mesh.rotation.z = d.rz
      scene.add(mesh)
      ringEntries.push({ mesh, speed: d.sp, axis: d.ax })
    }
    ringMeshesRef.current = ringEntries

    /* ================================================================
       6. Floating Particles — 120 particles, orbital magnetic drift
       ================================================================ */
    const particleCount = 120
    const pPositions = new Float32Array(particleCount * 3)
    const pSizes = new Float32Array(particleCount)
    const pSpeeds = new Float32Array(particleCount)
    const pRadii = new Float32Array(particleCount)
    const pAngles = new Float32Array(particleCount)
    const pOffsets = new Float32Array(particleCount)
    const pYOffsets = new Float32Array(particleCount)
    const pDrift = new Float32Array(particleCount)
    for (let i = 0; i < particleCount; i++) {
      pRadii[i] = 0.6 + Math.random() * 1.2
      pAngles[i] = Math.random() * Math.PI * 2
      pOffsets[i] = (Math.random() - 0.5) * 1.0
      pYOffsets[i] = (Math.random() - 0.5) * 0.8
      pSpeeds[i] = 0.1 + Math.random() * 0.3
      pDrift[i] = (Math.random() - 0.5) * 0.02
      pSizes[i] = 0.004 + Math.random() * 0.016
      pPositions[i * 3] = 0
      pPositions[i * 3 + 1] = 0
      pPositions[i * 3 + 2] = 0
    }
    const pGeo = new THREE.BufferGeometry()
    pGeo.setAttribute('position', new THREE.BufferAttribute(pPositions, 3))
    pGeo.setAttribute('size', new THREE.BufferAttribute(pSizes, 1))
    const pMat = new THREE.PointsMaterial({
      color: C_WHITE,
      size: 0.012,
      transparent: true,
      opacity: 0.35,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    })
    const particleSystem = new THREE.Points(pGeo, pMat)
    scene.add(particleSystem)
    particlesRef.current = particleSystem

    /* ================================================================
       7. Orbiting Nodes — 8 glowing points on inclined paths
       ================================================================ */
    const nodeCount = 8
    const nodePaths = generateNodePaths(nodeCount)
    const nPositions = new Float32Array(nodeCount * 3)
    const nSizes = new Float32Array(nodeCount)
    for (let i = 0; i < nodeCount; i++) {
      nSizes[i] = 0.035 + Math.random() * 0.025
    }
    const nGeo = new THREE.BufferGeometry()
    nGeo.setAttribute('position', new THREE.BufferAttribute(nPositions, 3))
    nGeo.setAttribute('size', new THREE.BufferAttribute(nSizes, 1))
    const nMat = new THREE.PointsMaterial({
      color: C_WHITE,
      size: 0.04,
      transparent: true,
      opacity: 0.7,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    })
    const nodeSystem = new THREE.Points(nGeo, nMat)
    scene.add(nodeSystem)
    nodesRef.current = nodeSystem

    /* ================================================================
       8. Glow Sprite
       ================================================================ */
    const spriteMat = new THREE.SpriteMaterial({
      map: glowTex,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
    const sprite = new THREE.Sprite(spriteMat)
    sprite.scale.set(3.5, 3.5, 1)
    scene.add(sprite)
    spriteRef.current = sprite

    /* ─── Geometry cleanup list ─── */
    const disposables: THREE.BufferGeometry[] = [coreGeo, innerGeo, shellGeo, dotGeo, holoGeo, pGeo, nGeo]

    /* ─── Visibilty / pause handling ─── */
    let paused = false
    const onVisibility = () => {
      if (document.hidden) {
        paused = true
        cancelAnimationFrame(animRef.current)
      } else {
        paused = false
        animate()
      }
    }
    document.addEventListener('visibilitychange', onVisibility)

    /* ─── Animation ─── */
    let time = 0
    let camAngle = 0

    const animate = () => {
      if (paused) return
      if (container.clientWidth === 0 || container.clientHeight === 0) {
        animRef.current = requestAnimationFrame(animate)
        return
      }
      time += 0.016
      const stateName = stateRef.current === 'error' ? 'thinking' : stateRef.current === 'offline' ? 'offline' : voiceRef.current ? 'speaking' : stateRef.current
      const cfg = STATE_CFG[stateName] || STATE_CFG.idle
      const rot = time * cfg.coreSpeed

      /* Group rotation */
      group.rotation.x = rot * 0.7
      group.rotation.y = rot

      /* Core sphere shader uniforms */
      coreMat.uniforms.uTime.value = time
      coreMat.uniforms.uNoiseStrength.value = cfg.distortionStrength
      coreMat.uniforms.uGlowIntensity.value = cfg.glowIntensity
      coreMat.uniforms.uOpacity.value = cfg.opacity

      /* Inner core — opposite rotation */
      innerMat.uniforms.uTime.value = time
      innerMat.uniforms.uGlowIntensity.value = cfg.glowIntensity * 1.2
      innerCore.rotation.x = -rot * 0.6
      innerCore.rotation.y = rot * 0.9

      /* Wireframe shell — slow independent rotation */
      shell.rotation.x = rot * 0.3 + time * 0.05
      shell.rotation.z = time * 0.03
      shellMat.opacity = cfg.opacity * 0.25
      dots.rotation.x = shell.rotation.x
      dots.rotation.y = shell.rotation.y
      dotMat.opacity = cfg.opacity * 0.6

      /* Holographic shell */
      holoMat.uniforms.uTime.value = time
      holoMat.uniforms.uOpacity.value = cfg.holoOpacity
      holoMat.uniforms.uScanSpeed.value = cfg.scanSpeed

      /* Smooth hand follow */
      const hp = handPosRef.current
      if (hp) {
        followRef.current.x += (hp.x * 0.4 - followRef.current.x) * 0.06
        followRef.current.y += (hp.y * 0.3 - followRef.current.y) * 0.06
      } else {
        followRef.current.x += (0 - followRef.current.x) * 0.03
        followRef.current.y += (0 - followRef.current.y) * 0.03
      }
      group.position.x = followRef.current.x * 0.3
      group.position.y = followRef.current.y * 0.3

      /* Pulse glow sprite */
      const pulse = 0.5 + 0.5 * Math.sin(time * cfg.pulseFreq + Math.sin(time * 0.5) * 0.3)
      spriteMat.opacity = Math.min(pulse * cfg.glowIntensity * 0.8, 0.6)

      /* Rotate rings at individual speeds */
      for (const entry of ringEntries) {
        const speed = entry.speed * cfg.ringSpeed * 0.01
        if (entry.axis === 'z') entry.mesh.rotation.z += speed
        else if (entry.axis === 'y') entry.mesh.rotation.y += speed
        else entry.mesh.rotation.x += speed
        const ringMat = entry.mesh.material as THREE.ShaderMaterial
        ringMat.uniforms.uTime.value = time
        ringMat.uniforms.uOpacity.value = entry.speed * 0.5 * (0.5 + pulse * 0.5) * cfg.ringSpeed
      }

      /* Animate particles — magnetic orbital drift */
      if (particlesRef.current) {
        const pPos = particlesRef.current.geometry.attributes.position.array as Float32Array
        for (let i = 0; i < particleCount; i++) {
          pAngles[i] += pSpeeds[i] * 0.006 * cfg.particleActivity
          const r = pRadii[i]
          const x = Math.cos(pAngles[i]) * r
          const z = Math.sin(pAngles[i]) * r
          const y = Math.sin(pAngles[i] * 1.5 + pOffsets[i]) * 0.4 + pYOffsets[i] * 0.3
          pPos[i * 3] = x + Math.sin(time * pDrift[i] + pOffsets[i]) * 0.08
          pPos[i * 3 + 1] = y + Math.cos(time * pDrift[i] * 0.7 + pOffsets[i]) * 0.08
          pPos[i * 3 + 2] = z
        }
        particlesRef.current.geometry.attributes.position.needsUpdate = true
        pMat.opacity = 0.15 + cfg.particleActivity * 0.4
      }

      /* Animate orbiting nodes */
      if (nodesRef.current) {
        const nPos = nodesRef.current.geometry.attributes.position.array as Float32Array
        for (let i = 0; i < nodeCount; i++) {
          const path = nodePaths[i]
          const theta = time * path.speed * cfg.ringSpeed + path.phase
          const x = Math.cos(theta) * path.radius
          const z = Math.sin(theta) * path.radius
          const y = Math.sin(theta * 0.5) * path.radius * Math.sin(path.inclination)
          nPos[i * 3] = x
          nPos[i * 3 + 1] = y
          nPos[i * 3 + 2] = z
        }
        nodesRef.current.geometry.attributes.position.needsUpdate = true
        nMat.opacity = cfg.opacity * 0.7
      }

      /* Subtle camera motion */
      camAngle += 0.002
      const cx = Math.sin(camAngle * 0.3) * 0.08
      const cy = Math.sin(camAngle * 0.2) * 0.04 + 0.15
      cam.position.x = cx
      cam.position.y = cy
      cam.lookAt(followRef.current.x * 0.1, followRef.current.y * 0.1, 0)

      renderer.render(scene, cam)
      animRef.current = requestAnimationFrame(animate)
    }
    animate()

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
      document.removeEventListener('visibilitychange', onVisibility)
      ro.disconnect()
      container.removeChild(renderer.domElement)
      renderer.dispose()
      disposables.forEach(d => d.dispose())
      coreMat.dispose()
      innerMat.dispose()
      shellMat.dispose()
      dotMat.dispose()
      holoMat.dispose()
      ringEntries.forEach(e => { e.mesh.geometry.dispose(); (e.mesh.material as THREE.ShaderMaterial).dispose() })
      pMat.dispose()
      nMat.dispose()
      spriteMat.dispose()
    }
  }, [glowTex])

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
      className="px-4 py-2.5 rounded-lg text-sm transition-all duration-200 active:scale-95 text-left glass glass-hover"
      style={{
        color: '#a0a0a8',
        fontWeight: 400,
        letterSpacing: '0.01em',
      }}
    >
      {label}
    </button>
  )
})

/* ─── AiCore ─── */
interface AiCoreProps {
  orbState: OrbState
  metrics: { latency: number; model: string; provider: string; memory: number; tokenUsage: number }
  onCommand: (prompt: string) => void
  hasMessages: boolean
  handPosition?: { x: number; y: number } | null
  voiceActivity?: boolean
}

export const AiCore = memo(function AiCore({ orbState, metrics, onCommand, hasMessages, handPosition = null, voiceActivity = false }: AiCoreProps) {
  const isOnline = orbState !== 'offline'

  if (hasMessages) {
    return (
      <div className="flex items-center gap-4 mb-6 px-8 pt-6 animate-fade-slide-in">
        <div className="w-12 h-12 shrink-0">
          <JarvisOrb orbState={orbState} handPosition={handPosition} voiceActivity={voiceActivity} />
        </div>
        <div>
          <div className="text-lg font-light tracking-wider blue-text" style={{ fontWeight: 200 }}>
            FRIDAY
          </div>
          <div className="flex items-center gap-2 text-[11px] mt-0.5" style={{ color: '#606068' }}>
            <span className={`inline-block w-1.5 h-1.5 rounded-full ${isOnline ? 'animate-pulse-glow' : ''}`}
              style={{ background: isOnline ? ACCENT : '#606068', boxShadow: isOnline ? `0 0 8px ${ACCENT}` : 'none' }}
            />
            <span style={{ color: isOnline ? ACCENT : '#606068' }}>{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
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
        <JarvisOrb orbState={orbState} handPosition={handPosition} voiceActivity={voiceActivity} />
      </div>
      <div className="text-[56px] font-thin tracking-[0.15em] blue-text animate-fade-slide-up" style={{ fontWeight: 100 }}>
        FRIDAY
      </div>

      <div className="flex items-center gap-3 mt-3 text-xs animate-fade-in" style={{ color: '#606068' }}>
        <div className="flex items-center gap-1.5">
          <span className={`inline-block w-1.5 h-1.5 rounded-full ${isOnline ? 'animate-pulse-glow' : ''}`}
            style={{ background: isOnline ? ACCENT : '#606068', boxShadow: isOnline ? `0 0 8px ${ACCENT}` : 'none' }}
          />
          <span style={{ color: isOnline ? ACCENT : '#606068' }}>{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
        <span className="w-px h-3 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }} />
        <span>{metrics.model}</span>
        <span className="w-px h-3 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }} />
        <span>{metrics.latency}ms latency</span>
        <span className="w-px h-3 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }} />
        <span>{metrics.memory}% RAM</span>
      </div>

      <div className="flex items-center gap-2 mt-8 animate-fade-slide-up" style={{ animationDelay: '0.15s' }}>
        {COMMANDS.map(c => (
          <CommandCard key={c.id} label={c.label} prompt={c.prompt} onClick={onCommand} />
        ))}
      </div>
    </div>
  )
})
