import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { PageSpinner } from '../../components/ui'
import { parseApiError, fmtDateTime } from '../../utils'
import aiPrepService from '../../services/aiPrepService'

export default function CandidateAiReport() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [report, setReport] = useState(null)
  const [session, setSession] = useState(null)
  const [error, setError] = useState(null)
  const [showTranscript, setShowTranscript] = useState(false)

  useEffect(() => {
    async function loadData() {
      setLoading(true)
      try {
        const [rep, sess] = await Promise.all([
          aiPrepService.getMockReport(id),
          aiPrepService.getMockSession(id),
        ])
        setReport(rep)
        setSession(sess)
      } catch (err) {
        setError(parseApiError(err))
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [id])

  if (loading) {
    return (
      <DashboardLayout>
        <PageSpinner />
      </DashboardLayout>
    )
  }

  if (error || !report) {
    return (
      <DashboardLayout>
        <div className="max-w-3xl mx-auto py-12 text-center">
          <div className="text-4xl mb-3">⚠️</div>
          <h2 className="font-display text-xl font-bold text-forest-900 mb-2">
            Could Not Load Evaluation Report
          </h2>
          <p className="text-forest-600 text-sm mb-6">
            {error || 'Unable to find report data for this interview session.'}
          </p>
          <Link
            to="/candidate/ai-prep"
            className="px-4 py-2 bg-forest-900 text-white rounded-xl text-sm font-semibold inline-block"
          >
            Return to AI Prep Hub
          </Link>
        </div>
      </DashboardLayout>
    )
  }

  const score = report.overall_score || 0
  const rubric = report.rubric || {}

  const getVerdict = (s) => {
    if (s >= 85) return { label: 'Strong Hire Level', color: 'text-emerald-700', bg: 'bg-emerald-50 border-emerald-200' }
    if (s >= 70) return { label: 'Solid Competence', color: 'text-blue-700', bg: 'bg-blue-50 border-blue-200' }
    if (s >= 55) return { label: 'Developing Contender', color: 'text-amber-700', bg: 'bg-amber-50 border-amber-200' }
    return { label: 'Needs Targeted Practice', color: 'text-rose-700', bg: 'bg-rose-50 border-rose-200' }
  }

  const verdict = getVerdict(score)

  const rubricDimensions = [
    { key: 'technical_knowledge', label: 'Technical Knowledge', desc: 'Accuracy of concepts, architecture, and technology depth' },
    { key: 'problem_solving', label: 'Problem Solving', desc: 'Decomposition, handling constraints, and architectural trade-offs' },
    { key: 'communication', label: 'Communication & Structure', desc: 'Clarity, conciseness, and articulation of decisions' },
    { key: 'answer_quality', label: 'Answer Quality & Probing', desc: 'Directness and handling of interviewer follow-up questions' },
  ]

  const handlePracticeRecommendations = () => {
    const recommendedTopicStr = report.recommendations?.join(', ') || ''
    navigate('/candidate/ai-prep/questions', {
      state: {
        job_role: session?.job_role || 'Software Engineer',
        tech_stack: recommendedTopicStr,
        difficulty: session?.difficulty || 'medium',
      },
    })
  }

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto animate-fade-in pb-16">
        {/* Navigation */}
        <div className="mb-6 flex items-center justify-between">
          <Link
            to="/candidate/ai-prep"
            className="text-sm font-semibold text-forest-700 hover:text-forest-900 flex items-center gap-1.5 transition"
          >
            <span>←</span> Back to AI Prep Hub
          </Link>

          <div className="flex items-center gap-2">
            <Link
              to="/candidate/ai-prep/mock"
              className="px-3.5 py-1.5 rounded-xl border border-cream-300 text-xs font-semibold text-forest-800 hover:bg-cream-100 transition"
            >
              Retake Mock Interview
            </Link>
          </div>
        </div>

        {/* Header Title */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className="text-xs uppercase font-bold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-900">
              Session Performance Report
            </span>
            {(session?.resume_snapshot || session?.resume_id) && (
              <span className="text-xs bg-emerald-100 text-emerald-800 border border-emerald-200 px-2.5 py-0.5 rounded-full font-medium inline-flex items-center gap-1">
                <span>📄</span> Resume-Aware Evaluation
              </span>
            )}
            {(() => {
              const reason = session?.completion_reason || report.completion_reason || 'natural'
              if (reason === 'time_limit_reached') {
                return (
                  <span className="text-xs bg-amber-100 text-amber-900 border border-amber-300 px-2.5 py-0.5 rounded-full font-medium inline-flex items-center gap-1">
                    <span>⏱️</span> Concluded Due to Time Limit
                  </span>
                )
              }
              if (reason === 'candidate_ended') {
                return (
                  <span className="text-xs bg-blue-100 text-blue-900 border border-blue-300 px-2.5 py-0.5 rounded-full font-medium inline-flex items-center gap-1">
                    <span>⏹️</span> Concluded Early by Candidate
                  </span>
                )
              }
              return (
                <span className="text-xs bg-emerald-100 text-emerald-900 border border-emerald-300 px-2.5 py-0.5 rounded-full font-medium inline-flex items-center gap-1">
                  <span>✓</span> Completed Naturally
                </span>
              )
            })()}
            {report.is_fallback && (
              <span className="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-medium">
                Standard Baseline Evaluation
              </span>
            )}
          </div>
          <h1 className="font-display text-3xl font-bold text-forest-900">
            {session?.job_role || 'Engineering'} Mock Interview Evaluation
          </h1>
          <div className="flex items-center gap-3 text-forest-600 font-sans text-xs mt-1.5 flex-wrap">
            <span>Completed {session?.completed_at ? fmtDateTime(session.completed_at) : 'recently'}</span>
            <span>•</span>
            <span>Focus: <strong className="capitalize text-forest-800">{session?.category || 'Technical'}</strong></span>
            <span>•</span>
            <span>Difficulty: <strong className="capitalize text-forest-800">{session?.difficulty || 'Medium'}</strong></span>
            <span>•</span>
            <span>
              Duration Mode: <strong className="text-forest-800">{session?.duration_mode === 'open_ended' ? 'Open-ended' : `${session?.duration_mode || session?.duration_mins || 30} mins`}</strong>
            </span>
            {session?.actual_duration_secs != null && (
              <>
                <span>•</span>
                <span>
                  Actual Duration: <strong className="text-forest-800">{Math.floor(session.actual_duration_secs / 60)}m {session.actual_duration_secs % 60}s</strong>
                </span>
              </>
            )}
          </div>
        </div>

        {/* Overall Score & Verdict Banner */}
        <div className="bg-white rounded-3xl border border-cream-300 shadow-sm p-6 md:p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
            {/* Score Ring / Badge */}
            <div className="md:col-span-1 flex flex-col items-center justify-center p-4 bg-cream-50/60 rounded-2xl border border-cream-200">
              <div className="relative flex items-center justify-center">
                <div className="text-5xl font-display font-extrabold text-forest-900">
                  {score}
                </div>
                <span className="text-forest-400 text-sm font-bold ml-1">/100</span>
              </div>
              <div className={`mt-3 px-3 py-1 rounded-full text-xs font-bold border ${verdict.bg} ${verdict.color}`}>
                {verdict.label}
              </div>
            </div>

            {/* Summary & Takeaway */}
            <div className="md:col-span-3">
              <h2 className="font-display text-lg font-bold text-forest-900 mb-2">
                Executive Evaluation Summary
              </h2>
              <p className="text-forest-700 text-sm leading-relaxed font-sans mb-4">
                {report.summary}
              </p>
              {report.hands_on_vs_theoretical && (
                <div className="mb-4 p-3.5 bg-forest-50/70 border border-forest-100 rounded-xl text-xs text-forest-900 leading-relaxed font-sans">
                  <div className="flex items-center gap-1.5 font-bold text-forest-950 mb-1 text-[11px] uppercase tracking-wider">
                    <span>🔬</span> Hands-On Execution vs. Theoretical Understanding
                  </div>
                  <p>{report.hands_on_vs_theoretical}</p>
                </div>
              )}
              <div className="flex flex-wrap gap-2">
                {session?.tech_stack?.map((tech, i) => (
                  <span key={i} className="text-xs font-mono px-2.5 py-0.5 bg-forest-50 text-forest-800 rounded-md border border-forest-100">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 4-Dimension Rubric */}
        <div className="bg-white rounded-3xl border border-cream-300 shadow-sm p-6 md:p-8 mb-8">
          <h2 className="font-display text-lg font-bold text-forest-900 mb-6 flex items-center gap-2">
            <span>📊</span> Multi-Dimensional Performance Rubric
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {rubricDimensions.map(dim => {
              const dimScore = rubric[dim.key] ?? 70
              const barColor =
                dimScore >= 80 ? 'bg-emerald-600' :
                dimScore >= 60 ? 'bg-forest-800' : 'bg-rose-500'

              return (
                <div key={dim.key} className="p-4 rounded-2xl bg-cream-50/40 border border-cream-200">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-semibold text-sm text-forest-900">{dim.label}</span>
                    <span className="font-mono text-sm font-bold text-forest-900">{dimScore}/100</span>
                  </div>
                  <p className="text-xs text-forest-500 mb-3 font-sans leading-tight">
                    {dim.desc}
                  </p>
                  {/* Progress Bar */}
                  <div className="w-full h-2.5 bg-cream-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${barColor} rounded-full transition-all duration-700`}
                      style={{ width: `${dimScore}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Competency Coverage Breakdown */}
        {report.competency_coverage && (
          <div className="bg-white rounded-3xl border border-cream-300 shadow-sm p-6 md:p-8 mb-8">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-forest-500">
                  Role Competencies
                </span>
                <h3 className="font-display text-xl font-bold text-forest-900 mt-0.5">
                  Competency Coverage Breakdown
                </h3>
              </div>
              <span className="text-xs text-forest-500">
                Evaluation across critical engineering dimensions
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(report.competency_coverage).map(([key, comp]) => {
                if (!comp || typeof comp !== 'object') return null
                const name = comp.name || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
                const status = comp.status || 'Adequate'
                const statusStyle =
                  status === 'Strong'
                    ? 'bg-emerald-100 text-emerald-800 border-emerald-200'
                    : status === 'Adequate'
                    ? 'bg-blue-100 text-blue-800 border-blue-200'
                    : status === 'Needs Improvement'
                    ? 'bg-amber-100 text-amber-800 border-amber-200'
                    : 'bg-cream-100 text-forest-600 border-cream-300'

                return (
                  <div key={key} className="p-4 rounded-2xl bg-cream-50/60 border border-cream-200 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-forest-900">{name}</span>
                        <div className="flex items-center gap-2">
                          {comp.score != null && (
                            <span className="text-xs font-mono font-bold text-forest-700">{comp.score}%</span>
                          )}
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${statusStyle}`}>
                            {status}
                          </span>
                        </div>
                      </div>
                      {comp.what_candidate_demonstrated && (
                        <p className="text-xs text-forest-800 font-sans mb-2 font-medium">
                          {comp.what_candidate_demonstrated}
                        </p>
                      )}
                      {comp.evidence && (
                        <div className="p-2.5 rounded-xl bg-white border border-cream-200 text-xs text-forest-700 font-sans leading-relaxed mb-2 italic">
                          <span className="font-semibold text-forest-800 not-italic text-[11px] block mb-0.5">Evidence Observed:</span>
                          "{comp.evidence}"
                        </div>
                      )}
                    </div>
                    {(comp.what_remains_uncertain || comp.improvement_area) && (
                      <div className="pt-2 border-t border-cream-200/80 text-[11px] text-forest-600 font-sans space-y-1">
                        {comp.what_remains_uncertain && (
                          <p><span className="font-semibold text-forest-700">Uncertainty:</span> {comp.what_remains_uncertain}</p>
                        )}
                        {comp.improvement_area && (
                          <p><span className="font-semibold text-forest-700">Growth Focus:</span> {comp.improvement_area}</p>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Strengths & Weaknesses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Strengths */}
          <div className="bg-white rounded-3xl border border-emerald-100 shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-sm font-bold">
                ✓
              </div>
              <h3 className="font-display text-base font-bold text-forest-900">
                Key Strengths Demonstrated
              </h3>
            </div>
            <ul className="space-y-3">
              {report.strengths?.map((str, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-forest-800 font-sans leading-relaxed">
                  <span className="text-emerald-600 font-bold mt-0.5">•</span>
                  <span>{str}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Weaknesses / Growth Areas */}
          <div className="bg-white rounded-3xl border border-rose-100 shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-full bg-rose-100 text-rose-800 flex items-center justify-center text-sm font-bold">
                ▲
              </div>
              <h3 className="font-display text-base font-bold text-forest-900">
                Areas for Improvement & Blindspots
              </h3>
            </div>
            <ul className="space-y-3">
              {report.weaknesses?.map((w, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-forest-800 font-sans leading-relaxed">
                  <span className="text-rose-600 font-bold mt-0.5">•</span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Resume Claims Validation */}
        {report.validated_claims && report.validated_claims.length > 0 && (
          <div className="bg-white rounded-3xl border border-cream-300 shadow-sm p-6 md:p-8 mb-8">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-forest-900 text-white flex items-center justify-center text-sm font-bold shadow-2xs">
                  🔍
                </div>
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-forest-500">
                    Resume Intelligence
                  </span>
                  <h3 className="font-display text-xl font-bold text-forest-900 mt-0.5">
                    Resume Claims Validation
                  </h3>
                </div>
              </div>
              <span className="text-xs text-forest-500 italic">
                Objective analysis of technical assertions vs demonstrated depth
              </span>
            </div>

            <p className="text-xs text-forest-600 mb-5 font-sans leading-relaxed">
              Alex cross-references technical assertions from your resume against your answers during the interview. Claims are categorized neutrally to highlight where you excelled and what future interviewers will probe further.
            </p>

            <div className="space-y-3">
              {report.validated_claims.map((claimItem, idx) => {
                const status = claimItem.status || 'Requires further validation'
                const isDemonstrated = status === 'Demonstrated'
                const isPartial = status === 'Partially demonstrated'

                const badgeStyle = isDemonstrated
                  ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                  : isPartial
                  ? 'bg-amber-100 text-amber-800 border-amber-300'
                  : 'bg-slate-100 text-slate-700 border-slate-300'

                const cardStyle = isDemonstrated
                  ? 'bg-emerald-50/40 border-emerald-200/80'
                  : isPartial
                  ? 'bg-amber-50/30 border-amber-200/70'
                  : 'bg-slate-50/50 border-slate-200/80'

                const badgeLabel = isDemonstrated
                  ? '✓ Demonstrated'
                  : isPartial
                  ? '◐ Partially demonstrated'
                  : '⚠ Requires further validation'

                return (
                  <div key={idx} className={`p-4 rounded-2xl border transition-all ${cardStyle}`}>
                    <div className="flex items-start justify-between gap-3 flex-wrap sm:flex-nowrap mb-1.5">
                      <p className="text-xs font-semibold text-forest-950 font-sans">
                        "{claimItem.claim}"
                      </p>
                      <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border whitespace-nowrap flex-shrink-0 ${badgeStyle}`}>
                        {badgeLabel}
                      </span>
                    </div>
                    {claimItem.evidence && (
                      <p className="text-xs text-forest-700 font-sans leading-relaxed mt-1">
                        <span className="font-semibold text-forest-800">Transcript Evidence:</span> "{claimItem.evidence}"
                      </p>
                    )}
                    {claimItem.notes && (
                      <p className="text-xs text-forest-600 font-sans leading-relaxed mt-0.5">
                        <span className="font-medium text-forest-700">Observation:</span> {claimItem.notes}
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Personalized Recommendations & Action Plan */}
        <div className="bg-gradient-to-br from-forest-900 to-forest-950 text-white rounded-3xl p-6 md:p-8 mb-8 shadow-md">
          <div className="flex items-center justify-between flex-wrap gap-4 mb-4">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-forest-300">
                Actionable Next Steps
              </span>
              <h3 className="font-display text-xl font-bold text-white mt-1">
                Personalized Practice Recommendations
              </h3>
            </div>
            <button
              onClick={handlePracticeRecommendations}
              className="px-4 py-2 bg-white text-forest-900 hover:bg-cream-100 rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5"
            >
              <span>Practice in Questions Studio</span>
              <span>→</span>
            </button>
          </div>

          <p className="text-forest-200 text-xs mb-6 max-w-2xl font-sans">
            Based on the technical gaps and follow-up exchanges in your interview, Alex recommends focusing on the following core concepts before your next real interview:
          </p>

          {report.actionable_recommendations && report.actionable_recommendations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {report.actionable_recommendations.map((rec, idx) => (
                <div key={idx} className="bg-white/10 backdrop-blur-xs rounded-2xl p-4 border border-white/10 flex flex-col justify-between">
                  <div>
                    <span className="text-xs text-amber-300 font-bold block mb-1">
                      Focus Area #{idx + 1}
                    </span>
                    <h4 className="font-display text-sm font-bold text-white mb-2">
                      {rec.topic}
                    </h4>
                    {rec.why_it_matters && (
                      <p className="text-[11px] text-forest-200 font-sans leading-relaxed mb-2">
                        <strong className="text-white font-medium">Why it matters:</strong> {rec.why_it_matters}
                      </p>
                    )}
                    {rec.specific_weakness && (
                      <p className="text-[11px] text-rose-200/90 font-sans leading-relaxed mb-2">
                        <strong className="text-rose-100 font-medium">Observed Gap:</strong> {rec.specific_weakness}
                      </p>
                    )}
                    {rec.concrete_exercise && (
                      <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-[11px] text-forest-100 font-sans mb-3">
                        <strong className="text-amber-200 block mb-0.5">Practical Exercise:</strong>
                        {rec.concrete_exercise}
                      </div>
                    )}
                  </div>
                  {rec.practice_question && (
                    <button
                      onClick={() => navigate('/candidate/ai-prep/questions', {
                        state: {
                          job_role: session?.job_role || 'Software Engineer',
                          tech_stack: rec.topic,
                          difficulty: session?.difficulty || 'medium',
                        }
                      })}
                      className="mt-2 text-left p-2 rounded-xl bg-white/15 hover:bg-white/25 transition text-[11px] text-white font-sans flex items-center justify-between gap-2"
                    >
                      <span className="line-clamp-1 italic">"{rec.practice_question}"</span>
                      <span className="text-amber-300 flex-shrink-0 font-bold">→</span>
                    </button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {report.recommendations?.map((rec, idx) => (
                <div key={idx} className="bg-white/10 backdrop-blur-xs rounded-xl p-3.5 border border-white/10">
                  <span className="text-xs text-amber-300 font-bold block mb-1">
                    Focus Area #{idx + 1}
                  </span>
                  <p className="text-xs text-forest-100 font-sans leading-relaxed">
                    {rec}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Full Interview Transcript Accordion */}
        <div className="bg-white rounded-3xl border border-cream-300 shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-base font-bold text-forest-900">
                Complete Interview Transcript ({session?.messages?.length || 0} messages)
              </h3>
              <p className="text-xs text-forest-500 mt-0.5">
                Review each question asked and your corresponding responses
              </p>
            </div>
            <button
              onClick={() => setShowTranscript(!showTranscript)}
              className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-cream-100 text-forest-800 hover:bg-cream-200 transition"
            >
              {showTranscript ? 'Hide Transcript ▲' : 'View Full Transcript ▼'}
            </button>
          </div>

          {showTranscript && (
            <div className="mt-6 pt-6 border-t border-cream-200 space-y-4 animate-fade-in">
              {session?.messages?.map((msg, i) => {
                const isInterviewer = msg.role === 'interviewer'
                return (
                  <div
                    key={msg.id || i}
                    className={`p-4 rounded-xl text-xs leading-relaxed ${
                      isInterviewer
                        ? 'bg-cream-50 border border-cream-200 text-forest-900'
                        : 'bg-forest-50/50 border border-forest-100 text-forest-950 font-sans'
                    }`}
                  >
                    <div className="font-bold mb-1 flex items-center justify-between text-[11px]">
                      <span className={isInterviewer ? 'text-forest-700' : 'text-forest-900'}>
                        {isInterviewer ? '🤖 Alex (Lead Interviewer)' : '👤 Candidate (You)'}
                      </span>
                      <span className="text-forest-400 font-mono">Turn #{msg.sequence || i + 1}</span>
                    </div>
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
