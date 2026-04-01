import { useState, useEffect, useRef } from 'react'
import { BookOpen, Play, Pause, Globe, Sparkles } from 'lucide-react'
import { generateStory, generateMultilingualStory, getStoryLanguages } from '../api'
import { useToast } from '../context/ToastContext'
import { PageHeader, Card, Input, Button, AudioPlayer, LoadingSpinner } from '../components/UI'

/**
 * AI FOR EDUCATION – AI Storytelling Module
 * Immersive storybook-style reading experience with multilingual support.
 * Features prosody-enhanced narration in 25+ languages.
 */

const GENRES = [
  { id: 'educational', name: 'Educational', emoji: '📚' },
  { id: 'adventure', name: 'Adventure', emoji: '🗺️' },
  { id: 'mystery', name: 'Mystery', emoji: '🔍' },
  { id: 'science', name: 'Science Fiction', emoji: '🚀' },
  { id: 'fantasy', name: 'Fantasy', emoji: '🧙' },
  { id: 'history', name: 'Historical', emoji: '🏛️' },
  { id: 'fable', name: 'Fable', emoji: '🦊' },
]

const AGE_GROUPS = [
  { id: 'children', name: 'Children (5-8)', emoji: '👶' },
  { id: 'kids', name: 'Kids (9-12)', emoji: '🧒' },
  { id: 'teens', name: 'Teens (13-17)', emoji: '🎓' },
  { id: 'adults', name: 'Adults (18+)', emoji: '👨' },
]

export default function Story() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [cursorPos, setCursorPos] = useState(0)
  const [isReading, setIsReading] = useState(false)
  const [readingSpeed, setReadingSpeed] = useState(300)
  const intervalRef = useRef(null)
  const storyRef = useRef(null)
  const toast = useToast()

  // Multilingual settings
  const [languages, setLanguages] = useState([])
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [selectedGenre, setSelectedGenre] = useState('educational')
  const [selectedAgeGroup, setSelectedAgeGroup] = useState('kids')
  const [isMultilingual, setIsMultilingual] = useState(false)

  // Load available languages on mount
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const { data } = await getStoryLanguages()
        setLanguages(data)
      } catch (err) {
        console.error('Failed to load languages:', err)
        // Fallback languages
        setLanguages([
          { code: 'en', name: 'English', voice_count: 9 },
          { code: 'es', name: 'Spanish', voice_count: 6 },
          { code: 'fr', name: 'French', voice_count: 5 },
          { code: 'de', name: 'German', voice_count: 5 },
          { code: 'zh', name: 'Chinese', voice_count: 6 },
          { code: 'ja', name: 'Japanese', voice_count: 4 },
          { code: 'ko', name: 'Korean', voice_count: 4 },
          { code: 'hi', name: 'Hindi', voice_count: 2 },
          { code: 'ar', name: 'Arabic', voice_count: 4 },
          { code: 'pt', name: 'Portuguese', voice_count: 4 },
        ])
      }
    }
    fetchLanguages()
  }, [])

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [])

  const startReadingCursor = (text) => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    setCursorPos(0)
    setIsReading(true)

    const paragraphs = text.split(/\n\s*\n|\n{2,}/).filter(p => p.trim() && p.trim() !== '---')
    const totalWords = paragraphs.reduce((count, p) => count + p.split(' ').length, 0)
    let pos = 0

    intervalRef.current = setInterval(() => {
      pos += 1
      if (pos >= totalWords) {
        clearInterval(intervalRef.current)
        setIsReading(false)
        return
      }
      setCursorPos(pos)
    }, readingSpeed)
  }

  const stopReadingCursor = () => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    setIsReading(false)
    setCursorPos(0)
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
      let data
      if (isMultilingual) {
        const response = await generateMultilingualStory({
          topic,
          language: selectedLanguage,
          genre: selectedGenre,
          ageGroup: selectedAgeGroup,
          wordCount: 400,
          includeAudio: true,
          includeProsody: true,
        })
        data = response.data
      } else {
        const response = await generateStory(topic)
        data = response.data
      }
      setResult(data)
      toast.success('Story generated successfully!')
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to generate story.'
      setError(message)
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }

  // Render story with storybook styling
  const renderStoryText = (text) => {
    const paragraphs = text.split(/\n\s*\n|\n{2,}/).filter(p => p.trim())
    let globalWordIndex = 0

    return (
      <div className="space-y-8">
        {paragraphs.map((paragraph, pIndex) => {
          // Scene transition
          if (paragraph.trim() === '---') {
            return (
              <div key={pIndex} className="flex items-center justify-center gap-4 py-4">
                <div className="w-12 h-px bg-gradient-to-r from-transparent to-amber-500/40" />
                <span className="text-amber-500/60 text-lg">✦</span>
                <div className="w-12 h-px bg-gradient-to-l from-transparent to-amber-500/40" />
              </div>
            )
          }

          const isDialogue = paragraph.trim().startsWith('"') || paragraph.trim().startsWith('"')
          const isFirstParagraph = pIndex === 0
          const words = paragraph.split(' ')
          const paragraphStartIndex = globalWordIndex
          globalWordIndex += words.length

          return (
            <p
              key={pIndex}
              className={`
                text-lg leading-[2] tracking-wide
                ${isDialogue ? 'pl-6 border-l-2 border-amber-500/30 italic text-amber-100/90' : 'text-gray-100'}
                ${isFirstParagraph ? 'first-letter:text-5xl first-letter:font-serif first-letter:font-bold first-letter:text-amber-400 first-letter:float-left first-letter:mr-3 first-letter:mt-1' : ''}
              `}
              style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}
            >
              {words.map((word, wIndex) => {
                const absoluteIndex = paragraphStartIndex + wIndex
                const isCurrentWord = isReading && absoluteIndex === cursorPos
                const isReadWord = isReading && absoluteIndex < cursorPos
                const isUnreadWord = isReading && absoluteIndex > cursorPos

                return (
                  <span
                    key={wIndex}
                    className={`
                      transition-all duration-300 ease-out
                      ${isCurrentWord
                        ? 'text-amber-300 font-semibold scale-105 inline-block bg-amber-500/20 px-1 rounded'
                        : isReadWord
                        ? 'text-gray-100'
                        : isUnreadWord
                        ? 'text-gray-500/70'
                        : ''
                      }
                    `}
                  >
                    {word}{' '}
                  </span>
                )
              })}
            </p>
          )
        })}
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title="AI Storytelling"
        subtitle="Learn through immersive narrative experiences in 25+ languages"
        icon={BookOpen}
      />

      {/* Input Card */}
      <Card className="mb-6">
        <div className="space-y-4">
          {/* Topic Input */}
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
              <Sparkles size={16} />
              Generate Story
            </Button>
          </div>

          {/* Multilingual Toggle */}
          <div className="flex items-center gap-3 pt-2 border-t border-gray-700/50">
            <button
              onClick={() => setIsMultilingual(!isMultilingual)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
                transition-all duration-200 border
                ${isMultilingual
                  ? 'bg-purple-600/30 border-purple-500/50 text-purple-300'
                  : 'bg-gray-800/50 border-gray-700/50 text-gray-400 hover:bg-gray-700/50'
                }
              `}
            >
              <Globe size={16} />
              Multilingual Mode
            </button>
            {isMultilingual && (
              <span className="text-xs text-gray-500">
                Generate stories in any of 25+ languages with expressive prosody
              </span>
            )}
          </div>

          {/* Multilingual Options */}
          {isMultilingual && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-3 animate-fade-in">
              {/* Language Selection */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Language</label>
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 text-gray-100 rounded-lg px-3 py-2 text-sm"
                >
                  {languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name} ({lang.voice_count} voices)
                    </option>
                  ))}
                </select>
              </div>

              {/* Genre Selection */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Genre</label>
                <select
                  value={selectedGenre}
                  onChange={(e) => setSelectedGenre(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 text-gray-100 rounded-lg px-3 py-2 text-sm"
                >
                  {GENRES.map((genre) => (
                    <option key={genre.id} value={genre.id}>
                      {genre.emoji} {genre.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Age Group Selection */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Age Group</label>
                <select
                  value={selectedAgeGroup}
                  onChange={(e) => setSelectedAgeGroup(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 text-gray-100 rounded-lg px-3 py-2 text-sm"
                >
                  {AGE_GROUPS.map((age) => (
                    <option key={age.id} value={age.id}>
                      {age.emoji} {age.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>
      </Card>

      {loading && (
        <Card>
          <LoadingSpinner text={isMultilingual ? `Crafting your ${selectedLanguage.toUpperCase()} story with prosody...` : "Crafting your story..."} />
        </Card>
      )}

      {error && (
        <Card className="border-red-900/50">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {/* Storybook Result */}
      {result && (
        <div className="space-y-6 animate-fade-in">
          {/* Audio Player */}
          <AudioPlayer src={result.audio_url} />

          {/* Storybook Container */}
          <div className="relative">
            {/* Decorative book spine effect */}
            <div className="absolute left-0 top-0 bottom-0 w-2 bg-gradient-to-r from-amber-900/40 to-transparent rounded-l-lg" />

            <div
              ref={storyRef}
              className="
                relative overflow-hidden rounded-xl
                bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800
                border border-amber-900/30
                shadow-2xl shadow-amber-900/10
              "
            >
              {/* Top decorative border */}
              <div className="h-1 bg-gradient-to-r from-amber-700/50 via-amber-500/50 to-amber-700/50" />

              {/* Header */}
              <div className="px-8 py-6 border-b border-amber-900/20 bg-gradient-to-b from-amber-900/10 to-transparent">
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">📖</span>
                    <div>
                      <h2 className="text-xl font-serif font-semibold text-amber-100">
                        {result.topic}
                      </h2>
                      <div className="flex items-center gap-2 text-sm text-amber-500/60 italic">
                        <span>An Educational Tale</span>
                        {result.language_name && (
                          <>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <Globe size={12} />
                              {result.language_name}
                            </span>
                          </>
                        )}
                        {result.has_prosody && (
                          <>
                            <span>•</span>
                            <span className="text-purple-400">✨ Prosody Enhanced</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Reading Controls */}
                  <div className="flex items-center gap-3">
                    {/* Speed Control */}
                    <select
                      value={readingSpeed}
                      onChange={(e) => setReadingSpeed(Number(e.target.value))}
                      className="bg-gray-800 border border-amber-900/30 text-amber-100 text-xs rounded px-2 py-1"
                      disabled={isReading}
                    >
                      <option value={400}>Slow</option>
                      <option value={300}>Normal</option>
                      <option value={200}>Fast</option>
                    </select>

                    {!isReading ? (
                      <button
                        onClick={() => startReadingCursor(result.story_text)}
                        className="
                          flex items-center gap-2 px-4 py-2 rounded-lg
                          bg-amber-600/20 hover:bg-amber-600/30
                          border border-amber-500/30
                          text-amber-300 text-sm font-medium
                          transition-all duration-200
                        "
                      >
                        <Play size={14} fill="currentColor" />
                        Read to Me
                      </button>
                    ) : (
                      <button
                        onClick={stopReadingCursor}
                        className="
                          flex items-center gap-2 px-4 py-2 rounded-lg
                          bg-red-600/20 hover:bg-red-600/30
                          border border-red-500/30
                          text-red-300 text-sm font-medium
                          transition-all duration-200
                        "
                      >
                        <Pause size={14} />
                        Stop
                      </button>
                    )}
                  </div>
                </div>

                {/* Metadata badges */}
                {result.genre && (
                  <div className="flex items-center gap-2 mt-3">
                    <span className="px-2 py-1 bg-purple-500/20 border border-purple-500/30 rounded text-xs text-purple-300">
                      {GENRES.find(g => g.id === result.genre)?.emoji} {result.genre}
                    </span>
                    {result.age_group && (
                      <span className="px-2 py-1 bg-blue-500/20 border border-blue-500/30 rounded text-xs text-blue-300">
                        {AGE_GROUPS.find(a => a.id === result.age_group)?.emoji} {result.age_group}
                      </span>
                    )}
                    {result.word_count && (
                      <span className="px-2 py-1 bg-gray-700/50 border border-gray-600/30 rounded text-xs text-gray-400">
                        {result.word_count} words
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Story Content */}
              <div className="px-10 py-8 max-h-[600px] overflow-y-auto custom-scrollbar">
                {/* Opening ornament */}
                <div className="flex justify-center mb-8">
                  <span className="text-amber-500/40 text-2xl tracking-[1em]">❦ ❦ ❦</span>
                </div>

                {renderStoryText(result.story_text)}

                {/* Closing ornament */}
                <div className="flex justify-center mt-10">
                  <span className="text-amber-500/40 text-xl">— The End —</span>
                </div>
              </div>

              {/* Bottom decorative border */}
              <div className="h-1 bg-gradient-to-r from-amber-700/50 via-amber-500/50 to-amber-700/50" />
            </div>
          </div>
        </div>
      )}

      {/* Custom scrollbar styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(217, 119, 6, 0.3);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(217, 119, 6, 0.5);
        }
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}
