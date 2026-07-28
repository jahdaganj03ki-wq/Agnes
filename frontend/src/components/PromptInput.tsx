interface Props {
  value: string
  onChange: (v: string) => void
  disabled?: boolean
  onSubmit: () => void
  aspectRatio: string
  onAspectRatioChange: (r: string) => void
}

const ratios = ['1:1', '16:9', '9:16', '4:3', '3:4']

export default function PromptInput({
  value, onChange, disabled, onSubmit,
  aspectRatio, onAspectRatioChange,
}: Props) {
  return (
    <div className="flex flex-col gap-3">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Describe your edit..."
        disabled={disabled}
        rows={3}
        className="w-full px-4 py-3 rounded-lg bg-surface border border-border text-gray-100 placeholder-text-muted resize-none disabled:opacity-50"
      />
      <div className="flex items-center gap-3">
        <div className="flex gap-2">
          {ratios.map((r) => (
            <button
              key={r}
              onClick={() => onAspectRatioChange(r)}
              disabled={disabled}
              className={`px-3 py-1 text-sm rounded-md border transition-colors ${
                aspectRatio === r
                  ? 'bg-primary text-white border-primary'
                  : 'bg-surface text-text-muted border-border hover:bg-surface-hover'
              } disabled:opacity-50`}
            >
              {r}
            </button>
          ))}
        </div>
        <button
          onClick={onSubmit}
          disabled={disabled || !value.trim()}
          className="ml-auto px-5 py-2 bg-primary hover:bg-primary-hover rounded-lg transition-colors disabled:opacity-50"
        >
          Generate
        </button>
      </div>
    </div>
  )
}
