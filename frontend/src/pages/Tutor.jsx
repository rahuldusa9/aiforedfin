import { useState, useRef } from 'react'
import { GraduationCap, ChevronRight, CheckCircle2, BookOpen, Lightbulb, ClipboardCheck } from 'lucide-react'
import { generateLearningPath, saveLearningProgress } from '../api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { PageHeader, Card, Input, Button, LoadingSpinner } from '../components/UI'

/**
 * AI FOR EDUCATION – AI Tutor Module
 * Structured learning paths with concepts, examples, and mini tests.
 */
export default function Tutor() {
  const { user } = useAuth()
  const toast = useToast()
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [path, setPath] = useState(null)
  const [error, setError] = useState('')
  const [activeStep, setActiveStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState(new Set())
  const [showAnswer, setShowAnswer] = useState({})
  const stepStartTime = useRef(Date.now())

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.warning('Please enter a topic first.')
      return
    }
    setLoading(true)
    setError('')
    setPath(null)
    setActiveStep(0)
    setCompletedSteps(new Set())
    setShowAnswer({})

    try {
      const { data } = await generateLearningPath(topic)
      setPath(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate learning path.')
    } finally {
      setLoading(false)
    }
  }

  const markComplete = (stepIndex) => {
    const timeSpent = (Date.now() - stepStartTime.current) / 1000
    setCompletedSteps((prev) => new Set([...prev, stepIndex]))
    if (stepIndex < (path?.steps?.length || 0) - 1) {
      setActiveStep(stepIndex + 1)
    }
    // Save progress to backend
    saveLearningProgress({
      user_id: user.id,
      module: 'tutor',
      topic: `${path.topic} - Step ${stepIndex + 1}`,
      status: 'completed',
      progress_percent: ((stepIndex + 1) / path.steps.length) * 100,
      notes: path.steps[stepIndex]?.title || '',
      time_spent_seconds: timeSpent,
    }).catch(() => {})
    stepStartTime.current = Date.now()
    toast.success(`Step ${stepIndex + 1} completed!`)
  }

  const toggleAnswer = (stepIndex) => {
    setShowAnswer((prev) => ({ ...prev, [stepIndex]: !prev[stepIndex] }))
  }

  return (
    <div>
      <PageHeader
        title="AI Tutor"
        subtitle="Guided learning paths tailored for you"
        icon={GraduationCap}
      />

      {/* Input */}
      <Card className="mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="What do you want to learn? (e.g., Neural Networks, Calculus)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
            />
          </div>
          <Button onClick={handleGenerate} loading={loading} className="sm:self-end">
            <GraduationCap size={16} />
            Generate Path
          </Button>
        </div>
      </Card>

      {loading && (
        <Card>
          <LoadingSpinner text="Building your personalized learning path..." />
        </Card>
      )}

      {error && (
        <Card className="border-red-900/50">
          <p className="text-red-400 text-sm">{error}</p>
        </Card>
      )}

      {/* Learning Path */}
      {path && path.steps && (
        <div className="animate-fade-in">
          {/* Progress Header */}
          <Card className="mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">{path.topic}</h2>
                <p className="text-sm text-gray-400 mt-1">
                  {path.total_steps} steps · ~{path.estimated_time_minutes} min
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold">
                  {completedSteps.size}/{path.steps.length}
                </p>
                <p className="text-xs text-gray-400">Completed</p>
              </div>
            </div>
            {/* Progress Bar */}
            <div className="mt-4 h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-white rounded-full transition-all duration-500"
                style={{ width: `${(completedSteps.size / path.steps.length) * 100}%` }}
              />
            </div>
          </Card>

          {/* Step Cards */}
          <div className="space-y-4">
            {path.steps.map((step, i) => {
              const isActive = activeStep === i
              const isCompleted = completedSteps.has(i)

              return (
                <Card
                  key={i}
                  hover={false}
                  className={`transition-all duration-300 cursor-pointer ${
                    isActive
                      ? 'border-white/30 bg-gray-800/50'
                      : isCompleted
                      ? 'border-gray-700 opacity-70'
                      : 'border-gray-800'
                  }`}
                  onClick={() => setActiveStep(i)}
                >
                  {/* Step Header */}
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border ${
                        isCompleted
                          ? 'bg-white text-black border-white'
                          : isActive
                          ? 'bg-gray-700 text-white border-white/50'
                          : 'bg-gray-800 text-gray-400 border-gray-700'
                      }`}
                    >
                      {isCompleted ? <CheckCircle2 size={16} /> : step.step_number}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-base">{step.title}</h3>
                    </div>
                    <ChevronRight
                      size={16}
                      className={`text-gray-500 transition-transform ${isActive ? 'rotate-90' : ''}`}
                    />
                  </div>

                  {/* Expanded Content */}
                  {isActive && (
                    <div className="space-y-5 animate-fade-in pl-11">
                      {/* Concept */}
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <BookOpen size={14} className="text-gray-400" />
                          <span className="text-xs uppercase tracking-wider text-gray-400 font-medium">
                            Concept
                          </span>
                        </div>
                        <p className="text-sm text-gray-200 leading-relaxed">
                          {step.concept_explanation}
                        </p>
                      </div>

                      {/* Examples */}
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <Lightbulb size={14} className="text-gray-400" />
                          <span className="text-xs uppercase tracking-wider text-gray-400 font-medium">
                            Examples
                          </span>
                        </div>
                        <ul className="space-y-2">
                          {step.examples.map((ex, j) => (
                            <li
                              key={j}
                              className="text-sm text-gray-300 pl-4 border-l border-gray-700"
                            >
                              {ex}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Mini Test */}
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <ClipboardCheck size={14} className="text-gray-400" />
                          <span className="text-xs uppercase tracking-wider text-gray-400 font-medium">
                            Quick Check
                          </span>
                        </div>
                        <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                          <p className="text-sm text-gray-200 mb-2">{step.mini_test.question}</p>
                          {showAnswer[i] ? (
                            <p className="text-sm text-white font-medium animate-fade-in">
                              → {step.mini_test.answer}
                            </p>
                          ) : (
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                toggleAnswer(i)
                              }}
                              className="text-xs text-gray-400 hover:text-white transition-colors underline"
                            >
                              Show Answer
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Complete Button */}
                      {!isCompleted && (
                        <Button
                          variant="secondary"
                          onClick={(e) => {
                            e.stopPropagation()
                            markComplete(i)
                          }}
                          className="text-sm"
                        >
                          <CheckCircle2 size={14} />
                          Mark as Complete
                        </Button>
                      )}
                    </div>
                  )}
                </Card>
              )
            })}
          </div>

          {/* Completion Message */}
          {completedSteps.size === path.steps.length && (
            <Card className="mt-6 text-center animate-fade-in">
              <p className="text-2xl mb-2">🎉</p>
              <p className="text-lg font-semibold">Learning Path Complete!</p>
              <p className="text-sm text-gray-400 mt-1">
                You've mastered all steps of {path.topic}
              </p>
              <Button onClick={handleGenerate} className="mt-4 mx-auto">
                Learn Something New
              </Button>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
