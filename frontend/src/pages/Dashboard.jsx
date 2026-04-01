import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { LayoutDashboard, TrendingUp, Brain, Clock, Target } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { getDashboardStats } from '../api'
import { useAuth } from '../context/AuthContext'
import { PageHeader, Card, LoadingShimmer } from '../components/UI'

/**
 * AI FOR EDUCATION – Dashboard Page
 * Minimal statistics, performance graph, and overview.
 */
export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [user.id])

  const loadStats = async () => {
    try {
      const { data } = await getDashboardStats(user.id)
      setStats(data)
    } catch (err) {
      console.error('Failed to load stats:', err)
      // Use default empty stats
      setStats({
        quiz_stats: { total_quizzes: 0, average_score: 0, quiz_history: [] },
        emotional_stats: { total_interactions: 0, sentiment_distribution: {} },
        learning_stats: { modules_used: 0, total_time_minutes: 0 },
      })
    } finally {
      setLoading(false)
    }
  }

  const statCards = stats
    ? [
        {
          label: 'Quizzes Taken',
          value: stats.quiz_stats.total_quizzes,
          icon: Target,
        },
        {
          label: 'Average Score',
          value: `${stats.quiz_stats.average_score}%`,
          icon: TrendingUp,
        },
        {
          label: 'Chat Sessions',
          value: stats.emotional_stats.total_interactions,
          icon: Brain,
        },
        {
          label: 'Study Time',
          value: `${stats.learning_stats.total_time_minutes}m`,
          icon: Clock,
        },
      ]
    : []

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Your learning overview at a glance"
        icon={LayoutDashboard}
      />

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} hover={false}>
              <LoadingShimmer lines={2} />
            </Card>
          ))}
        </div>
      ) : (
        <>
          {/* Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {statCards.map((card, i) => (
              <Card key={i} className="animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-gray-400 uppercase tracking-wider font-medium">
                    {card.label}
                  </span>
                  <card.icon size={16} className="text-gray-500" strokeWidth={1.5} />
                </div>
                <p className="text-3xl font-bold tracking-tight">{card.value}</p>
              </Card>
            ))}
          </div>

          {/* Performance Graph */}
          <Card className="mb-8">
            <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <TrendingUp size={18} strokeWidth={1.5} />
              Performance Trend
            </h2>
            {stats.quiz_stats.quiz_history.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={stats.quiz_stats.quiz_history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1A1A1A" />
                    <XAxis
                      dataKey="topic"
                      stroke="#555"
                      tick={{ fontSize: 11, fill: '#777' }}
                      tickLine={false}
                    />
                    <YAxis
                      stroke="#555"
                      tick={{ fontSize: 11, fill: '#777' }}
                      tickLine={false}
                      domain={[0, 100]}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1A1A1A',
                        border: '1px solid #2A2A2A',
                        borderRadius: '8px',
                        color: '#FFF',
                        fontSize: '12px',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#FFFFFF"
                      strokeWidth={2}
                      dot={{ fill: '#FFFFFF', r: 4, strokeWidth: 0 }}
                      activeDot={{ r: 6, fill: '#FFFFFF' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center">
                <p className="text-gray-500 text-sm">
                  No quiz data yet. Take a quiz to see your performance trend.
                </p>
              </div>
            )}
          </Card>

          {/* Sentiment Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <h2 className="text-lg font-semibold mb-4">Emotional Wellness</h2>
              {Object.keys(stats.emotional_stats.sentiment_distribution).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(stats.emotional_stats.sentiment_distribution).map(
                    ([sentiment, count]) => (
                      <div key={sentiment} className="flex items-center justify-between">
                        <span className="text-sm text-gray-300 capitalize">{sentiment}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-white/60 rounded-full transition-all duration-500"
                              style={{
                                width: `${
                                  (count / stats.emotional_stats.total_interactions) * 100
                                }%`,
                              }}
                            />
                          </div>
                          <span className="text-xs text-gray-500 w-8 text-right">{count}</span>
                        </div>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">
                  Chat with AI Friend to track emotional wellness.
                </p>
              )}
            </Card>

            <Card>
              <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: 'Take a Quiz', path: '/quiz', emoji: '📝' },
                  { label: 'Listen to Podcast', path: '/podcast', emoji: '🎙️' },
                  { label: 'Read a Story', path: '/story', emoji: '📖' },
                  { label: 'Chat with Friend', path: '/friend', emoji: '💬' },
                ].map((action) => (
                  <Link
                    key={action.path}
                    to={action.path}
                    className="flex items-center gap-3 p-3 rounded-lg bg-gray-800/50 border border-gray-800 hover:border-gray-600 hover:bg-gray-800 transition-all duration-200 text-sm group"
                  >
                    <span className="text-lg">{action.emoji}</span>
                    <span className="text-gray-300 group-hover:text-white transition-colors">
                      {action.label}
                    </span>
                  </Link>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
