import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { Badge, Spinner } from '../../components/ui'
import { parseApiError } from '../../utils'
import aiPrepService from '../../services/aiPrepService'

export default function CandidateAiQuestions() {
  const location = useLocation()
  const navState = location.state || {}

  // Context form state
  const [interviewId, setInterviewId] = useState(navState.interview_id || '')
  const [jobRole, setJobRole] = useState(navState.job_role || 'Full Stack Engineer')
  const [techStackInput, setTechStackInput] = useState(
    Array.isArray(navState.tech_stack) ? navState.tech_stack.join(', ') : (navState.tech_stack || 'React, Node.js, PostgreSQL')
  )
  const [difficulty, setDifficulty] = useState(navState.difficulty || 'medium')
  const [category, setCategory] = useState('technical')
  const [count, setCount] = useState(5)

  // Questions state
  const [questions, setQuestions] = useState([])
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)

  // Evaluation state map: { [questionIndex]: { answer: string, evaluating: boolean, result: object, error: string } }
  const [evalStates, setEvalStates] = useState({})
  // Open hints/criteria map: { [questionIndex]: { showHint: bool, showCriteria: bool, showAnswerBox: bool } }
  const [cardToggles, setCardToggles] = useState({})

  // Auto-generate on first load if coming with context
  useEffect(() => {
    if (navState.job_role) {
      handleGenerate()
    }
  }, [])

  const handleGenerate = async () => {
    setGenerating(true)
    setError(null)
    try {
      const techArray = techStackInput
        .split(',')
        .map(s => s.trim())
        .filter(Boolean)

      const payload = {
        interview_id: interviewId || null,
        job_role: jobRole,
        tech_stack: techArray,
        difficulty,
        category,
        count: Number(count),
      }

      const res = await aiPrepService.generateQuestions(payload)
      setQuestions(res.questions || [])
      setEvalStates({})
      // Default first card to show answer box
      setCardToggles({ 0: { showAnswerBox: true } })
    } catch (err) {
      setError(parseApiError(err))
    } finally {
      setGenerating(false)
    }
  }

  const toggleField = (idx, field) => {
    setCardToggles(prev => ({
      ...prev,
      [idx]: {
        ...prev[idx],
        [field]: !prev[idx]?.[field],
      },
    }))
  }

  const handleAnswerChange = (idx, text) => {
    setEvalStates(prev => ({
      ...prev,
      [idx]: {
        ...prev[idx],
        answer: text,
      },
    }))
  }

  const handleEvaluateAnswer = async (idx, questionItem) => {
    const currentAnswer = evalStates[idx]?.answer?.trim()
    if (!currentAnswer || currentAnswer.length < 10) {
      setEvalStates(prev => ({
        ...prev,
        [idx]: { ...prev[idx], error: 'Please write at least a sentence or two to evaluate.' },
      }))
      return
    }

    setEvalStates(prev => ({
      ...prev,
      [idx]: { ...prev[idx], evaluating: true, error: null },
    }))

    try {
      const payload = {
        question: questionItem.question,
        answer: currentAnswer,
        job_role: jobRole,
        difficulty,
      }
      const evalRes = await aiPrepService.evaluateAnswer(payload)
      setEvalStates(prev => ({
        ...prev,
        [idx]: { ...prev[idx], evaluating: false, result: evalRes },
      }))
    } catch (err) {
      setEvalStates(prev => ({
        ...prev,
        [idx]: { ...prev[idx], evaluating: false, error: parseApiError(err) },
      }))
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto animate-fade-in pb-16">
        {/* Breadcrumb & Navigation */}
        <div className="mb-6 flex items-center justify-between">
          <Link
            to="/candidate/ai-prep"
            className="text-sm font-semibold text-forest-700 hover:text-forest-900 flex items-center gap-1.5 transition"
          >
            <span>←</span> Back to AI Prep Hub
          </Link>

          <Link
            to="/candidate/ai-prep/mock"
            state={{ job_role: jobRole, tech_stack: techStackInput, difficulty }}
            className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-cream-100 hover:bg-cream-200 text-forest-900 border border-cream-300 transition flex items-center gap-1.5"
          >
            <span>🎙️</span> Switch to Live Mock Interview
          </Link>
        </div>

        {/* Header */}
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-forest-900">
            AI Practice Question Studio
          </h1>
          <p className="text-forest-600 font-sans text-sm mt-1">
            Generate challenging, realistic questions with hints and evaluation criteria.
            Test your answers and receive personalized AI scoring and actionable improvements.
          </p>
        </div>

        {/* Configuration Bar */}
        <div className="bg-white rounded-2xl border border-cream-300 shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1">
                Job Role
              </label>
              <input
                type="text"
                value={jobRole}
                onChange={e => setJobRole(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none"
                placeholder="e.g. Frontend Engineer"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1">
                Tech Stack
              </label>
              <input
                type="text"
                value={techStackInput}
                onChange={e => setTechStackInput(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none"
                placeholder="e.g. React, TypeScript, GraphQL"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none"
              >
                <option value="technical">Technical Depth</option>
                <option value="system_design">System Design & Architecture</option>
                <option value="behavioral">Behavioral (STAR Method)</option>
                <option value="role_specific">Role-Specific Scenarios</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1">
                Difficulty & Count
              </label>
              <div className="flex gap-2">
                <select
                  value={difficulty}
                  onChange={e => setDifficulty(e.target.value)}
                  className="w-1/2 px-2.5 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none capitalize"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>

                <select
                  value={count}
                  onChange={e => setCount(e.target.value)}
                  className="w-1/2 px-2.5 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none"
                >
                  <option value={3}>3 Qs</option>
                  <option value={5}>5 Qs</option>
                  <option value={8}>8 Qs</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-2 border-t border-cream-200">
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="px-5 py-2.5 bg-forest-900 hover:bg-forest-800 text-white rounded-xl text-sm font-semibold transition shadow-sm flex items-center gap-2 disabled:opacity-50"
            >
              {generating ? (
                <>
                  <Spinner size="sm" color="white" />
                  Generating Questions...
                </>
              ) : (
                <>
                  <span>⚡</span> Generate Practice Questions
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-sm text-rose-700 mb-8">
            {error}
          </div>
        )}

        {/* Questions List */}
        {questions.length > 0 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-lg font-bold text-forest-900">
                Generated Practice Questions ({questions.length})
              </h2>
              <span className="text-xs text-forest-500">
                Type your answer and click evaluate to receive AI feedback
              </span>
            </div>

            {questions.map((q, idx) => {
              const toggles = cardToggles[idx] || {}
              const evalState = evalStates[idx] || {}
              const answerText = evalState.answer || ''
              const wordCount = answerText.trim() ? answerText.trim().split(/\s+/).length : 0

              return (
                <div
                  key={idx}
                  className="bg-white rounded-2xl border border-cream-300 shadow-sm p-6 transition-all hover:border-forest-300"
                >
                  {/* Card Top */}
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="w-6 h-6 rounded-full bg-forest-900 text-white text-xs font-bold flex items-center justify-center">
                        {idx + 1}
                      </span>
                      <span className="text-xs uppercase font-bold px-2.5 py-0.5 rounded-full bg-forest-50 text-forest-800 border border-forest-100">
                        {q.category || category}
                      </span>
                      <span className="text-xs capitalize px-2 py-0.5 rounded-md bg-cream-100 text-forest-700 font-medium">
                        {q.difficulty || difficulty}
                      </span>
                      {q.is_fallback && (
                        <span className="text-[11px] bg-amber-50 text-amber-800 px-2 py-0.5 rounded">
                          Standard question
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {q.hint && (
                        <button
                          type="button"
                          onClick={() => toggleField(idx, 'showHint')}
                          className="text-xs font-medium text-forest-600 hover:text-forest-900 px-2 py-1 rounded hover:bg-cream-100 transition"
                        >
                          {toggles.showHint ? 'Hide Hint' : '💡 Show Hint'}
                        </button>
                      )}
                      {q.evaluation_criteria && (
                        <button
                          type="button"
                          onClick={() => toggleField(idx, 'showCriteria')}
                          className="text-xs font-medium text-forest-600 hover:text-forest-900 px-2 py-1 rounded hover:bg-cream-100 transition"
                        >
                          {toggles.showCriteria ? 'Hide Criteria' : '📋 Criteria'}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Question Text */}
                  <h3 className="font-display text-base font-semibold text-forest-900 mb-4 leading-snug">
                    {q.question}
                  </h3>

                  {/* Collapsible Hint */}
                  {toggles.showHint && q.hint && (
                    <div className="p-3 mb-4 bg-amber-50/70 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-start gap-2 animate-fade-in">
                      <span className="text-sm">💡</span>
                      <div>
                        <strong className="font-semibold">Hint:</strong> {q.hint}
                      </div>
                    </div>
                  )}

                  {/* Collapsible Criteria */}
                  {toggles.showCriteria && q.evaluation_criteria && (
                    <div className="p-3 mb-4 bg-blue-50/70 border border-blue-200 rounded-xl text-xs text-blue-900 flex items-start gap-2 animate-fade-in">
                      <span className="text-sm">📋</span>
                      <div>
                        <strong className="font-semibold">Interviewer Criteria:</strong> {q.evaluation_criteria}
                      </div>
                    </div>
                  )}

                  {/* Practice Answer Toggle & Area */}
                  <div className="mt-4 pt-4 border-t border-cream-200">
                    <div className="flex items-center justify-between mb-2">
                      <button
                        type="button"
                        onClick={() => toggleField(idx, 'showAnswerBox')}
                        className="text-xs font-semibold text-forest-800 hover:text-forest-900 flex items-center gap-1.5"
                      >
                        <span>{toggles.showAnswerBox !== false ? '▼' : '▶'}</span>
                        <span>Practice Your Response</span>
                      </button>

                      {toggles.showAnswerBox !== false && (
                        <span className="text-xs text-forest-500 font-mono">
                          {wordCount} words
                        </span>
                      )}
                    </div>

                    {toggles.showAnswerBox !== false && (
                      <div className="animate-fade-in space-y-3">
                        <textarea
                          rows={4}
                          value={answerText}
                          onChange={e => handleAnswerChange(idx, e.target.value)}
                          placeholder="Type your answer here... Be clear and structured (e.g. state context, architectural decision, and trade-offs)."
                          className="w-full p-3 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none font-sans leading-relaxed"
                        />

                        {evalState.error && (
                          <div className="text-xs text-rose-600 bg-rose-50 p-2 rounded-lg">
                            {evalState.error}
                          </div>
                        )}

                        <div className="flex justify-end">
                          <button
                            type="button"
                            onClick={() => handleEvaluateAnswer(idx, q)}
                            disabled={evalState.evaluating || !answerText.trim()}
                            className="px-4 py-2 bg-forest-900 hover:bg-forest-800 text-white rounded-xl text-xs font-semibold transition flex items-center gap-2 shadow-xs disabled:opacity-40"
                          >
                            {evalState.evaluating ? (
                              <>
                                <Spinner size="sm" color="white" />
                                Evaluating with AI...
                              </>
                            ) : (
                              <>
                                <span>🤖</span> Submit for AI Feedback
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* AI Evaluation Result Card */}
                  {evalState.result && (
                    <div className="mt-5 p-5 bg-gradient-to-br from-cream-50 to-white rounded-xl border border-forest-200 shadow-xs animate-fade-in">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-forest-900">AI Evaluation</span>
                          {evalState.result.is_fallback && (
                            <span className="text-[10px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded">
                              Offline evaluation
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-1.5">
                          <span className="text-xs text-forest-600 font-medium">Score:</span>
                          <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                            evalState.result.score >= 80 ? 'bg-emerald-100 text-emerald-800' :
                            evalState.result.score >= 60 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                          }`}>
                            {evalState.result.score} / 100
                          </span>
                        </div>
                      </div>

                      <p className="text-xs text-forest-800 mb-4 leading-relaxed font-sans">
                        {evalState.result.summary}
                      </p>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                        {/* Strengths */}
                        <div className="bg-emerald-50/60 border border-emerald-100 p-3 rounded-lg">
                          <h4 className="text-xs font-bold text-emerald-900 uppercase tracking-wider mb-2 flex items-center gap-1">
                            <span>✓</span> Key Strengths
                          </h4>
                          <ul className="space-y-1 text-xs text-emerald-800 list-disc list-inside">
                            {evalState.result.strengths?.map((s, i) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </div>

                        {/* Improvements */}
                        <div className="bg-rose-50/60 border border-rose-100 p-3 rounded-lg">
                          <h4 className="text-xs font-bold text-rose-900 uppercase tracking-wider mb-2 flex items-center gap-1">
                            <span>▲</span> Areas for Improvement
                          </h4>
                          <ul className="space-y-1 text-xs text-rose-800 list-disc list-inside">
                            {evalState.result.improvements?.map((imp, i) => (
                              <li key={i}>{imp}</li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {evalState.result.model_answer_snippet && (
                        <div className="bg-white border border-cream-300 p-3 rounded-lg text-xs">
                          <strong className="text-forest-900 font-semibold block mb-1">
                            Interviewer Key Takeaways & Model Direction:
                          </strong>
                          <p className="text-forest-600 italic">
                            "{evalState.result.model_answer_snippet}"
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
