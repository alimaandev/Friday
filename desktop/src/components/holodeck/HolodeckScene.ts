/**
 * HolodeckScene — manages a THREE.js 3D data visualization scene.
 * Renders metrics as animated bars + ambient particles + orbital rings.
 */
import * as THREE from 'three'

export interface HolodeckMetrics {
  latency: number
  memory: number
  tokenUsage: number
  cpu?: number
}

const BAR_CONFIGS = [
  { label: 'CPU', color: '#00a8ff', getValue: (m: HolodeckMetrics) => (m.cpu ?? 50) / 100 },
  { label: 'RAM', color: '#7c3aed', getValue: (m: HolodeckMetrics) => m.memory / 100 },
  { label: 'LAT', color: '#d4a040', getValue: (m: HolodeckMetrics) => Math.min(m.latency / 500, 1) },
  { label: 'TOK', color: '#22c55e', getValue: (m: HolodeckMetrics) => Math.min(m.tokenUsage / 4000, 1) },
]

export class HolodeckScene {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private animId: number = 0
  private bars: THREE.Mesh[] = []
  private barTargets: number[] = []
  private particles: THREE.Points
  private rings: THREE.Line[] = []
  private clock = new THREE.Clock()
  private disposeFn: (() => void)[] = []

  constructor(canvas: HTMLCanvasElement) {
    const w = canvas.clientWidth || 600
    const h = canvas.clientHeight || 300

    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(0x0a0a0f)

    this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
    this.camera.position.set(5, 3, 6)
    this.camera.lookAt(0, 0, 0)

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false })
    this.renderer.setSize(w, h)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

    // Lights
    const ambient = new THREE.AmbientLight(0x333344, 0.6)
    this.scene.add(ambient)
    const dir = new THREE.DirectionalLight(0xffffff, 1.2)
    dir.position.set(5, 10, 7)
    this.scene.add(dir)
    const back = new THREE.DirectionalLight(0x4488ff, 0.3)
    back.position.set(-5, 0, -5)
    this.scene.add(back)

    // Ground grid
    const grid = new THREE.GridHelper(8, 16, 0x00a8ff, 0x222244)
    grid.position.y = -0.5
    this.scene.add(grid)
    this.disposeFn.push(() => this.scene.remove(grid))

    // Bars
    BAR_CONFIGS.forEach((cfg, i) => {
      const geo = new THREE.BoxGeometry(0.6, 0.01, 0.6)
      const mat = new THREE.MeshPhysicalMaterial({
        color: cfg.color,
        metalness: 0.1,
        roughness: 0.4,
        emissive: cfg.color,
        emissiveIntensity: 0.15,
      })
      const mesh = new THREE.Mesh(geo, mat)
      const xPos = (i - (BAR_CONFIGS.length - 1) / 2) * 1.4
      mesh.position.set(xPos, -0.5, 0)
      this.scene.add(mesh)
      this.bars.push(mesh)
      this.barTargets.push(0.1)
      this.disposeFn.push(() => this.scene.remove(mesh))
    })

    // Particles
    const particleCount = 400
    const positions = new Float32Array(particleCount * 3)
    for (let i = 0; i < particleCount * 3; i++) {
      positions[i] = (Math.random() - 0.5) * 20
    }
    const pGeo = new THREE.BufferGeometry()
    pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    const pMat = new THREE.PointsMaterial({
      color: 0x4488ff,
      size: 0.04,
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
    })
    this.particles = new THREE.Points(pGeo, pMat)
    this.particles.position.y = 1
    this.scene.add(this.particles)
    this.disposeFn.push(() => this.scene.remove(this.particles))

    // Orbital rings
    for (let i = 0; i < 2; i++) {
      const r = 2.5 + i * 0.8
      const curve = new THREE.EllipseCurve(0, 0, r, r, 0, 2 * Math.PI, false, 0)
      const pts = curve.getPoints(60)
      const g = new THREE.BufferGeometry().setFromPoints(
        pts.map(p => new THREE.Vector3(p.x, 0, p.y))
      )
      const l = new THREE.Line(
        g,
        new THREE.LineBasicMaterial({
          color: i === 0 ? 0x00a8ff : 0x7c3aed,
          transparent: true,
          opacity: 0.2,
        })
      )
      l.position.y = -0.3
      this.scene.add(l)
      this.rings.push(l)
      this.disposeFn.push(() => this.scene.remove(l))
    }

    this.animate()
  }

  private animate = () => {
    this.animId = requestAnimationFrame(this.animate)
    const dt = this.clock.getDelta()
    const t = this.clock.getElapsedTime()

    // Smooth bars
    this.bars.forEach((bar, i) => {
      const target = this.barTargets[i]
      const cur = bar.scale.y
      const next = cur + (target - cur) * 3 * dt
      bar.scale.y = next
      bar.position.y = -0.5 + next / 2
    })

    // Rotate particles
    this.particles.rotation.y += dt * 0.05

    // Pulse rings
    this.rings.forEach((ring, i) => {
      ring.rotation.y += dt * (0.1 + i * 0.05)
      const pulse = 0.15 + 0.1 * Math.sin(t * 0.5 + i)
      const mat = ring.material
      if (!Array.isArray(mat)) mat.opacity = pulse
    })

    // Subtle camera bob
    this.camera.position.x = 5 * Math.sin(t * 0.03)
    this.camera.position.z = 6 * Math.cos(t * 0.03)
    this.camera.lookAt(0, 0, 0)

    this.renderer.render(this.scene, this.camera)
  }

  updateMetrics(metrics: HolodeckMetrics) {
    BAR_CONFIGS.forEach((cfg, i) => {
      this.barTargets[i] = Math.max(cfg.getValue(metrics), 0.05)
    })
  }

  updateGesture(x: number, openness: number) {
    // x: -1..1 → rotate left-right
    // openness: 0..1 → zoom
    this.camera.position.x = 5 * Math.sin(x * 0.5)
    this.camera.position.z = 6 * Math.cos(x * 0.5)
    this.camera.position.y = 3 + (1 - openness) * 2
    this.camera.lookAt(0, 0, 0)
  }

  resize(w: number, h: number) {
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(w, h)
  }

  dispose() {
    cancelAnimationFrame(this.animId)
    this.disposeFn.forEach(fn => fn())
    this.renderer.dispose()
  }
}