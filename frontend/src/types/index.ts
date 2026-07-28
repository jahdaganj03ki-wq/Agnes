export interface RetryState {
  prompt: string
  enhancedPrompt: string
  imageUrl: string
  revisedPrompt: string | null
  aspectRatio: string
  imageBase64: string
}

export type PipelineState =
  | 'idle'
  | 'input_ready'
  | 'uploading'
  | 'skills_loading'
  | 'enhancing'
  | 'generating'
  | 'result'
  | 'error'
  | 'retrying'
