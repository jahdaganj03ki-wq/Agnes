import { useRef } from 'react'

interface Props {
  imageUrl: string
  revisedPrompt: string | null
}

export default function ResultCard({ imageUrl, revisedPrompt }: Props) {
  const linkRef = useRef<HTMLAnchorElement>(null)

  return (
    <div className="bg-surface rounded-lg border border-border p-4 space-y-3">
      <img
        src={imageUrl}
        alt="Generation result"
        className="w-full rounded-lg"
      />
      {revisedPrompt && (
        <p className="text-sm text-text-muted">{revisedPrompt}</p>
      )}
      <a
        ref={linkRef}
        href={imageUrl}
        download="agnes-result.png"
        className="inline-block px-4 py-2 bg-primary hover:bg-primary-hover rounded-lg text-sm transition-colors"
      >
        Download
      </a>
    </div>
  )
}
