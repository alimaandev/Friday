import { useRef, useCallback } from 'react'

export function useCameraCapture() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  const captureFrame = useCallback((stream: MediaStream | null): string | null => {
    if (!stream) return null
    const video = document.createElement('video')
    video.srcObject = stream
    video.play()

    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas')
    }
    const canvas = canvasRef.current
    canvas.width = 320
    canvas.height = 240
    const ctx = canvas.getContext('2d')
    if (!ctx) return null

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    video.remove()

    return canvas.toDataURL('image/png').split(',')[1]
  }, [])

  return { captureFrame }
}