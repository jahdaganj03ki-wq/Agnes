import { useCallback } from 'react'
import type { RetryState } from '../types'

const KEY = 'agnes-retry-state'

export function useRetryState() {
  const save = useCallback((state: RetryState) => {
    try {
      localStorage.setItem(KEY, JSON.stringify(state))
    } catch { /* quota exceeded */ }
  }, [])

  const load = useCallback((): RetryState | null => {
    try {
      const raw = localStorage.getItem(KEY)
      return raw ? (JSON.parse(raw) as RetryState) : null
    } catch {
      return null
    }
  }, [])

  const clear = useCallback(() => {
    try {
      localStorage.removeItem(KEY)
    } catch { /* noop */ }
  }, [])

  return { save, load, clear }
}
