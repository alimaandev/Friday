import * as THREE from 'three'

/* ─── 3D Noise (value noise) ─── */
const noiseGLSL = `
  float hash(vec3 p) {
    p = fract(p * 0.3183099 + 0.1);
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
  }

  float noise3D(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i + vec3(0,0,0));
    float b = hash(i + vec3(1,0,0));
    float c = hash(i + vec3(0,1,0));
    float d = hash(i + vec3(1,1,0));
    float e = hash(i + vec3(0,0,1));
    float ff = hash(i + vec3(1,0,1));
    float g = hash(i + vec3(0,1,1));
    float h = hash(i + vec3(1,1,1));
    float u1 = mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
    float u2 = mix(mix(e, ff, f.x), mix(g, h, f.x), f.y);
    return mix(u1, u2, f.z);
  }
`

/* ─── Core Energy Sphere shaders ─── */
export const coreVertexShader = `
  uniform float uTime;
  uniform float uNoiseScale;
  uniform float uNoiseStrength;
  uniform float uDistortionSpeed;

  varying float vFresnel;
  varying float vNoise;
  varying vec3 vNormal;
  varying vec3 vViewDir;

  ${noiseGLSL}

  void main() {
    vec3 pos = position;
    float n = noise3D(pos * uNoiseScale + uTime * uDistortionSpeed);
    pos += normal * n * uNoiseStrength;

    vec4 worldPos = modelMatrix * vec4(pos, 1.0);
    vec3 viewDir = normalize(cameraPosition - worldPos.xyz);
    vec3 worldNormal = normalize(mat3(modelMatrix) * normal);

    vFresnel = 1.0 - abs(dot(viewDir, worldNormal));
    vFresnel = pow(vFresnel, 2.5);
    vNoise = n;
    vNormal = worldNormal;
    vViewDir = viewDir;

    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`

export const coreFragmentShader = `
  uniform float uTime;
  uniform float uGlowIntensity;
  uniform float uOpacity;
  uniform vec3 uColorInner;
  uniform vec3 uColorOuter;
  uniform vec3 uEdgeColor;

  varying float vFresnel;
  varying float vNoise;
  varying vec3 vNormal;
  varying vec3 vViewDir;

  ${noiseGLSL}

  void main() {
    float noisePattern = vNoise * 0.5 + 0.5;
    float fresnelGlow = vFresnel * 0.9;

    float rim = 1.0 - abs(dot(vViewDir, vNormal));
    rim = pow(rim, 3.0);

    vec3 innerColor = uColorInner + vec3(0.05) * noisePattern;
    vec3 edgeColor = mix(uEdgeColor, vec3(1.0), fresnelGlow * 0.5);
    vec3 baseColor = mix(innerColor, uColorOuter, fresnelGlow * 0.6 + noisePattern * 0.1);

    vec3 glow = vec3(1.0) * fresnelGlow * uGlowIntensity * 0.6;
    vec3 rimGlow = vec3(1.0) * rim * 0.3 * uGlowIntensity;

    float energy = noise3D(vNormal * 2.0 + uTime * 0.15) * 0.5 + 0.5;
    vec3 energyFlow = vec3(1.0) * energy * 0.1 * uGlowIntensity;

    vec3 finalColor = baseColor + glow + rimGlow + energyFlow;
    float alpha = uOpacity + fresnelGlow * 0.3 + rim * 0.2;

    gl_FragColor = vec4(finalColor, alpha);
  }
`

/* ─── Internal Core shaders ─── */
export const innerCoreVertexShader = `
  uniform float uTime;
  uniform float uNoiseScale;
  uniform float uNoiseStrength;

  varying float vFresnel;
  varying float vNoise;

  ${noiseGLSL}

  void main() {
    vec3 pos = position;
    float n = noise3D(pos * uNoiseScale + uTime * 0.08);
    pos += normal * n * uNoiseStrength;

    vec4 worldPos = modelMatrix * vec4(pos, 1.0);
    vec3 viewDir = normalize(cameraPosition - worldPos.xyz);
    vec3 worldNormal = normalize(mat3(modelMatrix) * normal);

    vFresnel = 1.0 - abs(dot(viewDir, worldNormal));
    vFresnel = pow(vFresnel, 2.0);
    vNoise = n;

    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`

export const innerCoreFragmentShader = `
  uniform float uTime;
  uniform float uGlowIntensity;
  uniform vec3 uColor;

  varying float vFresnel;
  varying float vNoise;

  void main() {
    float pattern = vNoise * 0.5 + 0.5;
    vec3 base = uColor + vec3(0.1) * pattern;
    vec3 glow = vec3(1.0) * vFresnel * uGlowIntensity * 0.8;
    float pulse = 0.85 + 0.15 * sin(uTime * 1.5 + pattern * 6.28);

    vec3 finalColor = (base + glow) * pulse;
    float alpha = 0.7 + vFresnel * 0.3;

    gl_FragColor = vec4(finalColor, alpha);
  }
`

/* ─── Holographic Shell shaders ─── */
export const holoVertexShader = `
  varying vec2 vUv;
  varying vec3 vPosition;
  varying vec3 vNormal;

  void main() {
    vUv = uv;
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vPosition = worldPos.xyz;
    vNormal = normalize(mat3(modelMatrix) * normal);
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`

export const holoFragmentShader = `
  uniform float uTime;
  uniform float uOpacity;
  uniform float uScanSpeed;
  uniform float uGridScale;
  uniform vec3 uLineColor;
  uniform vec3 uBgColor;

  varying vec2 vUv;
  varying vec3 vPosition;
  varying vec3 vNormal;

  void main() {
    vec2 uv = vUv * uGridScale;

    // Hexagonal grid pattern
    vec2 hexCoord = uv;
    vec2 hexOffset = vec2(0.5, 0.577);
    vec2 hexIndex = floor((hexCoord + hexOffset) / (hexOffset * 2.0));
    vec2 localPos = hexCoord - hexIndex * hexOffset * 2.0;
    float distToEdge = 1.0 - abs(localPos.x / hexOffset.x) + (1.0 - abs(localPos.y / hexOffset.y));
    distToEdge = clamp(distToEdge, 0.0, 1.0);

    // Grid lines
    float gridX = abs(fract(uv.x * 0.5) - 0.5) * 2.0;
    float gridY = abs(fract(uv.y * 0.5) - 0.5) * 2.0;
    float gridLine = 1.0 - smoothstep(0.0, 0.03, min(gridX, gridY));
    float hexLine = 1.0 - smoothstep(0.85, 0.95, distToEdge);

    float linePattern = max(gridLine, hexLine * 0.5);

    // Scanlines
    float scan = sin(vPosition.y * 40.0 + uTime * uScanSpeed) * 0.5 + 0.5;
    scan = smoothstep(0.3, 0.7, scan);

    // Vertical data stream
    float dataStream = fract(vPosition.y * 3.0 - uTime * 0.3);
    dataStream = 1.0 - smoothstep(0.0, 0.1, abs(dataStream - 0.5) * 2.0);

    vec3 color = uBgColor;
    color = mix(color, uLineColor, linePattern * 0.6);
    color = mix(color, uLineColor * 1.5, scan * 0.15);
    color += vec3(1.0) * dataStream * 0.05;

    float alpha = uOpacity * (linePattern * 0.5 + 0.2 + scan * 0.1);

    // Fresnel fade on edges
    vec3 viewDir = normalize(cameraPosition - vPosition);
    float fresnel = 1.0 - abs(dot(viewDir, normalize(vNormal)));
    alpha *= 0.3 + fresnel * 0.7;

    gl_FragColor = vec4(color, alpha);
  }
`

/* ─── Ring shaders ─── */
export const ringVertexShader = `
  varying vec2 vUv;
  varying vec3 vPosition;

  void main() {
    vUv = uv;
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vPosition = worldPos.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`

export const ringFragmentShader = `
  uniform float uTime;
  uniform float uOpacity;
  uniform vec3 uColor;

  varying vec2 vUv;

  void main() {
    // Gradient along ring circumference
    float gradient = sin(vUv.x * 6.28 * 2.0 + uTime * 0.5) * 0.5 + 0.5;
    float brightness = 0.6 + gradient * 0.4;

    vec3 color = uColor * brightness;
    float alpha = uOpacity * (0.5 + gradient * 0.5);

    gl_FragColor = vec4(color, alpha);
  }
`

/* ─── Utility: create ShaderMaterial for core sphere ─── */
export function createCoreMaterial(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    vertexShader: coreVertexShader,
    fragmentShader: coreFragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uNoiseScale: { value: 2.5 },
      uNoiseStrength: { value: 0.04 },
      uDistortionSpeed: { value: 0.1 },
      uGlowIntensity: { value: 0.6 },
      uOpacity: { value: 0.75 },
      uColorInner: { value: new THREE.Color('#2B2F36') },
      uColorOuter: { value: new THREE.Color('#6E737C') },
      uEdgeColor: { value: new THREE.Color('#BFC4CC') },
    },
    transparent: true,
    side: THREE.DoubleSide,
    blending: THREE.NormalBlending,
    depthWrite: false,
  })
}

/* ─── Utility: create ShaderMaterial for inner core ─── */
export function createInnerCoreMaterial(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    vertexShader: innerCoreVertexShader,
    fragmentShader: innerCoreFragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uNoiseScale: { value: 3.0 },
      uNoiseStrength: { value: 0.03 },
      uGlowIntensity: { value: 0.8 },
      uColor: { value: new THREE.Color('#BFC4CC') },
    },
    transparent: true,
    side: THREE.DoubleSide,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  })
}

/* ─── Utility: create ShaderMaterial for holographic shell ─── */
export function createHoloMaterial(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    vertexShader: holoVertexShader,
    fragmentShader: holoFragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uOpacity: { value: 0.15 },
      uScanSpeed: { value: 2.0 },
      uGridScale: { value: 12.0 },
      uLineColor: { value: new THREE.Color('#FFFFFF') },
      uBgColor: { value: new THREE.Color('#0F1115') },
    },
    transparent: true,
    side: THREE.DoubleSide,
    blending: THREE.NormalBlending,
    depthWrite: false,
  })
}

/* ─── Utility: create ShaderMaterial for orbital rings ─── */
export function createRingMaterial(color: string, opacity: number): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    vertexShader: ringVertexShader,
    fragmentShader: ringFragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uOpacity: { value: opacity },
      uColor: { value: new THREE.Color(color) },
    },
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false,
  })
}

/* ─── Procedural glow sprite texture ─── */
export function makeGlowTexture(): THREE.CanvasTexture {
  const c = document.createElement('canvas')
  c.width = 128; c.height = 128
  const ctx = c.getContext('2d')!
  const grad = ctx.createRadialGradient(64, 64, 0, 64, 64, 64)
  grad.addColorStop(0, 'rgba(255, 255, 255, 0.6)')
  grad.addColorStop(0.2, 'rgba(200, 210, 230, 0.3)')
  grad.addColorStop(0.5, 'rgba(150, 170, 200, 0.1)')
  grad.addColorStop(1, 'rgba(0,0,0,0)')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, 128, 128)
  return new THREE.CanvasTexture(c)
}
