import { useState, useRef, useEffect } from 'react'
import { Heart, Send, Smile, Frown, Meh, AlertTriangle } from 'lucide-react'
import { chatWithFriend } from '../api'
import { useAuth } from '../context/AuthContext'
import { PageHeader, Card, Button } from '../components/UI'

/**
 * AI FOR EDUCATION – AI Friend Module
 * Chat interface with sentiment detection and emotional support.
 */

const sentimentIcons = {
  positive: { icon: Smile, color: 'text-green-400' },
  neutral: { icon: Meh, color: 'text-gray-400' },
  stressed: { icon: Frown, color: 'text-orange-400' },
  anxious: { icon: AlertTriangle, color: 'text-red-400' },
}

export default function Friend() {
  const { user } = useAuth()
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: "Hey there! 👋 I'm your AI study buddy. You can talk to me about anything — studies, feelings, or just to chat. How are you doing today?",
      sentiment: 'positive',
    },
  ])
  const [loading, setLoading] = useState(false)
  const chatEndRef = useRef(null)

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!message.trim() || loading) return

    const userMsg = message.trim()
    setMessage('')
    setMessages((prev) => [...prev, { role: 'user', text: userMsg }])
    setLoading(true)

    try {
      const { data } = await chatWithFriend(userMsg, user.id)
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: data.response || "I'm sorry, I couldn't generate a response.",
          sentiment: data.sentiment || 'neutral',
          isNegative: data.is_negative || false,
          confidence: data.confidence || 0,
        },
      ])
    } catch (err) {
      console.error('[Friend] Chat error:', err)
      const errorMessage = err.response?.data?.detail || "I'm sorry, I couldn't process that right now. Please try again in a moment."
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: errorMessage,
          sentiment: 'neutral',
          isNegative: false,
          confidence: 0,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)]">
      <PageHeader
        title="AI Friend"
        subtitle="Your supportive study companion"
        icon={Heart}
      />

      {/* Chat Area */}
      <Card className="flex-1 flex flex-col overflow-hidden !p-0" hover={false}>
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 animate-slide-up ${
                msg.role === 'user' ? 'flex-row-reverse' : ''
              }`}
              style={{ animationDelay: `${Math.min(i * 0.05, 0.3)}s` }}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 border ${
                  msg.role === 'user'
                    ? 'bg-white text-black border-white'
                    : 'bg-gray-800 text-white border-gray-600'
                }`}
              >
                <span className="text-xs font-bold">
                  {msg.role === 'user' ? 'U' : 'AI'}
                </span>
              </div>

              {/* Bubble */}
              <div
                className={`max-w-[75%] ${
                  msg.role === 'user' ? 'text-right' : ''
                }`}
              >
                <div
                  className={`inline-block p-3 rounded-xl text-sm leading-relaxed whitespace-pre-line ${
                    msg.role === 'user'
                      ? 'bg-white text-black rounded-tr-none'
                      : msg.isNegative
                      ? 'bg-gray-700 text-white border border-gray-600 rounded-tl-none'
                      : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-tl-none'
                  }`}
                >
                  {msg.text}
                </div>

                {/* Sentiment badge */}
                {msg.role === 'ai' && msg.sentiment && (
                  <div className={`flex items-center gap-1.5 mt-1.5 text-xs ${
                    msg.role === 'user' ? 'justify-end' : ''
                  }`}>
                    {sentimentIcons[msg.sentiment] ? (() => {
                      const SIcon = sentimentIcons[msg.sentiment].icon
                      return <SIcon size={12} className={sentimentIcons[msg.sentiment].color} />
                    })() : null}
                    <span className="capitalize text-gray-500">{msg.sentiment}</span>
                    {msg.confidence && msg.confidence > 0 && (
                      <span className="text-gray-600">({(msg.confidence * 100).toFixed(0)}%)</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {loading && (
            <div className="flex gap-3 animate-fade-in">
              <div className="w-8 h-8 rounded-full bg-gray-800 border border-gray-600 flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-bold">AI</span>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl rounded-tl-none p-3">
                <div className="flex gap-1">
                  {[0, 1, 2].map((j) => (
                    <div
                      key={j}
                      className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                      style={{ animationDelay: `${j * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="border-t border-gray-800 p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your message..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:border-white/50 focus:ring-0 transition-colors"
              disabled={loading}
            />
            <Button
              onClick={handleSend}
              disabled={!message.trim() || loading}
              className="!px-4"
            >
              <Send size={16} />
            </Button>
          </div>
          <p className="text-[10px] text-gray-600 mt-2 text-center">
            Your emotional state is analyzed to provide better support. All data is private.
          </p>
        </div>
      </Card>
    </div>
  )
}
