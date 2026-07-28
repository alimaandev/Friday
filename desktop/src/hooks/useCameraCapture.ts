/**
 * Capture a single frame from a MediaStream as a base64 PNG string.
 * Pure function — no React hooks.
 */
export function captureFrame(stream: MediaStream | null): string | null {
  if (!stream) return null
  const video = document.createElement('video')
  video.srcObject = stream
  video.play()

  const canvas = document.createElement('canvas')
  canvas.width = 320
  canvas.height = 240
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    video.remove()
    return null
  }

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
  video.remove()
  canvas.remove()

  return canvas.toDataURL('image/png').split(',')[1]
}