import { useCallback, useRef, useState } from 'react'
import type { PipelineState } from '../types'

interface UseEditImageReturn {
  state: PipelineState
  skills: string[]
  enhanced: string | null
  imageUrl: string
  revised: string | null
  error: string | null
  run: (prompt: string, imageBase64: string, aspectRatio: string) => Promise<void>
  cancel: () => void
}

export function useEditImage(): UseEditImageReturn {
  const [state, setState] = useState<PipelineState>('idle')
  const [skills, setSkills] = useState<string[]>([])
  const [enhanced, setEnhanced] = useState<string | null>(null)
  const [imageUrl, setImageUrl] = useState('')
  const [revised, setRevised] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const cancel = useCallback(() => {
    abortRef.current?.abort()
    setState('idle')
  }, [])

  const run = useCallback(async (
    prompt: string,
    imageBase64: string,
    aspectRatio: string,
  ) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setState('skills_loading')
    setSkills([])
    setEnhanced(null)
    setImageUrl('')
    setRevised(null)
    setError(null)

    try {
      const res = await fetch('/api/edit-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, image_base64: imageBase64, aspect_ratio: aspectRatio }),
        signal: controller.signal,
      })

      if (!res.ok) {
        setState('error')
        setError(`Server error: ${res.status}`)
        return
      }

      const reader = res.body?.getReader()
      if (!reader) {
        setState('error')
        setError('No response body')
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let event = ''
        let data = ''

        for (const line of lines) {
          if (controller.signal.aborted) break
          if (line.startsWith('event: ')) event = line.slice(7)
          else if (line.startsWith('data: ')) data = line.slice(6)
          else if (line === '' && event) {
            const parsed = JSON.parse(data)
            switch (event) {
              case 'skill_loaded':
                setSkills((prev) => [...prev, parsed.skill])
                break
              case 'skill_loading':
                break
              case 'enhancing':
                setState('enhancing')
                break
              case 'prompt_enhanced':
                setEnhanced(parsed.enhanced)
                setState('generating')
                break
              case 'generating':
                setState('generating')
                break
              case 'result':
                setImageUrl(parsed.image_url)
                setRevised(parsed.revised_prompt)
                setState('result')
                break
              case 'error':
                setState('error')
                setError(parsed.message)
                break
            }
            event = ''
            data = ''
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        setState('idle')
        return
      }
      setState('error')
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }, [])

  return { state, skills, enhanced, imageUrl, revised, error, run, cancel }
}
