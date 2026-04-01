import { useState, useEffect } from 'react'
import { User, Mail, Shield, BarChart3, MessageCircle, Clock } from 'lucide-react'
import { getDashboardStats } from '../api'
import { useAuth } from '../context/AuthContext'
import { PageHeader, Card, LoadingShimmer } from '../components/UI'

/**
 * AI FOR EDUCATION – Profile Page
 * User information, activity summary, and account management.
 */
export default function Profile() {
  const { user, logout } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadStats = async () => {
      try {
        const { data } = await getDashboardStats(user.id)
        setStats(data)
      } catch {
        // Stats might not be available
      } finally {
        setLoading(false)
      }
    }
    loadStats()
  }, [user.id])

  const infoItems = [
    { label: 'Username', value: user.username, icon: User },
    { label: 'Email', value: user.email, icon: Mail },
    { label: 'Full Name', value: user.full_name || '—', icon: User },
    { label: 'Role', value: user.role || 'student', icon: Shield },
  ]

  return (
    <div>
      <PageHeader title="Profile" subtitle="Your account and activity" icon={User} />

      {/* User Info Card */}
      <Card className="mb-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-white text-black flex items-center justify-center text-2xl font-bold">
            {(user.full_name || user.username || 'U')[0].toUpperCase()}
          </div>
          <div>
            <h2 className="text-xl font-bold">{user.full_name || user.username}</h2>
            <p className="text-sm text-gray-400">@{user.username}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {infoItems.map((item) => (
            <div key={item.label} className="flex items-center gap-3 p-3 rounded-lg bg-gray-900 border border-gray-800">
              <item.icon size={16} className="text-gray-500" />
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider">{item.label}</p>
                <p className="text-sm text-gray-200">{item.value}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Activity Summary */}
      <Card className="mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <BarChart3 size={18} strokeWidth={1.5} />
          Activity Summary
        </h3>

        {loading ? (
          <LoadingShimmer lines={3} />
        ) : stats ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Quizzes', value: stats.quiz_stats?.total_quizzes || 0, icon: BarChart3 },
              { label: 'Avg Score', value: `${stats.quiz_stats?.average_score || 0}%`, icon: BarChart3 },
              { label: 'Chats', value: stats.emotional_stats?.total_interactions || 0, icon: MessageCircle },
              { label: 'Study Time', value: `${stats.learning_stats?.total_time_minutes || 0}m`, icon: Clock },
            ].map((stat) => (
              <div key={stat.label} className="text-center p-4 rounded-lg bg-gray-900 border border-gray-800">
                <stat.icon size={16} className="mx-auto text-gray-500 mb-2" />
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No activity data available yet. Start learning!</p>
        )}
      </Card>

      {/* Danger Zone */}
      <Card>
        <h3 className="text-lg font-semibold mb-2">Account</h3>
        <p className="text-sm text-gray-400 mb-4">Manage your session</p>
        <button
          onClick={logout}
          className="px-4 py-2 bg-gray-900 border border-red-900/50 text-red-400 rounded-lg text-sm hover:bg-red-950/30 hover:border-red-700 transition-colors"
        >
          Sign Out
        </button>
      </Card>
    </div>
  )
}
