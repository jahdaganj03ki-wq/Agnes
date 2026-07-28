import { useRef, useState } from 'react'

interface Props {
  onImage: (base64: string) => void
  disabled?: boolean
}

export default function ImageUploader({ onImage, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState<string | null>(null)

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const dataUrl = reader.result as string
      setPreview(dataUrl)
      // Strip data:image/...;base64, prefix before sending to backend
      const raw = dataUrl.split(',')[1] || dataUrl
      onImage(raw)
    }
    reader.readAsDataURL(file)
  }

  const handleRemove = () => {
    setPreview(null)
    onImage('')
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="border-2 border-dashed border-border rounded-lg p-4 text-center">
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleFile}
        className="hidden"
        disabled={disabled}
      />
      {preview ? (
        <div className="flex flex-col items-center gap-2">
          <img
            src={preview}
            alt="Preview"
            className="max-h-48 rounded-lg object-contain"
          />
          <div className="flex gap-2">
            <button
              onClick={() => inputRef.current?.click()}
              disabled={disabled}
              className="px-3 py-1 text-sm bg-primary hover:bg-primary-hover rounded transition-colors disabled:opacity-50"
            >
              Change
            </button>
            <button
              onClick={handleRemove}
              disabled={disabled}
              className="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 rounded transition-colors disabled:opacity-50"
            >
              Remove
            </button>
          </div>
        </div>
      ) : (
        <>
          <button
            onClick={() => inputRef.current?.click()}
            disabled={disabled}
            className="px-4 py-2 bg-primary hover:bg-primary-hover rounded-lg transition-colors disabled:opacity-50"
          >
            Upload Image
          </button>
          <p className="text-sm text-text-muted mt-2">PNG, JPG up to 10MB</p>
        </>
      )}
    </div>
  )
}
