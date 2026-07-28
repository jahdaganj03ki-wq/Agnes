import { useNavigate, useLocation } from 'react-router-dom'

const navItems = [
  { label: 'Home', icon: '🏠', path: '/' },
  { label: 'Edit Image', icon: '🖌️', path: '/edit' },
  { label: 'Settings', icon: '⚙️', path: '/settings' },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <aside className="w-16 md:w-56 bg-gray-900 border-r border-border flex flex-col py-4 shrink-0">
      <div className="px-4 mb-6">
        <img src="/logo.png" alt="Agnes" className="w-8 h-8 md:w-10 md:h-10" />
      </div>
      <nav className="flex flex-col gap-1 px-2">
        {navItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
              location.pathname === item.path
                ? 'bg-primary/20 text-primary'
                : 'text-text-muted hover:bg-surface-hover hover:text-gray-100'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="hidden md:inline text-sm font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
