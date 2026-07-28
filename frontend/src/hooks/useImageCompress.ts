import { useCallback } from 'react'

const MAX_SIZE = 2048
const QUALITY = 0.85

export function useImageCompress() {
  const compress = useCallback((file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        let { width, height } = img
        if (width > MAX_SIZE || height > MAX_SIZE) {
          const ratio = Math.min(MAX_SIZE / width, MAX_SIZE / height)
          width = Math.round(width * ratio)
          height = Math.round(height * ratio)
        }

        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          reject(new Error('Canvas 2D not available'))
          return
        }
        ctx.drawImage(img, 0, 0, width, height)
        resolve(canvas.toDataURL('image/jpeg', QUALITY))
      }
      img.onerror = () => reject(new Error('Failed to load image'))
      img.src = URL.createObjectURL(file)
    })
  }, [])

  return { compress }
}
