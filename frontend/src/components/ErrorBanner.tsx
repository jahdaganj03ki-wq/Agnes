interface Props {
  message: string
  onRetry?: () => void
}

export default function ErrorBanner({ message, onRetry }: Props) {
  return (
    <div className="bg-error-bg border border-error-border text-error-text rounded-lg p-4 flex items-center justify-between">
      <span className="text-sm">{message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="ml-4 px-4 py-1 bg-red-700 hover:bg-red-600 rounded-md text-sm transition-colors shrink-0"
        >
          Retry
        </button>
      )}
    </div>
  )
}
