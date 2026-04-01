/**
 * AI FOR EDUCATION – Progress/Analytics Page
 * Learning analytics, strengths/weaknesses, and insights.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  getLearningSummary,
  getStrengthWeakness,
  getLearningVelocity,
  getRecommendations,
  getGamificationStats,
} from '../api';

export default function Progress() {
  const { user } = useAuth();

  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [strengths, setStrengths] = useState(null);
  const [velocity, setVelocity] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [gamification, setGamification] = useState(null);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user, timeRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [summaryRes, strengthsRes, velocityRes, recsRes, gamRes] = await Promise.all([
        getLearningSummary(user.id, timeRange),
        getStrengthWeakness(user.id),
        getLearningVelocity(user.id),
        getRecommendations(user.id),
        getGamificationStats(user.id),
      ]);

      setSummary(summaryRes.data);
      setStrengths(strengthsRes.data);
      setVelocity(velocityRes.data);
      setRecommendations(recsRes.data.recommendations || []);
      setGamification(gamRes.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-white/30 border-t-white rounded-full mx-auto"></div>
          <p className="text-white/70 mt-4">Loading your progress...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Your Progress</h1>
          <p className="text-white/70">Track your learning journey</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(parseInt(e.target.value))}
          className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Level & XP Card */}
      {gamification && (
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-white/80 text-sm">Level {gamification.level?.level}</div>
              <div className="text-3xl font-bold text-white">{gamification.level?.name}</div>
              <div className="text-white/70 mt-1">{gamification.xp?.toLocaleString()} XP</div>
            </div>
            <div className="text-right">
              <div className="text-6xl">🏆</div>
              <div className="text-white/70 text-sm mt-2">{gamification.badge_count} badges</div>
            </div>
          </div>

          {/* XP Progress */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-white/70 mb-1">
              <span>Progress to Level {(gamification.level?.level || 0) + 1}</span>
              <span>{gamification.level?.progress_percent?.toFixed(0)}%</span>
            </div>
            <div className="h-3 bg-white/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 transition-all"
                style={{ width: `${gamification.level?.progress_percent || 0}%` }}
              />
            </div>
            <div className="text-xs text-white/50 mt-1">
              {gamification.level?.xp_to_next?.toLocaleString()} XP to next level
            </div>
          </div>

          {/* Streak */}
          <div className="mt-4 flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🔥</span>
              <div>
                <div className="text-lg font-bold text-white">{gamification.current_streak} days</div>
                <div className="text-xs text-white/60">Current Streak</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">⭐</span>
              <div>
                <div className="text-lg font-bold text-white">{gamification.longest_streak} days</div>
                <div className="text-xs text-white/60">Best Streak</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <div className="text-3xl font-bold text-white">{summary.total_activities}</div>
            <div className="text-white/70 text-sm">Activities</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <div className="text-3xl font-bold text-blue-400">{summary.total_time_minutes?.toFixed(0)}</div>
            <div className="text-white/70 text-sm">Minutes Studied</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <div className="text-3xl font-bold text-green-400">{summary.quiz_average_score?.toFixed(0)}%</div>
            <div className="text-white/70 text-sm">Quiz Average</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <div className="text-3xl font-bold text-purple-400">{summary.daily_average_minutes?.toFixed(0)}</div>
            <div className="text-white/70 text-sm">Daily Average (min)</div>
          </div>
        </div>
      )}

      {/* Strengths & Weaknesses */}
      {strengths && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Strengths */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="text-2xl">💪</span> Your Strengths
            </h3>
            {strengths.strengths?.length > 0 ? (
              <div className="space-y-3">
                {strengths.strengths.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="text-white">{item.topic}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-white/20 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500"
                          style={{ width: `${item.average_score}%` }}
                        />
                      </div>
                      <span className="text-green-400 text-sm w-12">{item.average_score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-white/60">Complete more activities to see your strengths!</p>
            )}
          </div>

          {/* Weaknesses */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="text-2xl">📈</span> Areas to Improve
            </h3>
            {strengths.weaknesses?.length > 0 ? (
              <div className="space-y-3">
                {strengths.weaknesses.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="text-white">{item.topic}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-white/20 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-orange-500"
                          style={{ width: `${item.average_score}%` }}
                        />
                      </div>
                      <span className="text-orange-400 text-sm w-12">{item.average_score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-white/60">Great work! No weak areas identified.</p>
            )}
          </div>
        </div>
      )}

      {/* Learning Velocity */}
      {velocity && velocity.velocity_status !== 'insufficient_data' && (
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">🚀</span> Learning Velocity
          </h3>
          <div className="flex items-center gap-4">
            <div className={`text-4xl ${
              velocity.velocity_status === 'accelerating' ? 'text-green-400' :
              velocity.velocity_status === 'slowing' ? 'text-orange-400' : 'text-blue-400'
            }`}>
              {velocity.velocity_status === 'accelerating' ? '📈' :
               velocity.velocity_status === 'slowing' ? '📉' : '➡️'}
            </div>
            <div>
              <div className="text-white font-medium">{velocity.velocity_message}</div>
              <div className="text-white/60 text-sm">
                {velocity.weekly_time_change_minutes > 0 ? '+' : ''}{velocity.weekly_time_change_minutes?.toFixed(0)} min from last week
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">💡</span> Personalized Recommendations
          </h3>
          <div className="space-y-3">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border ${
                  rec.priority === 'high' ? 'bg-red-500/10 border-red-500/30' :
                  rec.priority === 'medium' ? 'bg-yellow-500/10 border-yellow-500/30' :
                  'bg-blue-500/10 border-blue-500/30'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-white font-medium">{rec.message}</div>
                    {rec.topic && (
                      <div className="text-white/60 text-sm mt-1">Topic: {rec.topic}</div>
                    )}
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    rec.priority === 'high' ? 'bg-red-500/20 text-red-300' :
                    rec.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                    'bg-blue-500/20 text-blue-300'
                  }`}>
                    {rec.priority}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Badges */}
      {gamification?.badges?.length > 0 && (
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">🏅</span> Your Badges
          </h3>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
            {gamification.badges.map((badge, idx) => (
              <div key={idx} className="text-center p-3 bg-white/5 rounded-lg">
                <div className="text-3xl mb-1">{badge.icon}</div>
                <div className="text-white text-sm font-medium">{badge.name}</div>
                <div className="text-white/50 text-xs">{badge.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Breakdown */}
      {summary?.activity_breakdown && Object.keys(summary.activity_breakdown).length > 0 && (
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">📊</span> Activity Breakdown
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(summary.activity_breakdown).map(([activity, count]) => (
              <div key={activity} className="text-center p-3 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-white">{count}</div>
                <div className="text-white/60 text-sm capitalize">{activity.replace('_', ' ')}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
