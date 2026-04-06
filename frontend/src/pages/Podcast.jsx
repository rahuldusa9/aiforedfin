import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mic, Play, FileText, Globe, Clock, Sparkles } from 'lucide-react'
import { generatePodcast, getStoryLanguages } from '../api'
import { useToast } from '../context/ToastContext'
import { PageHeader, Card, Input, Button, AudioPlayer, LoadingSpinner, Select } from '../components/UI'

/**
 * AI FOR EDUCATION – AI Podcast Module
 * Generate educational podcasts with 2 speakers.
 */
export default function Podcast() {
  const [topic, setTopic] = useState('')
  const [language, setLanguage] = useState('en')
  const [length, setLength] = useState('medium')
  const [languages, setLanguages] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [audioCompleted, setAudioCompleted] = useState(false)
  const toast = useToast()
  const navigate = useNavigate()

  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const { data } = await getStoryLanguages()
        setLanguages(data)
      } catch (err) {
        console.error('Failed to load languages:', err)
        setLanguages([
          { code: 'en', name: 'English', voice_count: 9 },
          { code: 'es', name: 'Spanish', voice_count: 6 },
          { code: 'fr', name: 'French', voice_count: 5 },
          { code: 'de', name: 'German', voice_count: 5 },
          { code: 'hi', name: 'Hindi', voice_count: 2 },
          { code: 'ja', name: 'Japanese', voice_count: 4 },
          { code: 'ko', name: 'Korean', voice_count: 4 }
        ])
      }
    }
    fetchLanguages()
  }, [])

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.warning('Please enter a topic first.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    setAudioCompleted(false)

    try {
      const { data } = await generatePodcast(topic, language, length)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate podcast. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleAudioEnded = () => {
    setAudioCompleted(true)
    toast.success('Podcast completed! Why not test your knowledge with a quiz?', { duration: 5000 })
  }

  const takeQuiz = () => {
    let transcript = '';
    if (result && result.script) {
      transcript = result.script.map(s => `${s.speaker}: ${s.text}`).join('\n');
    }
    navigate('/quiz', { state: { topic: result?.topic || topic, content: transcript } })
  }

  return (
    <div>
      <PageHeader
        title="AI Podcast"
        subtitle="Generate educational podcasts on any topic"
        icon={Mic}
      />

      {/* Input Section */}
      <Card className="mb-6">
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Enter a topic (e.g., Quantum Physics, World War II, Machine Learning)"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
              />
            </div>
            <Button onClick={handleGenerate} loading={loading} className="sm:self-end">
              <Sparkles size={16} />
              Generate Podcast
            </Button>
          </div>

          {/* Options */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 animate-fade-in">
              {/* Language Selection */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Language</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 text-gray-100 rounded-lg px-3 py-2 text-sm"
                >
                  {languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name} ({lang.voice_count} voices)
                    </option>
                  ))}
                </select>
              </div>

              {/* Length Selection */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Length</label>
                <select
                  value={length}
                  onChange={(e) => setLength(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 text-gray-100 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="short">Short (~3 mins)</option>
                  <option value="medium">Medium (~5 mins)</option>
                  <option value="long">Long (~10 mins)</option>
                </select>
              </div>
          </div>
        </div>
      </Card>

      {/* Loading */}
      {loading && (
        <Card>
          <LoadingSpinner text="Generating podcast script and audio... This may take a minute." />
        </Card>
      )}

      {/* Error */}
      {error && (
        <Card className="border-red-900/50">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-6 animate-fade-in">
          {/* Audio Player and Quiz Prompt */}
          <Card className="flex flex-col md:flex-row items-center gap-6">
            <div className="flex-1 w-full">
              <AudioPlayer src={result.audio_url} onEnded={handleAudioEnded} />
            </div>
            {audioCompleted && (
              <div className="animate-fade-in w-full md:w-auto flex-shrink-0 flex items-center gap-3 bg-indigo-900/40 p-3 rounded-lg border border-indigo-500/30">
                <span className="text-sm text-indigo-200 block">Ready to test your knowledge?</span>
                <Button onClick={takeQuiz} className="bg-indigo-600 hover:bg-indigo-500 text-white border-0 py-2">
                  <FileText size={16} />
                  Take Quiz Now
                </Button>
              </div>
            )}
          </Card>

          {/* Script */}
          <Card>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Play size={16} />
              Podcast Script — {result.topic}
            </h2>
            <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
              {result.script.map((entry, i) => (
                <div
                  key={i}
                  className={`flex gap-3 animate-slide-up ${
                    entry.speaker === 'Host' ? '' : 'flex-row-reverse text-right'
                  }`}
                  style={{ animationDelay: `${i * 0.05}s` }}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold border ${
                      entry.speaker === 'Host'
                        ? 'bg-white text-black border-white'
                        : 'bg-gray-800 text-white border-gray-600'
                    }`}
                  >
                    {entry.speaker[0]}
                  </div>
                  <div
                    className={`flex-1 p-3 rounded-lg ${
                      entry.speaker === 'Host'
                        ? 'bg-gray-800/50 border border-gray-800'
                        : 'bg-gray-900 border border-gray-700'
                    }`}
                  >
                    <p className="text-xs text-gray-400 mb-1 font-medium">{entry.speaker}</p>
                    <p className="text-sm text-gray-200 leading-relaxed">{entry.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
