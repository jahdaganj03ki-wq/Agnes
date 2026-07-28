import type { PipelineState } from '../types'

interface Props {
  state: PipelineState
  skills: string[]
  enhanced: string | null
}

export default function StatusIndicator({ state, skills, enhanced }: Props) {
  if (state === 'idle' || state === 'input_ready') return null

  return (
    <div className="bg-surface rounded-lg p-4 border border-border space-y-2">
      {state === 'skills_loading' && skills.length > 0 && (
        <div className="text-sm text-text-muted">
          <span className="animate-pulse">⏳</span> Skills loaded: {skills.join(', ')}
        </div>
      )}
      {state === 'enhancing' && (
        <div className="text-sm text-text-muted">
          <span className="animate-pulse">✨</span> Enhancing prompt...
        </div>
      )}
      {state === 'generating' && (
        <div className="text-sm text-text-muted">
          <span className="animate-pulse">🎨</span> Generating image...
        </div>
      )}
      {enhanced && (
        <div className="text-xs text-text-muted border-t border-border pt-2 mt-2">
          <strong>Enhanced:</strong> {enhanced}
        </div>
      )}
    </div>
  )
}
