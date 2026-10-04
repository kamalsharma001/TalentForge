import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { Spinner, PageSpinner } from '../../components/ui'
import { parseApiError } from '../../utils'
import aiPrepService from '../../services/aiPrepService'

export default function CandidateAiMockRoom() {
  const { id } = useParams()
  const navigate = useNavigate()
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const [loading, setLoading] = useState(true)
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [error, setError] = useState(null)

  // Lifecycle state machine: 'ACTIVE' | 'SESSION_ENDED'
  const [sessionState, setSessionState] = useState('ACTIVE')
  const [endReason, setEndReason] = useState('time_limit_reached') // 'time_limit_reached' | 'candidate_ended' | 'natural'
  const [showTerminalModal, setShowTerminalModal] = useState(false)
  const [showCandidateConfirmModal, setShowCandidateConfirmModal] = useState(false)

  // Input & sending state
  const [inputText, setInputText] = useState('')
  const [sending, setSending] = useState(false)
  const [concluding, setConcluding] = useState(false)
  const [isSessionConcluded, setIsSessionConcluded] = useState(false)

  // Live Timer
  const [secondsElapsed, setSecondsElapsed] = useState(0)

  // Load session & initialize lifecycle state
  useEffect(() => {
    async function loadSession() {
      setLoading(true)
      try {
        const data = await aiPrepService.getMockSession(id)
        setSession(data)
        setMessages(data.messages || [])

        const isTimed = data.duration_mode !== 'open_ended' && (data.duration_mins || 30) > 0
        const totalDurationSecs = isTimed ? (data.duration_mins || 30) * 60 : 0
        const isServerTimeExpired = isTimed && data.time_remaining_secs !== null && data.time_remaining_secs <= 0
        const isCompleted = data.status === 'completed' || data.completion_reason === 'time_limit_reached' || isServerTimeExpired

        if (isCompleted) {
          // Terminal state immediately on load/refresh if backend reports completed or expired
          setSessionState('SESSION_ENDED')
          const determinedReason = data.completion_reason || (isServerTimeExpired ? 'time_limit_reached' : 'natural')
          setEndReason(determinedReason)
          setShowTerminalModal(true)
          if (isTimed) {
            setSecondsElapsed(totalDurationSecs)
          } else {
            setSecondsElapsed(data.actual_duration_secs || 0)
          }
        } else {
          setSessionState('ACTIVE')
          // Initialize timer from server elapsed or started_at
          if (data.time_elapsed_secs !== undefined && data.time_elapsed_secs !== null) {
            setSecondsElapsed(data.time_elapsed_secs)
          } else if (data.started_at || data.created_at) {
            const started = new Date(data.started_at || data.created_at).getTime()
            const now = Date.now()
            const diffSecs = Math.max(0, Math.floor((now - started) / 1000))
            setSecondsElapsed(diffSecs)
          }
        }
      } catch (err) {
        setError(parseApiError(err))
      } finally {
        setLoading(false)
      }
    }
    loadSession()
  }, [id])

  // Timer interval: active only while ACTIVE and not concluding
  useEffect(() => {
    if (sessionState === 'SESSION_ENDED' || concluding || !session) return

    const isTimed = session.duration_mode !== 'open_ended' && (session.duration_mins || 30) > 0
    const totalDurationSecs = isTimed ? (session.duration_mins || 30) * 60 : 0

    const timer = setInterval(() => {
      setSecondsElapsed(prev => {
        const next = prev + 1
        if (isTimed && next >= totalDurationSecs) {
          clearInterval(timer)
          handleTimeExpired()
          return totalDurationSecs
        }
        return next
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [session, sessionState, concluding])

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  // Format seconds to mm:ss
  const formatTimer = (totalSecs) => {
    const mins = Math.floor(totalSecs / 60)
    const secs = totalSecs % 60
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }

  // Handle timeout transition
  const handleTimeExpired = async () => {
    // 1. Immediately transition frontend into terminal SESSION_ENDED state
    setSessionState('SESSION_ENDED')
    setEndReason('time_limit_reached')
    setShowTerminalModal(true)
    setShowCandidateConfirmModal(false)

    // 2. Fetch authoritative state from backend
    try {
      const updated = await aiPrepService.getMockSession(id)
      setSession(updated)
      if (updated.messages) {
        setMessages(updated.messages)
      }
    } catch (err) {
      console.error('Error syncing expired session with server:', err)
    }
  }

  // Send candidate response
  const handleSendMessage = async (e) => {
    if (e) e.preventDefault()
    const text = inputText.trim()

    // Completely block sending if session has ended, sending, concluding, or text is empty
    if (sessionState === 'SESSION_ENDED' || !text || sending || concluding) return

    setSending(true)
    setError(null)

    // Optimistic UI
    const tempCandidateMsg = {
      id: 'temp-' + Date.now(),
      role: 'candidate',
      content: text,
      sequence: messages.length + 1,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempCandidateMsg])
    setInputText('')

    try {
      const res = await aiPrepService.sendMockMessage(id, text)
      // Replace temp message with confirmed messages
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== tempCandidateMsg.id)
        return [...filtered, res.candidate_message, res.ai_response]
      })

      if (res.is_concluding) {
        if (res.completion_reason === 'time_limit_reached') {
          setSessionState('SESSION_ENDED')
          setEndReason('time_limit_reached')
          setShowTerminalModal(true)
        } else {
          setIsSessionConcluded(true)
        }
      }
    } catch (err) {
      const errMsg = parseApiError(err)
      setError(errMsg)
      // Rollback optimistic message
      setMessages(prev => prev.filter(m => m.id !== tempCandidateMsg.id))
      setInputText(text)

      // Handle race condition: server rejected because allotted time expired or completed
      const lowerErr = errMsg.toLowerCase()
      if (
        lowerErr.includes('time limit was reached') ||
        lowerErr.includes('allotted time has expired') ||
        lowerErr.includes('already completed')
      ) {
        setSessionState('SESSION_ENDED')
        setEndReason('time_limit_reached')
        setShowTerminalModal(true)
        setShowCandidateConfirmModal(false)
      }
    } finally {
      setSending(false)
      if (sessionState !== 'SESSION_ENDED') {
        setTimeout(() => inputRef.current?.focus(), 100)
      }
    }
  }

  // Keyboard shortcut Ctrl+Enter / Cmd+Enter
  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      if (sessionState === 'SESSION_ENDED' || sending || concluding) return
      handleSendMessage()
    }
  }

  // Candidate confirms manual conclusion ("candidate_ended")
  const handleCandidateConclude = async () => {
    setShowCandidateConfirmModal(false)
    setConcluding(true)
    setError(null)
    try {
      await aiPrepService.endMockSession(id, 'candidate_ended')
      navigate(`/candidate/ai-prep/report/${id}`)
    } catch (err) {
      setError(parseApiError(err))
      setConcluding(false)
      setSessionState('SESSION_ENDED')
      setEndReason('candidate_ended')
      setShowTerminalModal(true)
    }
  }

  // Primary action on terminal modal: View Evaluation Report
  const handleViewReport = async () => {
    // If session is already completed with score, navigate directly
    if (session?.status === 'completed' && session?.ai_score !== null) {
      navigate(`/candidate/ai-prep/report/${id}`)
      return
    }

    setConcluding(true)
    setError(null)
    try {
      await aiPrepService.endMockSession(id, endReason || 'time_limit_reached')
      navigate(`/candidate/ai-prep/report/${id}`)
    } catch (err) {
      setError(parseApiError(err))
      setConcluding(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <PageSpinner />
      </DashboardLayout>
    )
  }

  const candidateTurns = messages.filter(m => m.role === 'candidate').length
  const isTimed = session?.duration_mode !== 'open_ended' && (session?.duration_mins || 30) > 0
  const totalDurationSecs = isTimed ? (session?.duration_mins || 30) * 60 : 0
  const remainingSecs = isTimed ? Math.max(0, totalDurationSecs - secondsElapsed) : null
  const isTimeExpiring = isTimed && remainingSecs <= 180 && remainingSecs > 0
  const isTimeUp = isTimed && (remainingSecs === 0 || sessionState === 'SESSION_ENDED')

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-8.5rem)] animate-fade-in relative">
        {/* Top Room Bar */}
        <div className="bg-white rounded-2xl border border-cream-300 shadow-sm px-6 py-4 mb-4 flex items-center justify-between flex-wrap gap-4 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-forest-900 text-white flex items-center justify-center font-bold text-sm shadow-xs">
              🤖
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-display text-base font-bold text-forest-900">
                  Alex
                </h2>
                <span className="text-[11px] bg-forest-100 text-forest-800 px-2 py-0.5 rounded font-medium">
                  Lead Technical Interviewer
                </span>
                {(session?.resume_snapshot || session?.resume_id) && (
                  <span className="text-[11px] bg-emerald-100 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded font-medium inline-flex items-center gap-1">
                    <span>📄</span> Resume-Aware
                  </span>
                )}
              </div>
              <div className="text-xs text-forest-500 font-sans">
                {session?.job_role || 'Software Engineer'} · <span className="capitalize">{session?.difficulty || 'Medium'}</span>
                {(session?.resume_snapshot || session?.resume_id) && (
                  <span className="text-emerald-700 ml-2 font-medium">• Tailored to your experience</span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Dynamic Timer Badge */}
            {isTimed ? (
              <div
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border font-mono text-xs ${
                  isTimeUp
                    ? 'bg-rose-50 border-rose-300 text-rose-700 font-bold'
                    : isTimeExpiring
                    ? 'bg-amber-50 border-amber-300 text-amber-800 font-semibold'
                    : 'bg-cream-100 border-cream-300 text-forest-700'
                }`}
              >
                <span>⏱️</span>
                <span>{isTimeUp ? 'Time limit reached' : `${formatTimer(remainingSecs)} left`}</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-cream-100 rounded-xl border border-cream-300 font-mono text-xs text-forest-700">
                <span>⏱️</span>
                <span>
                  {sessionState === 'SESSION_ENDED'
                    ? `${formatTimer(secondsElapsed)} (Ended)`
                    : `${formatTimer(secondsElapsed)} (Open-ended)`}
                </span>
              </div>
            )}

            {/* Turn Counter */}
            <div className="text-xs text-forest-600 font-medium hidden sm:block">
              Exchanges: <span className="font-bold text-forest-900">{candidateTurns}</span>
            </div>

            {/* Finish & Evaluate Button: visible ONLY while session is ACTIVE */}
            {sessionState === 'ACTIVE' ? (
              <button
                onClick={() => setShowCandidateConfirmModal(true)}
                disabled={concluding || sending}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${
                  isSessionConcluded
                    ? 'bg-forest-900 text-white hover:bg-forest-800 shadow-xs'
                    : 'bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200'
                }`}
              >
                {isSessionConcluded ? 'Finish & View Evaluation' : 'Finish & Evaluate'}
              </button>
            ) : (
              <span className="px-3 py-1.5 rounded-xl text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 inline-flex items-center gap-1">
                <span>🛑</span> Session Ended
              </span>
            )}
          </div>
        </div>

        {/* Soft Concluding Banner when Alex initiates wrap-up while session is still active */}
        {isSessionConcluded && sessionState === 'ACTIVE' && (
          <div className="p-3.5 mb-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center justify-between flex-wrap gap-3 flex-shrink-0 animate-fade-in">
            <div className="flex items-center gap-2">
              <span className="text-lg">🏁</span>
              <span className="text-xs font-semibold text-emerald-950">
                Alex has completed the questions. Click below to review your comprehensive performance report.
              </span>
            </div>
            <button
              onClick={() => setShowCandidateConfirmModal(true)}
              className="px-4 py-1.5 bg-forest-900 hover:bg-forest-800 text-white rounded-xl text-xs font-bold transition shadow-xs"
            >
              Generate Performance Report →
            </button>
          </div>
        )}

        {error && (
          <div className="p-3 mb-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex-shrink-0">
            {error}
          </div>
        )}

        {/* Chat Transcript Area */}
        <div className="flex-1 bg-cream-50/50 rounded-2xl border border-cream-300 p-6 overflow-y-auto space-y-6">
          {messages.map((msg, index) => {
            const isInterviewer = msg.role === 'interviewer'

            return (
              <div
                key={msg.id || index}
                className={`flex gap-3 ${isInterviewer ? 'justify-start' : 'justify-end'} animate-fade-in`}
              >
                {isInterviewer && (
                  <div className="w-8 h-8 rounded-full bg-forest-900 text-white flex-shrink-0 flex items-center justify-center text-xs font-bold shadow-xs mt-1">
                    TF
                  </div>
                )}

                <div
                  className={`max-w-2xl rounded-2xl p-4 text-sm leading-relaxed shadow-xs ${
                    isInterviewer
                      ? 'bg-white text-forest-950 border border-cream-300 font-sans'
                      : 'bg-forest-900 text-white font-sans'
                  }`}
                >
                  <div className="flex items-center justify-between gap-4 mb-1.5">
                    <span
                      className={`text-[11px] font-semibold uppercase tracking-wider ${
                        isInterviewer ? 'text-forest-600' : 'text-forest-200'
                      }`}
                    >
                      {isInterviewer ? 'Alex (Interviewer)' : 'You'}
                    </span>
                    <span
                      className={`text-[10px] ${
                        isInterviewer ? 'text-forest-400' : 'text-forest-300'
                      }`}
                    >
                      #{msg.sequence || index + 1}
                    </span>
                  </div>

                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>

                {!isInterviewer && (
                  <div className="w-8 h-8 rounded-full bg-forest-800 text-white flex-shrink-0 flex items-center justify-center text-xs font-bold shadow-xs mt-1">
                    ME
                  </div>
                )}
              </div>
            )
          })}

          {/* Typing indicator */}
          {sending && (
            <div className="flex gap-3 justify-start animate-fade-in">
              <div className="w-8 h-8 rounded-full bg-forest-900 text-white flex-shrink-0 flex items-center justify-center text-xs font-bold shadow-xs mt-1">
                TF
              </div>
              <div className="bg-white border border-cream-300 rounded-2xl p-4 shadow-xs flex items-center gap-3">
                <div className="flex gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-forest-700 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full bg-forest-700 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full bg-forest-700 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-xs text-forest-500 font-medium">
                  Alex is analyzing your answer and preparing a follow-up...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar (COMPLETELY DISABLED IN SESSION_ENDED STATE) */}
        <form onSubmit={handleSendMessage} className="mt-4 flex-shrink-0">
          <div
            className={`bg-white rounded-2xl border border-cream-300 shadow-sm p-3 transition-all ${
              sessionState === 'SESSION_ENDED'
                ? 'opacity-60 bg-cream-50 cursor-not-allowed'
                : 'focus-within:ring-2 focus-within:ring-forest-500'
            }`}
          >
            <textarea
              ref={inputRef}
              rows={3}
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={sessionState === 'SESSION_ENDED' || sending || concluding}
              placeholder={
                sessionState === 'SESSION_ENDED'
                  ? "Interview session has ended. Click 'View Evaluation Report' to view your performance results."
                  : "Respond naturally to Alex's question... (Tip: Press Ctrl+Enter or Cmd+Enter to send)"
              }
              className="w-full text-sm font-sans focus:outline-none resize-none placeholder-forest-400 text-forest-900 disabled:bg-transparent disabled:cursor-not-allowed"
            />

            <div className="flex items-center justify-between pt-2 border-t border-cream-200 mt-1">
              <div className="text-xs text-forest-400">
                {sessionState === 'SESSION_ENDED'
                  ? 'Session concluded'
                  : inputText.trim()
                  ? `${inputText.trim().split(/\s+/).length} words`
                  : 'Press Ctrl+Enter to send'}
              </div>

              <button
                type="submit"
                disabled={sessionState === 'SESSION_ENDED' || sending || !inputText.trim() || concluding}
                className="px-5 py-2 bg-forest-900 hover:bg-forest-800 text-white rounded-xl text-xs font-semibold transition flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed shadow-xs"
              >
                {sending ? (
                  <>
                    <Spinner size="sm" color="white" />
                    Sending...
                  </>
                ) : (
                  <>
                    <span>Send Answer</span>
                    <span>↵</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Candidate Confirmation Modal (ACTIVE state manual finish) */}
        {showCandidateConfirmModal && (
          <div className="fixed inset-0 bg-forest-950/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl border border-cream-300 p-6 max-w-md w-full shadow-xl animate-fade-in">
              <div className="w-12 h-12 rounded-full bg-forest-100 text-forest-900 flex items-center justify-center text-2xl mb-3">
                🏁
              </div>
              <h3 className="font-display text-lg font-bold text-forest-900 mb-2">
                Conclude Mock Interview?
              </h3>
              <p className="text-forest-600 text-sm mb-6 leading-relaxed">
                Alex will evaluate your complete transcript ({candidateTurns} responses), calculate your 4-dimension rubric scores, validate claims, and compile recommendations.
              </p>
              <div className="flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowCandidateConfirmModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-forest-700 hover:bg-cream-100 rounded-xl transition"
                >
                  Continue Interview
                </button>
                <button
                  type="button"
                  onClick={handleCandidateConclude}
                  className="px-4 py-2 text-xs font-semibold bg-forest-900 hover:bg-forest-800 text-white rounded-xl transition shadow-xs"
                >
                  Yes, Conclude Interview
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Authoritative Terminal Modal (SESSION_ENDED state: exactly TWO actions) */}
        {showTerminalModal && (
          <div className="fixed inset-0 bg-forest-950/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-3xl border border-cream-300 p-8 max-w-md w-full shadow-2xl animate-fade-in text-center">
              <div className="w-16 h-16 rounded-2xl bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center text-3xl mx-auto mb-4">
                {endReason === 'time_limit_reached' ? '⏱️' : '🏁'}
              </div>

              <h3 className="font-display text-2xl font-bold text-forest-950 mb-2">
                {endReason === 'time_limit_reached'
                  ? 'Session Ended'
                  : endReason === 'candidate_ended'
                  ? 'Interview Completed'
                  : 'Interview Concluded'}
              </h3>

              <p className="text-forest-600 text-sm mb-6 leading-relaxed">
                {endReason === 'time_limit_reached'
                  ? 'Your allotted interview time has ended.'
                  : endReason === 'candidate_ended'
                  ? 'You have concluded the interview.'
                  : 'Alex has concluded all planned questions for this session.'}
              </p>

              {/* Session Meta Summary */}
              <div className="bg-cream-50 border border-cream-200 rounded-2xl p-4 mb-6 text-left grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div className="text-forest-400 font-medium">Role & Level</div>
                  <div className="font-semibold text-forest-900 mt-0.5 truncate">
                    {session?.job_role || 'Software Engineer'} ({session?.difficulty || 'Mid'})
                  </div>
                </div>
                <div>
                  <div className="text-forest-400 font-medium">Responses</div>
                  <div className="font-semibold text-forest-900 mt-0.5">
                    {candidateTurns} exchanges
                  </div>
                </div>
                <div>
                  <div className="text-forest-400 font-medium">Allotted Time</div>
                  <div className="font-semibold text-forest-900 mt-0.5">
                    {session?.duration_mode === 'open_ended'
                      ? 'Open-ended'
                      : `${session?.duration_mins || 30} mins`}
                  </div>
                </div>
                <div>
                  <div className="text-forest-400 font-medium">Reason</div>
                  <div className="font-semibold text-forest-900 mt-0.5 capitalize">
                    {endReason === 'time_limit_reached'
                      ? 'Time limit reached'
                      : endReason === 'candidate_ended'
                      ? 'Candidate concluded'
                      : 'Completed naturally'}
                  </div>
                </div>
              </div>

              {/* ONLY TWO ACTIONS: View Evaluation Report & Go to Dashboard */}
              <div className="space-y-3">
                <button
                  type="button"
                  onClick={handleViewReport}
                  disabled={concluding}
                  className="w-full py-3 px-5 bg-forest-900 hover:bg-forest-800 text-white rounded-xl text-sm font-bold transition shadow-xs flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {concluding ? (
                    <>
                      <Spinner size="sm" color="white" />
                      <span>Generating Evaluation Report...</span>
                    </>
                  ) : (
                    <>
                      <span>View Evaluation Report</span>
                      <span>→</span>
                    </>
                  )}
                </button>

                <button
                  type="button"
                  onClick={() => navigate('/candidate/ai-prep')}
                  disabled={concluding}
                  className="w-full py-2.5 px-5 bg-cream-100 hover:bg-cream-200 text-forest-700 rounded-xl text-xs font-semibold transition"
                >
                  Go to Dashboard
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Fullscreen Evaluation Loading Overlay */}
        {concluding && (
          <div className="fixed inset-0 bg-white/95 backdrop-blur-sm flex flex-col items-center justify-center z-50 p-6">
            <div className="w-16 h-16 border-4 border-forest-900 border-t-transparent rounded-full animate-spin mb-6" />
            <h3 className="font-display text-xl font-bold text-forest-900 mb-2">
              Alex is Evaluating Your Interview
            </h3>
            <p className="text-forest-600 text-sm text-center max-w-sm font-sans leading-relaxed">
              Analyzing full transcript, citing verbatim evidence quotes, verifying claims, and generating actionable practice recommendations...
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
