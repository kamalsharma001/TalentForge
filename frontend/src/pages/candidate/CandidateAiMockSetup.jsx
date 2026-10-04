import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { Spinner } from '../../components/ui'
import { parseApiError } from '../../utils'
import aiPrepService from '../../services/aiPrepService'

export default function CandidateAiMockSetup() {
  const navigate = useNavigate()
  const location = useLocation()
  const navState = location.state || {}

  const [loadingContext, setLoadingContext] = useState(true)
  const [interviews, setInterviews] = useState([])
  const [selectedInterviewId, setSelectedInterviewId] = useState(navState.interview_id || '')

  // Configuration
  const [jobRole, setJobRole] = useState(navState.job_role || 'Senior Software Engineer')
  const [techStackInput, setTechStackInput] = useState(
    Array.isArray(navState.tech_stack) ? navState.tech_stack.join(', ') : (navState.tech_stack || 'React, Python, PostgreSQL, AWS')
  )
  const [difficulty, setDifficulty] = useState(navState.difficulty || 'medium')
  const [category, setCategory] = useState('mixed')
  const [durationMode, setDurationMode] = useState('30')

  // Resume Grounding State
  const [resumes, setResumes] = useState([])
  const [selectedResumeId, setSelectedResumeId] = useState('')
  const [useResumeContext, setUseResumeContext] = useState(true)
  const [uploadingResume, setUploadingResume] = useState(false)
  const [resumeUploadError, setResumeUploadError] = useState(null)
  const [resumeSuccessMessage, setResumeSuccessMessage] = useState(null)

  const [launching, setLaunching] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadCtx() {
      try {
        const [ctx, resumeList] = await Promise.all([
          aiPrepService.getContext(),
          aiPrepService.listResumes().catch(() => []),
        ])

        setInterviews(ctx.interviews || [])
        setResumes(resumeList || [])

        if (resumeList && resumeList.length > 0) {
          const primary = resumeList.find(r => r.is_primary) || resumeList[0]
          setSelectedResumeId(primary.id)
        }

        if (!selectedInterviewId && ctx.interviews?.length > 0 && !navState.job_role) {
          const first = ctx.interviews[0]
          setSelectedInterviewId(first.id)
          setJobRole(first.job_role || first.title)
          if (first.tech_stack?.length > 0) {
            setTechStackInput(first.tech_stack.join(', '))
          }
          if (first.difficulty) {
            setDifficulty(first.difficulty)
          }
        }
      } catch (err) {
        console.error('Failed to load candidate context:', err)
      } finally {
        setLoadingContext(false)
      }
    }
    loadCtx()
  }, [])

  const handleInterviewSelect = (id) => {
    setSelectedInterviewId(id)
    if (!id) return
    const match = interviews.find(i => i.id === id)
    if (match) {
      setJobRole(match.job_role || match.title)
      if (match.tech_stack?.length > 0) {
        setTechStackInput(match.tech_stack.join(', '))
      }
      if (match.difficulty) {
        setDifficulty(match.difficulty)
      }
    }
  }

  const handleResumeFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadingResume(true)
    setResumeUploadError(null)
    setResumeSuccessMessage(null)
    try {
      const res = await aiPrepService.uploadResume(file)
      const newResume = res.resume
      setResumes(prev => [newResume, ...prev.filter(r => r.id !== newResume.id)])
      setSelectedResumeId(newResume.id)
      setUseResumeContext(true)
      const claimsCount = res.analysis?.technical_claims?.length || 0
      const skillsCount = Object.values(res.analysis?.skills || {}).flat().length || 0
      setResumeSuccessMessage(`Parsed "${newResume.file_name}"! ${claimsCount} claims and ${skillsCount} skills extracted with Gemini.`)

      // Optionally populate tech stack if default
      if (res.analysis?.skills) {
        const extractedLangs = Object.values(res.analysis.skills).flat()
        if (extractedLangs.length > 0 && techStackInput.includes('React, Python, PostgreSQL, AWS')) {
          setTechStackInput(extractedLangs.slice(0, 6).join(', '))
        }
      }
    } catch (err) {
      setResumeUploadError(parseApiError(err))
    } finally {
      setUploadingResume(false)
    }
  }

  const handleLaunch = async (e) => {
    e.preventDefault()
    setLaunching(true)
    setError(null)
    try {
      const techArray = techStackInput
        .split(',')
        .map(s => s.trim())
        .filter(Boolean)

      const payload = {
        interview_id: selectedInterviewId || null,
        resume_id: (useResumeContext && selectedResumeId) ? selectedResumeId : null,
        job_role: jobRole,
        tech_stack: techArray,
        difficulty,
        category,
        duration_mode: durationMode,
        duration_mins: durationMode === 'open_ended' ? 0 : Number(durationMode),
      }

      const session = await aiPrepService.startMockSession(payload)
      navigate(`/candidate/ai-prep/mock/${session.id}`)
    } catch (err) {
      setError(parseApiError(err))
      setLaunching(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto animate-fade-in pb-16">
        {/* Navigation */}
        <div className="mb-6">
          <Link
            to="/candidate/ai-prep"
            className="text-sm font-semibold text-forest-700 hover:text-forest-900 flex items-center gap-1.5 transition"
          >
            <span>←</span> Back to AI Prep Hub
          </Link>
        </div>

        {/* Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-forest-100 text-forest-800 rounded-full text-xs font-semibold uppercase tracking-wider mb-2">
            <span>🎙️</span> Live Text-Based Interview Room
          </div>
          <h1 className="font-display text-3xl font-bold text-forest-900">
            Setup AI Mock Interview
          </h1>
          <p className="text-forest-600 font-sans text-sm mt-1">
            Conduct a dynamic, multi-turn interview with Alex, our AI Technical Lead.
            Experience realistic technical trade-offs and probing follow-ups tailored to your responses.
          </p>
        </div>

        {/* Explanatory Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-4 rounded-xl border border-cream-300 shadow-xs">
            <span className="text-xl block mb-1">💬</span>
            <h4 className="font-semibold text-xs text-forest-900 uppercase tracking-wider mb-1">
              Conversational Multi-Turn
            </h4>
            <p className="text-xs text-forest-600 leading-relaxed font-sans">
              Not a static quiz. Alex starts with an opener and builds a natural dialogue around your answers.
            </p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-cream-300 shadow-xs">
            <span className="text-xl block mb-1">🧠</span>
            <h4 className="font-semibold text-xs text-forest-900 uppercase tracking-wider mb-1">
              Adaptive Probing Follow-Ups
            </h4>
            <p className="text-xs text-forest-600 leading-relaxed font-sans">
              Mentions of specific tools, architectural decisions, or gaps trigger deep contextual follow-up questions.
            </p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-cream-300 shadow-xs">
            <span className="text-xl block mb-1">📊</span>
            <h4 className="font-semibold text-xs text-forest-900 uppercase tracking-wider mb-1">
              Full Evaluation Rubric
            </h4>
            <p className="text-xs text-forest-600 leading-relaxed font-sans">
              End whenever you are ready to receive a multi-dimension scorecard, strengths, weaknesses, and practice tips.
            </p>
          </div>
        </div>

        {/* Configuration Form */}
        <form onSubmit={handleLaunch} className="bg-white rounded-2xl border border-cream-300 shadow-sm p-6 space-y-6">
          {/* Target Selection */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-2">
              Select Interview Target
            </label>
            <select
              value={selectedInterviewId}
              onChange={e => handleInterviewSelect(e.target.value)}
              className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none bg-cream-50/50 font-medium"
            >
              {interviews.length > 0 && (
                <optgroup label="Scheduled Platform Interviews">
                  {interviews.map(inv => (
                    <option key={inv.id} value={inv.id}>
                      {inv.title} — {inv.job_role || 'General Role'} ({inv.difficulty || 'Medium'})
                    </option>
                  ))}
                </optgroup>
              )}
              <option value="">Custom Role Practice (Configure below)</option>
            </select>
          </div>

          {/* Resume Grounding & Selection */}
          <div className="p-4 sm:p-5 rounded-2xl border border-cream-300 bg-cream-50/50 space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-forest-900 text-white flex items-center justify-center text-sm font-bold shadow-2xs">
                  📄
                </div>
                <div>
                  <h3 className="text-sm font-bold text-forest-900">
                    Resume-Aware Personalization
                  </h3>
                  <p className="text-xs text-forest-600">
                    Alex will anchor openers in your real projects and validate claimed technical depth.
                  </p>
                </div>
              </div>

              {resumes.length > 0 && (
                <label className="inline-flex items-center gap-2 cursor-pointer text-xs font-semibold text-forest-800 bg-white px-3 py-1 rounded-xl border border-cream-200">
                  <input
                    type="checkbox"
                    checked={useResumeContext}
                    onChange={e => setUseResumeContext(e.target.checked)}
                    className="rounded border-cream-400 text-forest-900 focus:ring-forest-500 w-4 h-4"
                  />
                  <span>Ground with Resume</span>
                </label>
              )}
            </div>

            {useResumeContext && (
              <div className="space-y-3 pt-3 border-t border-cream-200">
                {resumes.length > 0 ? (
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                      Selected Candidate Resume
                    </label>
                    <select
                      value={selectedResumeId}
                      onChange={e => setSelectedResumeId(e.target.value)}
                      className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 bg-white"
                    >
                      {resumes.map(r => (
                        <option key={r.id} value={r.id}>
                          {r.file_name} {r.is_primary ? '(Primary)' : ''}
                        </option>
                      ))}
                    </select>

                    {/* Resume Snapshot details badge */}
                    {(() => {
                      const cur = resumes.find(r => r.id === selectedResumeId)
                      if (!cur || !cur.parsed_data) return null
                      const skills = cur.parsed_data.skills || {}
                      const allSkills = Object.values(skills).flat()
                      const claimsCount = cur.parsed_data.technical_claims?.length || 0
                      return (
                        <div className="mt-2.5 p-3 rounded-xl bg-white border border-cream-200 text-xs text-forest-800">
                          <div className="flex items-center justify-between font-semibold mb-1">
                            <span className="flex items-center gap-1.5">
                              <span>🤖 Gemini Analysis Snapshot</span>
                            </span>
                            <span className="text-emerald-700 font-medium">✓ Ready for Interview</span>
                          </div>
                          {cur.parsed_data.summary && (
                            <p className="text-forest-600 line-clamp-2 mb-2 italic font-sans">
                              "{cur.parsed_data.summary}"
                            </p>
                          )}
                          <div className="flex flex-wrap gap-1.5 items-center">
                            <span className="text-forest-500 font-medium">Top Skills:</span>
                            {allSkills.slice(0, 8).map((sk, i) => (
                              <span key={i} className="px-2 py-0.5 rounded-md bg-forest-100 text-forest-800 font-mono text-[11px]">
                                {sk}
                              </span>
                            ))}
                            {claimsCount > 0 && (
                              <span className="px-2 py-0.5 rounded-md bg-amber-100 text-amber-900 font-medium text-[11px] ml-auto">
                                {claimsCount} claims to validate
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    })()}
                  </div>
                ) : (
                  <p className="text-xs text-forest-600 font-sans">
                    No resume uploaded yet. Upload a PDF or Word document (.docx) to practice with questions customized to your actual projects.
                  </p>
                )}

                {/* Upload or Replace button */}
                <div className="flex items-center gap-3 pt-1 flex-wrap">
                  <label className="cursor-pointer inline-flex items-center gap-2 px-3.5 py-1.5 bg-white border border-cream-300 hover:bg-cream-100 rounded-xl text-xs font-semibold text-forest-900 transition shadow-2xs">
                    {uploadingResume ? (
                      <>
                        <Spinner size="sm" color="forest" />
                        <span>Extracting & Analyzing with Gemini...</span>
                      </>
                    ) : (
                      <>
                        <span>📤</span>
                        <span>{resumes.length > 0 ? 'Upload Different Resume' : 'Upload Resume (.pdf, .docx)'}</span>
                      </>
                    )}
                    <input
                      type="file"
                      accept=".pdf,.docx,.doc,.txt"
                      disabled={uploadingResume}
                      onChange={handleResumeFileUpload}
                      className="hidden"
                    />
                  </label>

                  <span className="text-[11px] text-forest-500">
                    Supported: PDF, Word (.docx), up to 5MB. Resume is optional.
                  </span>
                </div>

                {resumeUploadError && (
                  <div className="p-2.5 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
                    {resumeUploadError}
                  </div>
                )}
                {resumeSuccessMessage && (
                  <div className="p-2.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl font-medium">
                    {resumeSuccessMessage}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Role & Tech Stack */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                Target Job Role
              </label>
              <input
                type="text"
                required
                value={jobRole}
                onChange={e => setJobRole(e.target.value)}
                placeholder="e.g. Backend Software Engineer"
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                Tech Stack (comma separated)
              </label>
              <input
                type="text"
                required
                value={techStackInput}
                onChange={e => setTechStackInput(e.target.value)}
                placeholder="e.g. Node.js, TypeScript, Docker, Redis"
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Difficulty & Category */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                Difficulty Level
              </label>
              <select
                value={difficulty}
                onChange={e => setDifficulty(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none capitalize"
              >
                <option value="easy">Easy (Entry / Junior)</option>
                <option value="medium">Medium (Mid-Level)</option>
                <option value="hard">Hard (Senior / Staff)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                Interview Focus
              </label>
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none"
              >
                <option value="mixed">Mixed (Technical + Behavioral)</option>
                <option value="technical">Technical Depth & Architecture</option>
                <option value="system_design">System Design & Scalability</option>
                <option value="behavioral">Behavioral (Leadership & STAR)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-forest-700 mb-1.5">
                Session Duration Mode
              </label>
              <select
                value={durationMode}
                onChange={e => setDurationMode(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl border border-cream-300 focus:ring-2 focus:ring-forest-500 focus:outline-none"
              >
                <option value="15">15 mins (Quick Sprint)</option>
                <option value="30">30 mins (Standard Technical · Recommended)</option>
                <option value="45">45 mins (Comprehensive Architecture)</option>
                <option value="60">60 mins (Full Loop Simulation)</option>
                <option value="open_ended">Open-ended (Self-Paced · No Cutoff)</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700">
              {error}
            </div>
          )}

          {/* Submit Action */}
          <div className="pt-4 border-t border-cream-200 flex items-center justify-between">
            <span className="text-xs text-forest-500">
              Interview room opens instantly in your browser (text-based chat).
            </span>

            <button
              type="submit"
              disabled={launching}
              className="px-6 py-2.5 bg-forest-900 hover:bg-forest-800 text-white rounded-xl text-sm font-semibold transition shadow-sm flex items-center gap-2 disabled:opacity-50"
            >
              {launching ? (
                <>
                  <Spinner size="sm" color="white" />
                  Connecting with Alex...
                </>
              ) : (
                <>
                  <span>🚀</span> Launch Mock Interview
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}
