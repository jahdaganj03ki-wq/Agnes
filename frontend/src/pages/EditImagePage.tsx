import { useCallback, useRef, useState } from 'react'
import Sidebar from '../components/Sidebar'
import ImageUploader from '../components/ImageUploader'
import PromptInput from '../components/PromptInput'
import StatusIndicator from '../components/StatusIndicator'
import ResultCard from '../components/ResultCard'
import ErrorBanner from '../components/ErrorBanner'
import { useEditImage } from '../hooks/useEditImage'
import { useRetryState } from '../hooks/useRetryState'
export default function EditImagePage() {
  const [prompt, setPrompt] = useState('')
  const [aspectRatio, setAspectRatio] = useState('1:1')
  const imageRef = useRef<string | null>(null)
  const retry = useRetryState()
  const { state, skills, enhanced, imageUrl, revised, error, run } = useEditImage()

  const isRunning = state === 'skills_loading' || state === 'enhancing' || state === 'generating'

  const handleImage = useCallback((base64: string) => {
    imageRef.current = base64
  }, [])

  const handleSubmit = useCallback(async () => {
    const img = imageRef.current
    if (!prompt.trim() || !img) return
    retry.save({ prompt, enhancedPrompt: '', imageUrl: '', revisedPrompt: null, aspectRatio, imageBase64: img })
    await run(prompt, img, aspectRatio)
  }, [prompt, aspectRatio, run, retry])

  const handleRetry = useCallback(async () => {
    const saved = retry.load()
    if (!saved) return
    setPrompt(saved.prompt)
    setAspectRatio(saved.aspectRatio)
    imageRef.current = saved.imageBase64
    await run(saved.prompt, saved.imageBase64, saved.aspectRatio)
  }, [run, retry])

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 flex flex-col p-6 max-w-3xl mx-auto w-full gap-6">
        <h1 className="text-2xl font-bold">Edit Image</h1>

        <ImageUploader onImage={handleImage} disabled={isRunning} />

        <PromptInput
          value={prompt}
          onChange={setPrompt}
          disabled={isRunning}
          onSubmit={handleSubmit}
          aspectRatio={aspectRatio}
          onAspectRatioChange={setAspectRatio}
        />

        <StatusIndicator state={state} skills={skills} enhanced={enhanced} />

        {error && <ErrorBanner message={error} onRetry={state === 'error' ? handleRetry : undefined} />}

        {(imageUrl || retry.load()?.imageUrl) && (
          <ResultCard
            imageUrl={imageUrl || retry.load()?.imageUrl || ''}
            revisedPrompt={revised || retry.load()?.revisedPrompt || null}
          />
        )}
      </main>
    </div>
  )
}
