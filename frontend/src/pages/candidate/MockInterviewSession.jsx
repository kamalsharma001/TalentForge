import { useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useFetch } from '../../hooks'
import { PageSpinner, Badge } from '../../components/ui'
import { fmtRelative, parseApiError } from '../../utils'
import mockInterviewService from '../../services/mockInterviewService'

const CATEGORY_LABELS = {
  behavioral:    'Behavioral',
  technical:     'Technical',
  system_design: 'System Design',
}

export default function MockInterviewSession() {
  const { id } = useParams()
  const [answer, setAnswer] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)

  const fetchFn = useCallback(() => mockInterviewService.getById(id), [id])
  const { data: session, loading, refetch } = useFetch(fetchFn)

  const handleSubmit = async () => {
    if (!answer.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      await mockInterviewService.submit(id, answer)
      await refetch()
    } catch (err) {
      setError(parseApiError(err))
    } finally {
      setSubmitting(false)
    }
  }

  const handleGenerateFeedback = async () => {
    setGenerating(true)
    setError(null)
    try {
      await mockInterviewService.generateFeedback(id)
      await refetch()
    } catch (err) {
      setError(parseApiError(err))
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return <DashboardLayout><PageSpinner /></DashboardLayout>
  }

  if (!session) {
    return (
      <DashboardLayout>
        <div className="max-w-3xl mx-auto animate-fade-in">
          <div className="card text-center py-16">
            <p className="text-forest-500">Session not found.</p>
            <Link to="/candidate/mock-interviews" className="btn-primary mt-4 inline-block text-sm px-6 py-2">← Back</Link>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const isCompleted = session.status === 'completed'
  const hasAnswer = !!session.answer_text
  const hasFeedback = !!session.ai_summary

  let strengths = []
  let weaknesses = []
  try { strengths = JSON.parse(session.ai_strengths || '[]') } catch {}
  try { weaknesses = JSON.parse(session.ai_weaknesses || '[]') } catch {}

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        {/* Header */}
        <div className="mb-6">
          <Link to="/candidate/mock-interviews" className="text-forest-500 text-sm hover:text-forest-900 transition-colors">
            ← Back to Mock Interviews
          </Link>
          <div className="flex items-center gap-3 mt-3">
            <p className="section-label mb-0">Mock Interview</p>
            <Badge variant={isCompleted ? 'green' : hasAnswer ? 'blue' : 'gray'}>
              {isCompleted ? 'Completed' : hasAnswer ? 'In Progress' : 'Pending'}
            </Badge>
          </div>
          <h1 className="font-display text-2xl text-forest-900 mt-1">
            {CATEGORY_LABELS[session.category] || session.category} — {session.difficulty}
          </h1>
          <p className="text-forest-400 text-xs mt-1">{fmtRelative(session.created_at)}</p>
        </div>

        {/* Question card */}
        <div className="card mb-5">
          <h2 className="font-display text-lg text-forest-900 mb-3">Question</h2>
          <div className="p-4 rounded-xl bg-cream-50 border border-cream-200">
            <p className="text-forest-800 text-sm leading-relaxed">{session.question_text}</p>
          </div>
        </div>

        {/* Answer section */}
        <div className="card mb-5">
          <h2 className="font-display text-lg text-forest-900 mb-3">Your Answer</h2>
          {hasAnswer ? (
            <div className="p-4 rounded-xl bg-forest-50 border border-forest-200">
              <p className="text-forest-800 text-sm leading-relaxed whitespace-pre-wrap">{session.answer_text}</p>
            </div>
          ) : (
            <>
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer here... Be thorough and structured in your response."
                rows={10}
                className="w-full p-4 rounded-xl border border-cream-200 bg-cream-50 text-forest-900 text-sm focus:outline-none focus:ring-2 focus:ring-forest-300 focus:border-forest-300 transition-all resize-none"
              />
              <div className="flex items-center justify-between mt-3">
                <p className="text-forest-400 text-xs">{answer.split(/\s+/).filter(Boolean).length} words</p>
                <button
                  onClick={handleSubmit}
                  disabled={submitting || !answer.trim()}
                  className="btn-primary text-sm px-6 py-2 disabled:opacity-50"
                >
                  {submitting ? 'Submitting…' : 'Submit Answer'}
                </button>
              </div>
            </>
          )}
        </div>

        {/* Generate feedback button */}
        {hasAnswer && !hasFeedback && (
          <div className="card mb-5 text-center">
            <p className="text-forest-600 text-sm mb-4">Your answer has been submitted. Generate AI feedback to see your evaluation.</p>
            <button
              onClick={handleGenerateFeedback}
              disabled={generating}
              className="btn-primary text-sm px-6 py-2 disabled:opacity-50"
            >
              {generating ? 'Generating Feedback…' : '🤖 Generate AI Feedback'}
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="card-yellow border-amber-200 mb-5 flex items-start gap-3">
            <span className="text-lg">⚠️</span>
            <p className="text-forest-700 text-sm">{error}</p>
          </div>
        )}

        {/* AI Feedback */}
        {hasFeedback && (
          <div className="space-y-5">
            {/* Score */}
            <div className="card">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-display text-lg text-forest-900">AI Score</h2>
                <span className={`text-2xl font-display font-bold ${
                  session.ai_score >= 8 ? 'text-green-600'
                    : session.ai_score >= 5 ? 'text-amber-500'
                    : 'text-red-500'
                }`}>
                  {session.ai_score}/10
                </span>
              </div>
              <div className="h-3 bg-cream-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    session.ai_score >= 8 ? 'bg-green-500'
                      : session.ai_score >= 5 ? 'bg-amber-400'
                      : 'bg-red-400'
                  }`}
                  style={{ width: `${(session.ai_score / 10) * 100}%` }}
                />
              </div>
            </div>

            {/* Summary */}
            <div className="card">
              <h2 className="font-display text-lg text-forest-900 mb-3">Summary</h2>
              <p className="text-forest-700 text-sm leading-relaxed">{session.ai_summary}</p>
            </div>

            {/* Strengths */}
            <div className="card">
              <h2 className="font-display text-lg text-forest-900 mb-3">✅ Strengths</h2>
              <ul className="space-y-2">
                {strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-forest-700">
                    <span className="text-green-500 font-bold mt-0.5">•</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Weaknesses */}
            <div className="card">
              <h2 className="font-display text-lg text-forest-900 mb-3">🔸 Areas for Improvement</h2>
              <ul className="space-y-2">
                {weaknesses.map((w, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-forest-700">
                    <span className="text-amber-500 font-bold mt-0.5">•</span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
