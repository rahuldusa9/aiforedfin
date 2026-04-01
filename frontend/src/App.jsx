import { Routes, Route } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import AuthPage from './pages/AuthPage'
import Dashboard from './pages/Dashboard'
import Podcast from './pages/Podcast'
import Quiz from './pages/Quiz'
import Story from './pages/Story'
import Tutor from './pages/Tutor'
import Friend from './pages/Friend'
import Profile from './pages/Profile'
import Flashcards from './pages/Flashcards'
import Progress from './pages/Progress'

/**
 * AI FOR EDUCATION – Root Application Component
 */
export default function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      </div>
    )
  }

  if (!user) {
    return <AuthPage />
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/podcast" element={<Podcast />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/story" element={<Story />} />
        <Route path="/tutor" element={<Tutor />} />
        <Route path="/friend" element={<Friend />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/flashcards" element={<Flashcards />} />
        <Route path="/progress" element={<Progress />} />
      </Routes>
    </Layout>
  )
}
