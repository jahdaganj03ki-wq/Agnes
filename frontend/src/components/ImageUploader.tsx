import { useRef } from 'react'

interface Props {
  onImage: (base64: string) => void
  disabled?: boolean
}

export default function ImageUploader({ onImage, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const dataUrl = reader.result as string
      onImage(dataUrl)
    }
    reader.readAsDataURL(file)
  }

  return (
    <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleFile}
        className="hidden"
        disabled={disabled}
      />
      <button
        onClick={() => inputRef.current?.click()}
        disabled={disabled}
        className="px-4 py-2 bg-primary hover:bg-primary-hover rounded-lg transition-colors disabled:opacity-50"
      >
        Upload Image
      </button>
      <p className="text-sm text-text-muted mt-2">PNG, JPG up to 10MB</p>
    </div>
  )
}
