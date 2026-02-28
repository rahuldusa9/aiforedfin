import { useState, useRef } from 'react'
import { HelpCircle, CheckCircle, XCircle, BarChart3 } from 'lucide-react'
import { generateQuiz, submitQuiz } from '../api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { PageHeader, Card, Input, Select, Button, LoadingSpinner } from '../components/UI'

/**
 * AI FOR EDUCATION – AI Quiz Module
 * Adaptive quiz with ML performance prediction.
 */
export default function Quiz() {
  const { user } = useAuth()
  const toast = useToast()
  const [topic, setTopic] = useState('')
  const [numQuestions, setNumQuestions] = useState(5)
  const [difficulty, setDifficulty] = useState('medium')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [quiz, setQuiz] = useState(null)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const startTime = useRef(null)

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.warning('Please enter a topic first.')
      return
    }
    setLoading(true)
    setError('')
    setQuiz(null)
    setResult(null)
    setAnswers({})

    try {
      const { data } = await generateQuiz(topic, numQuestions, difficulty)
      setQuiz(data)
      startTime.current = Date.now()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate quiz.')
    } finally {
      setLoading(false)
    }
  }

  const handleAnswer = (qIndex, option) => {
    setAnswers((prev) => ({ ...prev, [qIndex]: option }))
  }

  const handleSubmit = async () => {
    const timeTaken = (Date.now() - startTime.current) / 1000
    setSubmitting(true)

    try {
      const { data } = await submitQuiz({
        user_id: user.id,
        topic: quiz.topic,
        difficulty: quiz.difficulty,
        questions: quiz.questions,
        answers,
        time_taken_seconds: timeTaken,
      })
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit quiz.')
    } finally {
      setSubmitting(false)
    }
  }

  const allAnswered = quiz && Object.keys(answers).length === quiz.questions.length

  return (
    <div>
      <PageHeader
        title="AI Quiz"
        subtitle="Test your knowledge with adaptive quizzes"
        icon={HelpCircle}
      />

      {/* Configuration */}
      {!quiz && !result && (
        <Card className="mb-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            <Input
              label="Topic"
              placeholder="e.g., Photosynthesis"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
            />
            <Select
              label="Questions"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value))}
              options={[
                { value: 3, label: '3 Questions' },
                { value: 5, label: '5 Questions' },
                { value: 10, label: '10 Questions' },
              ]}
            />
            <Select
              label="Difficulty"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              options={[
                { value: 'easy', label: 'Easy' },
                { value: 'medium', label: 'Medium' },
                { value: 'hard', label: 'Hard' },
              ]}
            />
          </div>
          <Button onClick={handleGenerate} loading={loading}>
            Generate Quiz
          </Button>
        </Card>
      )}

      {loading && (
        <Card>
          <LoadingSpinner text="Generating quiz questions..." />
        </Card>
      )}

      {error && (
        <Card className="border-red-900/50 mb-4">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {/* Quiz Questions */}
      {quiz && !result && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold">
              {quiz.topic} — {quiz.difficulty.charAt(0).toUpperCase() + quiz.difficulty.slice(1)}
            </h2>
            <span className="text-sm text-gray-400">
              {Object.keys(answers).length}/{quiz.questions.length} answered
            </span>
          </div>

          {quiz.questions.map((q, i) => (
            <Card key={i} className="animate-slide-up" hover={false} style={{ animationDelay: `${i * 0.05}s` }}>
              <p className="text-sm text-gray-400 mb-2">Question {i + 1}</p>
              <p className="text-base font-medium mb-4">{q.question}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {Object.entries(q.options).map(([key, value]) => (
                  <button
                    key={key}
                    onClick={() => handleAnswer(i, key)}
                    className={`text-left px-4 py-3 rounded-lg border text-sm transition-all duration-200 ${
                      answers[i] === key
                        ? 'bg-white text-black border-white'
                        : 'bg-gray-800/50 border-gray-700 text-gray-300 hover:border-gray-500 hover:bg-gray-800'
                    }`}
                  >
                    <span className="font-mono font-bold mr-2">{key}.</span>
                    {value}
                  </button>
                ))}
              </div>
            </Card>
          ))}

          <div className="flex gap-3">
            <Button onClick={handleSubmit} loading={submitting} disabled={!allAnswered}>
              Submit Answers
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                setQuiz(null)
                setAnswers({})
              }}
            >
              Start Over
            </Button>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6 animate-fade-in">
          {/* Score Summary */}
          <Card>
            <div className="text-center py-4">
              <p className="text-6xl font-bold mb-2">{Math.round(result.score)}%</p>
              <p className="text-gray-400">
                {result.correct} out of {result.total} correct
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Average response time: {result.average_response_time}s per question
              </p>
            </div>
          </Card>

          {/* ML Prediction */}
          <Card>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <BarChart3 size={18} />
              AI Performance Analysis
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-800">
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">
                  Predicted Level
                </p>
                <p className="text-xl font-bold capitalize">
                  {result.prediction.predicted_performance}
                </p>
              </div>
              <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-800">
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">
                  Recommended Difficulty
                </p>
                <p className="text-xl font-bold capitalize">
                  {result.prediction.recommended_difficulty}
                </p>
              </div>
              <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-800">
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">
                  Weakness Probability
                </p>
                <p className="text-xl font-bold">
                  {(result.prediction.weakness_probability * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Probability bars */}
            {result.prediction.probabilities && (
              <div className="mt-4 space-y-2">
                {Object.entries(result.prediction.probabilities).map(([level, prob]) => (
                  <div key={level} className="flex items-center gap-3">
                    <span className="text-xs text-gray-400 w-16 capitalize">{level}</span>
                    <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-white/70 rounded-full transition-all duration-700"
                        style={{ width: `${prob * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-12 text-right">
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Detailed Results */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Detailed Results</h3>
            <div className="space-y-3">
              {result.details.map((d, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-lg border ${
                    d.is_correct
                      ? 'border-gray-700 bg-gray-800/30'
                      : 'border-red-900/30 bg-red-950/10'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {d.is_correct ? (
                      <CheckCircle size={18} className="text-white mt-0.5 flex-shrink-0" />
                    ) : (
                      <XCircle size={18} className="text-gray-500 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm font-medium mb-1">{d.question}</p>
                      <p className="text-xs text-gray-400">
                        Your answer: <span className="text-white">{d.user_answer}</span>
                        {!d.is_correct && (
                          <>
                            {' · '}Correct: <span className="text-white">{d.correct_answer}</span>
                          </>
                        )}
                      </p>
                      {d.explanation && (
                        <p className="text-xs text-gray-500 mt-1">{d.explanation}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Button
            onClick={() => {
              setQuiz(null)
              setResult(null)
              setAnswers({})
            }}
          >
            Take Another Quiz
          </Button>
        </div>
      )}
    </div>
  )
}
