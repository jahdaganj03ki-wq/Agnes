import { Routes, Route } from 'react-router-dom'
import WelcomePage from './pages/WelcomePage'
import EditImagePage from './pages/EditImagePage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      <Route path="/edit" element={<EditImagePage />} />
    </Routes>
  )
}

export default App
