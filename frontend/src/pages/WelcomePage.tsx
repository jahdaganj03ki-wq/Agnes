import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'

const actions = [
  { label: 'Generate Image', desc: 'Create from scratch', icon: '✨' },
  { label: 'Edit Image', desc: 'Transform an image', icon: '🖌️' },
  { label: 'Variations', desc: 'Remix an image', icon: '🎨' },
  { label: 'Background Remover', desc: 'Remove background', icon: '✂️' },
  { label: 'Image to Video', desc: 'Animate your image', icon: '🎥' },
]

export default function WelcomePage() {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 flex flex-col items-center justify-center px-6">
        <div className="max-w-xl text-center">
          <img src="/logo.png" alt="Agnes AI" className="w-20 h-20 mx-auto mb-4" />
          <h1 className="text-3xl font-bold mb-2">Welcome to Agnes AI</h1>
          <p className="text-text-muted mb-8">
            What would you like to create today?
          </p>
          <div className="grid grid-cols-1 gap-3">
            {actions.map((a) => (
              <button
                key={a.label}
                onClick={() => navigate('/edit')}
                className="flex items-center gap-3 px-5 py-3 rounded-lg bg-surface hover:bg-surface-hover border border-border text-left transition-colors"
              >
                <span className="text-xl">{a.icon}</span>
                <div>
                  <div className="font-medium">{a.label}</div>
                  <div className="text-sm text-text-muted">{a.desc}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
