import { useState } from 'react'
import { Mic, Play } from 'lucide-react'
import { generatePodcast } from '../api'
import { useToast } from '../context/ToastContext'
import { PageHeader, Card, Input, Button, AudioPlayer, LoadingSpinner } from '../components/UI'

/**
 * AI FOR EDUCATION – AI Podcast Module
 * Generate educational podcasts with 2 speakers.
 */
export default function Podcast() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const toast = useToast()

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.warning('Please enter a topic first.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const { data } = await generatePodcast(topic)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate podcast. Please try again.')
    } finally {
      setLoading(false)
    }
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
            <Mic size={16} />
            Generate Podcast
          </Button>
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
          {/* Audio Player */}
          <AudioPlayer src={result.audio_url} />

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
