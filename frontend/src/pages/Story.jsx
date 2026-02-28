import { useState, useEffect, useRef } from 'react'
import { BookOpen } from 'lucide-react'
import { generateStory } from '../api'
import { useToast } from '../context/ToastContext'
import { PageHeader, Card, Input, Button, AudioPlayer, LoadingSpinner } from '../components/UI'

/**
 * AI FOR EDUCATION – AI Storytelling Module
 * Narrative-based learning with audio narration and reading cursor.
 */
export default function Story() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [cursorPos, setCursorPos] = useState(0)
  const [isReading, setIsReading] = useState(false)
  const intervalRef = useRef(null)
  const toast = useToast()

  // Animated reading cursor
  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [])

  const startReadingCursor = (text) => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    setCursorPos(0)
    setIsReading(true)

    const words = text.split(' ')
    let pos = 0

    intervalRef.current = setInterval(() => {
      pos += 1
      if (pos >= words.length) {
        clearInterval(intervalRef.current)
        setIsReading(false)
        return
      }
      setCursorPos(pos)
    }, 300) // ~200 wpm reading speed
  }

  const stopReadingCursor = () => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    setIsReading(false)
  }

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.warning('Please enter a topic first.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    stopReadingCursor()

    try {
      const { data } = await generateStory(topic)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate story.')
    } finally {
      setLoading(false)
    }
  }

  // Render story text with animated cursor
  const renderStoryText = (text) => {
    const words = text.split(' ')
    return (
      <p className="text-base leading-relaxed text-gray-200">
        {words.map((word, i) => (
          <span
            key={i}
            className={`transition-all duration-200 ${
              isReading && i === cursorPos
                ? 'text-white font-semibold bg-white/10 px-0.5 rounded'
                : isReading && i < cursorPos
                ? 'text-white'
                : isReading
                ? 'text-gray-500'
                : 'text-gray-200'
            }`}
          >
            {word}{' '}
          </span>
        ))}
      </p>
    )
  }

  return (
    <div>
      <PageHeader
        title="AI Storytelling"
        subtitle="Learn through engaging narrative explanations"
        icon={BookOpen}
      />

      {/* Input */}
      <Card className="mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Enter a topic (e.g., How DNA Works, The Solar System)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
            />
          </div>
          <Button onClick={handleGenerate} loading={loading} className="sm:self-end">
            <BookOpen size={16} />
            Generate Story
          </Button>
        </div>
      </Card>

      {loading && (
        <Card>
          <LoadingSpinner text="Crafting your educational story..." />
        </Card>
      )}

      {error && (
        <Card className="border-red-900/50">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-6 animate-fade-in">
          {/* Audio */}
          <AudioPlayer src={result.audio_url} />

          {/* Story Text */}
          <Card>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">
                📖 {result.topic}
              </h2>
              <div className="flex gap-2">
                {!isReading ? (
                  <Button
                    variant="secondary"
                    onClick={() => startReadingCursor(result.story_text)}
                    className="text-xs !px-3 !py-1.5"
                  >
                    Start Reading Mode
                  </Button>
                ) : (
                  <Button
                    variant="secondary"
                    onClick={stopReadingCursor}
                    className="text-xs !px-3 !py-1.5"
                  >
                    Stop
                  </Button>
                )}
              </div>
            </div>
            <div className="max-h-[500px] overflow-y-auto pr-2">
              {renderStoryText(result.story_text)}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
