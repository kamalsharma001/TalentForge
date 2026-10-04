import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { Badge, PageSpinner, EmptyState } from '../../components/ui'
import { fmtDate, fmtRelative, parseApiError } from '../../utils'
import aiPrepService from '../../services/aiPrepService'

export default function CandidateAiPrepHub() {
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [context, setContext] = useState({ interviews: [], candidate_skills: [] })
  const [selectedInterviewId, setSelectedInterviewId] = useState('')
  const [customRole, setCustomRole] = useState('Full Stack Developer')
  const [customTechStack, setCustomTechStack] = useState('React, Python, PostgreSQL')
  const [difficulty, setDifficulty] = useState('medium')

  // Strategy plan state
  const [plan, setPlan] = useState(null)
  const [planLoading, setPlanLoading] = useState(false)
  const [planError, setPlanError] = useState(null)

  // Past mock sessions
  const [recentSessions, setRecentSessions] = useState([])
  const [sessionsLoading, setSessionsLoading] = useState(false)

  // Load context on mount
  useEffect(() => {
    async function loadInitialData() {
      setLoading(true)
      try {
        const ctx = await aiPrepService.getContext()
        setContext(ctx)
        if (ctx.interviews && ctx.interviews.length > 0) {
          setSelectedInterviewId(ctx.interviews[0].id)
        }
      } catch (err) {
        console.error('Failed to load candidate prep context:', err)
      } finally {
        setLoading(false)
      }
    }
    loadInitialData()
  }, [])

  // Load past sessions
  const fetchRecentSessions = useCallback(async () => {
    setSessionsLoading(true)
    try {
      const list = await aiPrepService.listMockSessions(10)
      setRecentSessions(list)
    } catch (err) {
      console.error('Failed to fetch mock sessions:', err)
    } finally {
      setSessionsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchRecentSessions()
  }, [fetchRecentSessions])

  // Determine active target info
  const selectedInterview = context.interviews?.find(i => i.id === selectedInterviewId)
  const activeRole = selectedInterview?.job_role || selectedInterview?.title || customRole
  const activeTech = selectedInterview?.tech_stack?.length > 0
    ? selectedInterview.tech_stack
    : customTechStack.split(',').map(s => s.trim()).filter(Boolean)
  const activeDifficulty = selectedInterview?.difficulty || difficulty

  const handleGeneratePlan = async () => {
    setPlanLoading(true)
    setPlanError(null)
    try {
      const payload = {
        interview_id: selectedInterviewId || null,
        job_role: activeRole,
        tech_stack: activeTech,
        difficulty: activeDifficulty,
      }
      const data = await aiPrepService.generatePlan(payload)
      setPlan(data)
    } catch (err) {
      setPlanError(parseApiError(err))
    } finally {
      setPlanLoading(false)
    }
  }

  const navigateToQuestions = () => {
    navigate('/candidate/ai-prep/questions', {
      state: {
        interview_id: selectedInterviewId || null,
        job_role: activeRole,
        tech_stack: activeTech,
        difficulty: activeDifficulty,
      },
    })
  }

  const navigateToMockSetup = () => {
    navigate('/candidate/ai-prep/mock', {
      state: {
        interview_id: selectedInterviewId || null,
        job_role: activeRole,
        tech_stack: activeTech,
        difficulty: activeDifficulty,
      },
    })
  }

  if (loading) {
    return (
      <DashboardLayout>
        <PageSpinner />
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto animate-fade-in pb-12">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">🤖</span>
            <p className="section-label">AI Interview Preparation</p>
          </div>
          <h1 className="font-display text-3xl font-bold text-forest-900">
            Interview Prep & AI Mock Studio
          </h1>
          <p className="text-forest-600 font-sans text-sm mt-1 max-w-2xl">
            Prepare strategically for your scheduled interviews, practice realistic questions with instant AI answer evaluations,
            and complete live text-based mock interviews with dynamic follow-ups.
          </p>
        </div>

        {/* Target Context Selector */}
        <div className="bg-white rounded-2xl border border-cream-300 shadow-sm p-6 mb-8">
          <h2 className="font-display text-lg font-semibold text-forest-900 mb-4 flex items-center gap-2">
            <span>🎯</span> Target Interview Configuration
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="md:col-span-1">
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                Prepare for Interview
              </label>
              <select
                value={selectedInterviewId}
                onChange={e => {
                  setSelectedInterviewId(e.target.value)
                  setPlan(null)
                }}
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:outline-none focus:ring-2 focus:ring-forest-500 bg-cream-50/50"
              >
                {context.interviews && context.interviews.length > 0 && (
                  <optgroup label="Scheduled Interviews">
                    {context.interviews.map(inv => (
                      <option key={inv.id} value={inv.id}>
                        {inv.title} ({inv.job_role || 'General'})
                      </option>
                    ))}
                  </optgroup>
                )}
                <option value="">Custom Practice Role</option>
              </select>
            </div>

            {selectedInterview ? (
              <>
                <div className="md:col-span-1">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                    Job Role
                  </label>
                  <div className="px-3 py-2 text-sm bg-cream-100 rounded-xl font-medium text-forest-900">
                    {selectedInterview.job_role || selectedInterview.title}
                  </div>
                </div>
                <div className="md:col-span-1">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                    Target Tech Stack
                  </label>
                  <div className="flex flex-wrap gap-1.5 py-1">
                    {selectedInterview.tech_stack && selectedInterview.tech_stack.length > 0 ? (
                      selectedInterview.tech_stack.map(tech => (
                        <span key={tech} className="px-2 py-0.5 text-xs bg-forest-100 text-forest-800 rounded-md font-mono">
                          {tech}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-forest-500 italic">General Engineering</span>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="md:col-span-1">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                    Custom Job Role
                  </label>
                  <input
                    type="text"
                    value={customRole}
                    onChange={e => setCustomRole(e.target.value)}
                    placeholder="e.g. Backend Engineer"
                    className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:outline-none focus:ring-2 focus:ring-forest-500"
                  />
                </div>
                <div className="md:col-span-1">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                    Tech Stack (comma separated)
                  </label>
                  <input
                    type="text"
                    value={customTechStack}
                    onChange={e => setCustomTechStack(e.target.value)}
                    placeholder="e.g. Python, Docker, PostgreSQL"
                    className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:outline-none focus:ring-2 focus:ring-forest-500"
                  />
                </div>
              </>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-cream-200">
            <div className="flex items-center gap-2">
              <span className="text-xs text-forest-600 font-medium">Difficulty Level:</span>
              <div className="inline-flex rounded-lg border border-cream-300 p-0.5 bg-cream-100/60">
                {['easy', 'medium', 'hard'].map(lvl => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => {
                      setDifficulty(lvl)
                      setPlan(null)
                    }}
                    className={`px-2.5 py-1 text-xs font-medium rounded-md capitalize transition-colors ${
                      activeDifficulty === lvl
                        ? 'bg-forest-900 text-white shadow-sm'
                        : 'text-forest-700 hover:text-forest-900'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleGeneratePlan}
              disabled={planLoading}
              className="px-4 py-2 bg-forest-900 hover:bg-forest-800 text-white rounded-xl text-sm font-semibold transition shadow-sm flex items-center gap-2 disabled:opacity-50"
            >
              {planLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Analyzing Strategy...
                </>
              ) : (
                <>
                  <span>✨</span> Generate AI Prep Strategy
                </>
              )}
            </button>
          </div>
        </div>

        {/* AI Strategic Plan Section */}
        {plan && (
          <div className="bg-gradient-to-br from-forest-50/70 via-white to-cream-100/50 rounded-2xl border border-forest-200 p-6 mb-8 shadow-sm animate-fade-in">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-forest-700 bg-forest-100 px-2 py-0.5 rounded-full">
                  AI Preparation Blueprint
                </span>
                <h3 className="font-display text-xl font-bold text-forest-900 mt-1">
                  Strategic Plan for {activeRole}
                </h3>
              </div>
              {plan.is_fallback && (
                <span className="text-xs bg-amber-100 text-amber-800 px-2.5 py-1 rounded-md font-medium">
                  Offline Standard Plan
                </span>
              )}
            </div>

            <p className="text-forest-800 text-sm leading-relaxed mb-6 font-sans">
              {plan.summary}
            </p>

            {/* Focus Areas */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              {plan.focus_areas?.map((area, idx) => (
                <div key={idx} className="bg-white rounded-xl p-4 border border-cream-300 shadow-xs">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-sm text-forest-900">{area.name}</span>
                    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                      area.weight?.toLowerCase() === 'high'
                        ? 'bg-rose-100 text-rose-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {area.weight} Priority
                    </span>
                  </div>
                  <p className="text-xs text-forest-600 leading-relaxed font-sans">
                    {area.description}
                  </p>
                </div>
              ))}
            </div>

            {/* Recommended Topics & Question Types */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-cream-200">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-forest-700 mb-2">
                  Recommended Deep-Dive Topics
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {plan.recommended_topics?.map((topic, i) => (
                    <span key={i} className="px-2.5 py-1 text-xs bg-white text-forest-800 rounded-lg border border-cream-300 font-medium">
                      📌 {topic}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-forest-700 mb-2">
                  Suggested Question Formats
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {plan.suggested_question_types?.map((qType, i) => (
                    <span key={i} className="px-2.5 py-1 text-xs bg-white text-forest-800 rounded-lg border border-cream-300 font-medium">
                      🎯 {qType}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {planError && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-sm text-rose-700 mb-8">
            {planError}
          </div>
        )}

        {/* Practice Mode Cards */}
        <h2 className="font-display text-xl font-bold text-forest-900 mb-4">
          Choose Practice Mode
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          {/* Practice Questions */}
          <div className="bg-white rounded-2xl border border-cream-300 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
            <div>
              <div className="w-12 h-12 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center text-2xl mb-4">
                📝
              </div>
              <h3 className="font-display text-lg font-bold text-forest-900 mb-2">
                Curated Question Bank & Instant AI Evaluation
              </h3>
              <p className="text-forest-600 text-sm mb-4 leading-relaxed">
                Generate real interview questions tailored to <strong className="text-forest-900">{activeRole}</strong>.
                Draft written answers, reveal contextual hints, and receive instant rubric-based AI scoring with concrete strengths and areas for improvement.
              </p>
              <div className="flex flex-wrap gap-1.5 mb-6">
                <span className="text-xs bg-cream-100 text-forest-700 px-2 py-0.5 rounded-md">Individual practice</span>
                <span className="text-xs bg-cream-100 text-forest-700 px-2 py-0.5 rounded-md">Hints & Criteria</span>
                <span className="text-xs bg-cream-100 text-forest-700 px-2 py-0.5 rounded-md">Instant feedback</span>
              </div>
            </div>
            <button
              onClick={navigateToQuestions}
              className="w-full py-2.5 bg-forest-900 hover:bg-forest-800 text-white rounded-xl text-sm font-semibold transition flex items-center justify-center gap-2"
            >
              <span>Practice Questions</span>
              <span>→</span>
            </button>
          </div>

          {/* Conversational Mock Interview */}
          <div className="bg-white rounded-2xl border border-forest-300 ring-1 ring-forest-500/20 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between relative overflow-hidden">
            <div className="absolute top-4 right-4 bg-forest-100 text-forest-900 text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider">
              Live Interactive
            </div>
            <div>
              <div className="w-12 h-12 rounded-xl bg-forest-900 text-white flex items-center justify-center text-2xl mb-4 shadow-sm">
                🎙️
              </div>
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-display text-lg font-bold text-forest-900">
                  Conversational AI Mock Interview
                </h3>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded-full font-bold">
                  Resume-Aware
                </span>
              </div>
              <p className="text-forest-600 text-sm mb-4 leading-relaxed">
                Experience a realistic text-based interview with Alex, our AI Lead Interviewer.
                Alex dynamically probes into your answers and uploaded resume, explores trade-offs, and delivers a multi-dimensional performance report.
              </p>
              <div className="flex flex-wrap gap-1.5 mb-6">
                <span className="text-xs bg-forest-50 text-forest-800 px-2 py-0.5 rounded-md">Resume project grounding</span>
                <span className="text-xs bg-forest-50 text-forest-800 px-2 py-0.5 rounded-md">Dynamic follow-ups</span>
                <span className="text-xs bg-forest-50 text-forest-800 px-2 py-0.5 rounded-md">Claim validation report</span>
              </div>
            </div>
            <button
              onClick={navigateToMockSetup}
              className="w-full py-2.5 bg-forest-800 hover:bg-forest-900 text-white rounded-xl text-sm font-semibold transition flex items-center justify-center gap-2"
            >
              <span>Launch AI Mock Interview</span>
              <span>→</span>
            </button>
          </div>
        </div>

        {/* Recent Mock Interview Sessions */}
        <div className="bg-white rounded-2xl border border-cream-300 p-6 shadow-sm mb-12">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display text-lg font-bold text-forest-900">
              Recent Mock Interview Sessions
            </h3>
            <Link
              to="/candidate/ai-prep/mock"
              className="text-xs font-semibold text-forest-700 hover:text-forest-900"
            >
              New Session →
            </Link>
          </div>

          {sessionsLoading ? (
            <div className="py-8 flex justify-center">
              <div className="w-6 h-6 border-2 border-forest-900 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : recentSessions.length === 0 ? (
            <div className="py-8 text-center text-forest-500 text-sm">
              <p className="mb-2">No previous mock interview sessions yet.</p>
              <button
                onClick={navigateToMockSetup}
                className="text-xs font-semibold text-forest-900 underline"
              >
                Start your first AI mock interview now
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-cream-200 text-xs uppercase font-semibold text-forest-500">
                    <th className="pb-3">Role & Stack</th>
                    <th className="pb-3">Difficulty</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Score</th>
                    <th className="pb-3">Date</th>
                    <th className="pb-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cream-100">
                  {recentSessions.map(sess => (
                    <tr key={sess.id} className="hover:bg-cream-50/50 transition">
                      <td className="py-3">
                        <div className="font-semibold text-forest-900 flex items-center gap-1.5">
                          <span>{sess.job_role || 'General Interview'}</span>
                          {sess.has_resume && (
                            <span className="text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-200 px-1.5 py-0.2 rounded font-medium">
                              📄 Resume
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-forest-500 font-mono">
                          {sess.tech_stack?.join(', ') || 'Standard stack'}
                        </div>
                      </td>
                      <td className="py-3 capitalize text-xs text-forest-700">
                        {sess.difficulty || 'medium'}
                      </td>
                      <td className="py-3">
                        <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                          sess.status === 'completed'
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {sess.status === 'completed' ? 'Completed' : 'In Progress'}
                        </span>
                      </td>
                      <td className="py-3 font-semibold text-forest-900">
                        {sess.ai_score ? (
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            sess.ai_score >= 80 ? 'bg-emerald-100 text-emerald-800' :
                            sess.ai_score >= 60 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                          }`}>
                            {sess.ai_score}/100
                          </span>
                        ) : '—'}
                      </td>
                      <td className="py-3 text-xs text-forest-500">
                        {fmtRelative(sess.created_at)}
                      </td>
                      <td className="py-3 text-right">
                        {sess.status === 'completed' ? (
                          <Link
                            to={`/candidate/ai-prep/report/${sess.id}`}
                            className="text-xs font-semibold text-forest-900 hover:underline px-2.5 py-1 rounded bg-cream-100"
                          >
                            View Report →
                          </Link>
                        ) : (
                          <Link
                            to={`/candidate/ai-prep/mock/${sess.id}`}
                            className="text-xs font-semibold text-white px-2.5 py-1 rounded bg-forest-900 hover:bg-forest-800"
                          >
                            Resume →
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
