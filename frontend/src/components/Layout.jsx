import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Mic,
  HelpCircle,
  BookOpen,
  GraduationCap,
  Heart,
  Menu,
  X,
  User,
  LogOut,
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

/**
 * AI FOR EDUCATION – Main Layout
 * Left sidebar navigation + content area.
 */

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/podcast', icon: Mic, label: 'AI Podcast' },
  { path: '/quiz', icon: HelpCircle, label: 'AI Quiz' },
  { path: '/story', icon: BookOpen, label: 'AI Story' },
  { path: '/tutor', icon: GraduationCap, label: 'AI Tutor' },
  { path: '/friend', icon: Heart, label: 'AI Friend' },
  { path: '/profile', icon: User, label: 'Profile' },
]

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex h-screen overflow-hidden bg-black">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 border-r border-gray-800
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:inset-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full border border-white/30 flex items-center justify-center">
              <span className="text-xs font-bold">AI</span>
            </div>
            <div>
              <h1 className="text-sm font-semibold tracking-wide">AI FOR EDU</h1>
              <p className="text-[10px] text-gray-400 tracking-widest uppercase">Adaptive Learning</p>
            </div>
          </div>
          <button
            className="lg:hidden text-gray-400 hover:text-white"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-6 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200
                ${
                  isActive
                    ? 'bg-white text-black shadow-lg shadow-white/5'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
            >
              <item.icon size={18} strokeWidth={1.5} />
              <span>{item.label}</span>
              {/* Active indicator */}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-gray-800 space-y-2">
          <button
            onClick={() => { logout(); navigate('/'); }}
            className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-gray-400 hover:text-red-400 hover:bg-gray-800 transition-all duration-200 w-full"
          >
            <LogOut size={18} strokeWidth={1.5} />
            <span>Sign Out</span>
          </button>
          <p className="text-[10px] text-gray-500 tracking-wider uppercase px-4">
            v1.0.0 — Powered by AI
          </p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm flex-shrink-0">
          <button
            className="lg:hidden text-gray-400 hover:text-white transition-colors"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={22} />
          </button>
          <div className="hidden lg:block" />
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400 hidden sm:block">{user?.full_name || user?.username}</span>
            <NavLink to="/profile" className="w-8 h-8 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center hover:border-gray-500 transition-colors">
              <span className="text-xs font-medium">{(user?.full_name || user?.username || 'U')[0].toUpperCase()}</span>
            </NavLink>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="max-w-6xl mx-auto animate-fade-in">
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}
