import { useCallback, useEffect, useState } from 'react'
import Sidebar from '../components/Sidebar'

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('')
  const [masked, setMasked] = useState<string | null>(null)
  const [configured, setConfigured] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'ok' | 'error'; text: string } | null>(null)

  useEffect(() => {
    fetch('/api/settings')
      .then((r) => r.json())
      .then((data) => {
        setConfigured(data.configured)
        setMasked(data.key_masked ?? null)
      })
      .catch(() => setConfigured(false))
  }, [])

  const handleSave = useCallback(async () => {
    const key = apiKey.trim()
    if (!key.startsWith('sk-')) {
      setMessage({ type: 'error', text: 'API key must start with "sk-"' })
      return
    }
    setSaving(true)
    setMessage(null)
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key }),
      })
      const data = await res.json()
      if (data.status === 'ok') {
        setMasked(data.key_masked)
        setConfigured(true)
        setApiKey('')
        setMessage({ type: 'ok', text: 'API key saved successfully.' })
      } else {
        setMessage({ type: 'error', text: data.message || 'Failed to save' })
      }
    } catch {
      setMessage({ type: 'error', text: 'Could not reach the server' })
    } finally {
      setSaving(false)
    }
  }, [apiKey])

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 flex flex-col p-6 max-w-xl mx-auto w-full gap-6">
        <h1 className="text-2xl font-bold">Settings</h1>

        {configured && masked && (
          <div className="bg-green-900/30 border border-green-700 rounded-lg px-4 py-3 text-sm">
            Current API key: <code className="text-green-300">{masked}</code>
          </div>
        )}

        <div className="flex flex-col gap-3">
          <label className="text-sm font-medium text-text-muted">
            Agnes AI API Key
          </label>
          <input
            type="text"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder={configured ? 'Enter new key to replace...' : 'sk-...'}
            className="w-full px-4 py-3 rounded-lg bg-surface border border-border text-gray-100 placeholder-text-muted font-mono"
          />
          <button
            onClick={handleSave}
            disabled={saving || !apiKey.trim()}
            className="self-start px-5 py-2 bg-primary hover:bg-primary-hover rounded-lg transition-colors disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>

        {message && (
          <div
            className={`rounded-lg px-4 py-3 text-sm ${
              message.type === 'ok'
                ? 'bg-green-900/30 border border-green-700 text-green-300'
                : 'bg-red-900/30 border border-red-700 text-red-300'
            }`}
          >
            {message.text}
          </div>
        )}
      </main>
    </div>
  )
}
