import { Routes, Route } from 'react-router-dom'
import WelcomePage from './pages/WelcomePage'
import EditImagePage from './pages/EditImagePage'
import SettingsPage from './pages/SettingsPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      <Route path="/edit" element={<EditImagePage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  )
}

export default App
