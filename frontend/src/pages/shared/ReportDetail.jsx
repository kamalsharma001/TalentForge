import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { useFetch } from '../../hooks'
import reportService from '../../services/reportService'
import interviewService from '../../services/interviewService'
import { ScoreBar, DecisionBadge, PageSpinner, Modal } from '../../components/ui'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

export default function ReportDetail() {
  const { interviewId } = useParams()
  const navigate        = useNavigate()

  const { data: interview, loading: ivLoading } = useFetch(
    () => interviewService.getById(interviewId), [interviewId]
  )
  const { data: report, loading: rLoading, refetch } = useFetch(
    () => reportService.getByInterview(interviewId), [interviewId]
  )

  const { user } = useAuth()
  const role = user?.role

  const [genAI,      setGenAI]      = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [showEdit,   setShowEdit]   = useState(false)
  const [editForm,   setEditForm]   = useState({})
  const [saving,     setSaving]     = useState(false)

  const loading = ivLoading || rLoading

  const handleGenerateAI = async () => {
    setGenAI(true)
    try {
      await reportService.generateAI(interviewId)
      toast.success('AI feedback generated!')
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || 'AI generation failed — check OPENAI_API_KEY')
    } finally { setGenAI(false) }
  }

  const handlePublish = async () => {
    if (!report?.id) return
    setPublishing(true)
    try {
      await reportService.publish(report.id)
      toast.success('Report published to candidate!')
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Publish failed')
    } finally { setPublishing(false) }
  }

  const openEdit = () => {
    setEditForm({
      summary:        report?.summary        || '',
      strengths:      report?.strengths      || '',
      weaknesses:     report?.weaknesses     || '',
      recommendation: report?.recommendation || '',
      decision:       report?.decision       || '',
    })
    setShowEdit(true)
  }

  const handleSaveEdit = async () => {
    setSaving(true)
    try {
      await reportService.update(report.id, editForm)
      toast.success('Report updated!')
      setShowEdit(false)
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Update failed')
    } finally { setSaving(false) }
  }

  const canPublish  = ['admin','recruiter'].includes(role) && report && !report.is_published
  const canEdit     = ['admin','recruiter','interviewer'].includes(role) && report && !report.is_published
  const canGenAI    = ['admin','recruiter','interviewer'].includes(role)
  const isCandidate = role === 'candidate'

  if (loading) return <DashboardLayout><PageSpinner /></DashboardLayout>

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">

        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <button onClick={() => navigate(-1)} className="btn-ghost text-xs mb-2 -ml-2">← Back</button>
            <h1 className="font-display text-2xl text-forest-900">
              {interview?.title || 'Interview Report'}
            </h1>
            <p className="text-forest-500 text-sm mt-1">
              {interview?.job_role || 'Technical Interview'} ·{' '}
              {report?.published_at
                ? `Published ${format(new Date(report.published_at), 'MMM d, yyyy')}`
                : 'Draft'
              }
            </p>
          </div>

          <div className="flex items-center gap-2 ml-4 flex-shrink-0 flex-wrap justify-end">
            {canGenAI && (
              <button onClick={handleGenerateAI} disabled={genAI}
                className="btn-secondary text-xs py-2 px-4 flex items-center gap-1.5">
                {genAI
                  ? <><span className="w-3 h-3 border-2 border-forest-900 border-t-transparent rounded-full animate-spin" />Generating…</>
                  : '🤖 Generate AI'}
              </button>
            )}
            {canEdit && (
              <button onClick={openEdit} className="btn-secondary text-xs py-2 px-4">Edit</button>
            )}
            {canPublish && (
              <button onClick={handlePublish} disabled={publishing} className="btn-primary text-xs py-2 px-4">
                {publishing ? 'Publishing…' : '📢 Publish'}
              </button>
            )}
          </div>
        </div>

        {/* Not yet published notice for candidate */}
        {isCandidate && !report?.is_published && (
          <div className="card-yellow border-amber-200 mb-5 flex items-start gap-3">
            <span className="text-xl">⏳</span>
            <div>
              <p className="font-semibold text-forest-900 text-sm">Report not yet published</p>
              <p className="text-forest-600 text-sm">Your recruiter is reviewing the report. You'll be notified when it's ready.</p>
            </div>
          </div>
        )}

        {/* No report yet */}
        {!report && !loading && (
          <div className="card text-center py-16">
            <div className="text-5xl mb-4">📝</div>
            <p className="font-display text-xl text-forest-900 mb-2">No report yet</p>
            <p className="text-forest-500 text-sm mb-6">
              {role === 'interviewer'
                ? 'Submit the evaluation report for this interview.'
                : 'The interviewer hasn\'t submitted a report yet.'}
            </p>
            {role === 'interviewer' && (
              <Link to={`/interviewer/reports?interview=${interviewId}`} className="btn-primary">
                Submit Report →
              </Link>
            )}
          </div>
        )}

        {report && (
          <>
            {/* Decision + score */}
            <div className="grid sm:grid-cols-3 gap-4 mb-5">
              <div className="card col-span-1 flex flex-col items-center justify-center py-6">
                <p className="text-forest-400 text-xs font-semibold uppercase tracking-wide mb-2">Decision</p>
                {report.decision
                  ? <DecisionBadge decision={report.decision} />
                  : <span className="text-forest-400 text-sm">Pending</span>}
              </div>
              <div className="card col-span-1 flex flex-col items-center justify-center py-6">
                <p className="text-forest-400 text-xs font-semibold uppercase tracking-wide mb-2">Overall Score</p>
                <span className="font-display text-3xl font-bold text-forest-900">
                  {report.overall_score ? `${report.overall_score}/10` : '—'}
                </span>
              </div>
              <div className="card col-span-1 flex flex-col items-center justify-center py-6">
                <p className="text-forest-400 text-xs font-semibold uppercase tracking-wide mb-2">Status</p>
                <span className={`badge ${report.is_published ? 'badge-green' : 'badge-amber'}`}>
                  {report.is_published ? '✓ Published' : 'Draft'}
                </span>
              </div>
            </div>

            {/* Scores */}
            {interview?.scores?.length > 0 && (
              <div className="card mb-5">
                <h2 className="font-display text-lg text-forest-900 mb-4">Dimension Scores</h2>
                {interview.scores.map(s => (
                  <ScoreBar key={s.id} dimension={s.dimension} score={s.score} maxScore={s.max_score} />
                ))}
              </div>
            )}

            {/* AI Section */}
            {(report.ai_summary || report.ai_strengths || report.ai_weaknesses) && (
              <div className="rounded-2xl border-2 border-amber-300 bg-amber-50 p-5 mb-5">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">🤖</span>
                  <h2 className="font-display text-lg text-forest-900">AI-Generated Insights</h2>
                  {report.ai_generated_at && (
                    <span className="text-xs text-forest-400 ml-auto">
                      {format(new Date(report.ai_generated_at), 'MMM d, h:mma')}
                    </span>
                  )}
                </div>

                {report.ai_summary && (
                  <div className="mb-4">
                    <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1">Summary</p>
                    <p className="text-forest-700 text-sm leading-relaxed">{report.ai_summary}</p>
                  </div>
                )}

                <div className="grid sm:grid-cols-2 gap-4">
                  {report.ai_strengths && (
                    <div className="bg-white rounded-xl p-4 border border-green-200">
                      <p className="text-xs font-semibold text-green-700 uppercase tracking-wide mb-2">💪 Strengths</p>
                      <p className="text-forest-700 text-sm leading-relaxed whitespace-pre-line">{report.ai_strengths}</p>
                    </div>
                  )}
                  {report.ai_weaknesses && (
                    <div className="bg-white rounded-xl p-4 border border-red-200">
                      <p className="text-xs font-semibold text-red-600 uppercase tracking-wide mb-2">📈 Areas to Improve</p>
                      <p className="text-forest-700 text-sm leading-relaxed whitespace-pre-line">{report.ai_weaknesses}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Human written sections */}
            {[
              { key: 'summary',        label: 'Overall Summary',        icon: '📋' },
              { key: 'strengths',      label: 'Strengths',              icon: '💪' },
              { key: 'weaknesses',     label: 'Areas for Improvement',  icon: '📈' },
              { key: 'recommendation', label: 'Recommendation',         icon: '🎯' },
            ].map(sec => report[sec.key] ? (
              <div key={sec.key} className="card mb-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-lg">{sec.icon}</span>
                  <h2 className="font-display text-lg text-forest-900">{sec.label}</h2>
                </div>
                <p className="text-forest-700 text-sm leading-relaxed whitespace-pre-line">{report[sec.key]}</p>
              </div>
            ) : null)}

            {/* Private notes — hidden from candidate */}
            {!isCandidate && report.private_notes && (
              <div className="card mb-5 border-l-4 border-l-forest-900">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-lg">🔒</span>
                  <h2 className="font-display text-lg text-forest-900">Private Notes</h2>
                  <span className="badge-gray text-xs">Not visible to candidate</span>
                </div>
                <p className="text-forest-700 text-sm leading-relaxed">{report.private_notes}</p>
              </div>
            )}

            {/* Recording */}
            {interview?.recording_url && (
              <div className="card flex items-center gap-4">
                <div className="text-2xl">🎬</div>
                <div className="flex-1">
                  <p className="font-semibold text-forest-900 text-sm">Interview Recording</p>
                  {interview.recording_duration_s && (
                    <p className="text-forest-400 text-xs">
                      {Math.round(interview.recording_duration_s / 60)} min recording
                    </p>
                  )}
                </div>
                <a href={interview.recording_url} target="_blank" rel="noopener noreferrer"
                  className="btn-secondary text-sm py-2 px-4">
                  Watch →
                </a>
              </div>
            )}
          </>
        )}
      </div>

      {/* Edit modal */}
      <Modal open={showEdit} onClose={() => setShowEdit(false)} title="Edit Report" maxWidth="max-w-2xl">
        <div className="space-y-4 max-h-[65vh] overflow-y-auto pr-1">
          {[
            { k: 'summary',        label: 'Summary',               rows: 4 },
            { k: 'strengths',      label: 'Strengths',             rows: 3 },
            { k: 'weaknesses',     label: 'Areas for Improvement', rows: 3 },
            { k: 'recommendation', label: 'Recommendation',        rows: 3 },
          ].map(f => (
            <div key={f.k}>
              <label className="label">{f.label}</label>
              <textarea className="input resize-none" rows={f.rows}
                value={editForm[f.k] || ''}
                onChange={e => setEditForm(ef => ({ ...ef, [f.k]: e.target.value }))} />
            </div>
          ))}
          <div>
            <label className="label">Decision</label>
            <select className="input" value={editForm.decision || ''}
              onChange={e => setEditForm(ef => ({ ...ef, decision: e.target.value }))}>
              <option value="">— Select decision —</option>
              <option value="hire">✓ Hire</option>
              <option value="hold">⏸ Hold</option>
              <option value="no_hire">✕ No Hire</option>
            </select>
          </div>
        </div>
        <div className="flex gap-3 justify-end mt-5 pt-4 border-t border-cream-200">
          <button onClick={() => setShowEdit(false)} className="btn-secondary text-sm py-2 px-4">Cancel</button>
          <button onClick={handleSaveEdit} disabled={saving} className="btn-primary text-sm py-2 px-4">
            {saving ? 'Saving…' : 'Save Changes'}
          </button>
        </div>
      </Modal>
    </DashboardLayout>
  )
}
