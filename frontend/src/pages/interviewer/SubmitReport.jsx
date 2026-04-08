import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import reportService from '../../services/reportService'
import interviewService from '../../services/interviewService'
import { useFetch } from '../../hooks'
import { ScoreBar, PageSpinner, EmptyState } from '../../components/ui'
import toast from 'react-hot-toast'

const DIMENSIONS = ['Problem Solving','Communication','Code Quality','System Design','Technical Knowledge','Culture Fit']
const DECISIONS  = [
  { v: 'hire',    label: '✓ Hire',     color: 'bg-green-600' },
  { v: 'hold',    label: '⏸ Hold',     color: 'bg-amber-500' },
  { v: 'no_hire', label: '✕ No Hire',  color: 'bg-red-600'   },
]

export default function SubmitReport() {
  const [searchParams] = useSearchParams()
  const preselectedId  = searchParams.get('interview')
  const navigate       = useNavigate()

  const { data: listData, loading: listLoading } = useFetch(
    () => interviewService.list({ status: 'report_pending', per_page: 50 }),
    []
  )
  const pendingInterviews = 
    listData?.items || []

  const [selectedId, setSelectedId] = useState(preselectedId || '')
  const [scores, setScores] = useState(
    Object.fromEntries(DIMENSIONS.map(d => [d, { score: 5, notes: '' }]))
  )

  const [scoresLocked, setScoresLocked] = useState(false)

  const [report, setReport] = useState({
    summary: '',
    strengths: '',
    weaknesses: '',
    recommendation: '',
    decision: ''
  })

  const [loading, setLoading] = useState(false)
  const [genAI, setGenAI] = useState(false)

  useEffect(() => { 
    if (preselectedId) setSelectedId(preselectedId) 
  }, [preselectedId])

  const handleLockScores = async () => {
    if (!selectedId) {
      toast.error('Select an interview first')
      return
    }

    try {

      const scorePayload = DIMENSIONS.map(d => ({
        dimension: d,
        score: scores[d].score,
        notes: scores[d].notes || undefined,
      }))

      // create report placeholder so AI can attach feedback
      try {
        await reportService.getByInterview(selectedId)
      } catch {
        await reportService.create(selectedId, {})
      }

      setScoresLocked(true)

      toast.success("Scores locked. You can now generate AI feedback.")

    } catch (err) {
      toast.error(err?.response?.data?.error || 'Failed to lock scores')
    }
  }

  const getReportId = async () => {
    const res = await reportService.getByInterview(selectedId)
    return res.id
  }

  const handleSubmit = async () => {
    if (!selectedId) {
      toast.error('Select an interview first')
      return
    }

    setLoading(true)

    try {

      const reportData = {
        ...report,
        strengths: Array.isArray(report.strengths)
          ? report.strengths.join("\n")
          : report.strengths,

        weaknesses: Array.isArray(report.weaknesses)
          ? report.weaknesses.join("\n")
          : report.weaknesses,

        decision: report.decision || undefined,
      }

      const reportId = await getReportId()

      await reportService.update(reportId, reportData)

      toast.success('Report submitted!')
      navigate('/interviewer/interviews')
      window.location.reload()

    } catch (err) {
      toast.error(err?.response?.data?.error || 'Submission failed')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateAI = async () => {
    if (!selectedId) { 
      toast.error('Select an interview first'); 
      return 
    }

    setGenAI(true)

    try {
      const ai = await reportService.generateAI(selectedId)

      setReport(r => ({
        ...r,
        summary: ai.summary || r.summary,
        strengths: Array.isArray(ai.strengths) ? ai.strengths.join('\n') : ai.strengths,
        weaknesses: Array.isArray(ai.weaknesses) ? ai.weaknesses.join('\n') : ai.weaknesses
      }))

      toast.success('AI feedback generated and pre-filled!')

    } catch (err) {
      toast.error(err?.response?.data?.error || 'AI generation failed')
    } finally {
      setGenAI(false)
    }
  }

  if (listLoading) return <DashboardLayout><PageSpinner /></DashboardLayout>

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Interviewer</p>
          <h1 className="font-display text-3xl text-forest-900">Submit Evaluation Report</h1>
        </div>

        {pendingInterviews.length === 0 ? (
          <div className="card">
            <EmptyState icon="📝" title="No pending reports"
              description="You have no interviews awaiting a report. Nice work!" />
          </div>
        ) : (
          <>
            <div className="card mb-5">
              <label className="label">Select Interview</label>
              <select
                className="input"
                value={selectedId}
                onChange={e => setSelectedId(e.target.value)}
              >
                <option value="">— Choose an interview —</option>
                {pendingInterviews.map(iv => (
                  <option key={iv.id} value={iv.id}>{iv.title}</option>
                ))}
              </select>
            </div>

            <div className="card mb-5">
              <h2 className="font-display text-lg text-forest-900 mb-4">Dimension Scores</h2>

              <div className="space-y-5">
                {DIMENSIONS.map(dim => (
                  <div key={dim}>
                    <div className="flex items-center justify-between mb-1.5">
                      <label className="label mb-0">{dim}</label>
                      <span className="text-forest-900 font-bold text-sm">
                        {scores[dim].score}/10
                      </span>
                    </div>

                    <input
                      type="range"
                      min={1}
                      max={10}
                      value={scores[dim].score}
                      disabled={scoresLocked}
                      onChange={e =>
                        setScores(s => ({
                          ...s,
                          [dim]: { ...s[dim], score: +e.target.value }
                        }))
                      }
                      className="w-full accent-forest-900 mb-2"
                    />

                    <div className="h-1.5 bg-cream-200 rounded-full overflow-hidden -mt-1">
                      <div
                        className="h-full bg-forest-700 rounded-full transition-all"
                        style={{ width: `${scores[dim].score * 10}%` }}
                      />
                    </div>

                    <input
                      className="input mt-2 text-xs"
                      disabled={scoresLocked}
                      placeholder={`Notes on ${dim} (optional)`}
                      value={scores[dim].notes}
                      onChange={e =>
                        setScores(s => ({
                          ...s,
                          [dim]: { ...s[dim], notes: e.target.value }
                        }))
                      }
                    />
                  </div>
                ))}
              </div>

              <div className="flex justify-end mt-4">
                <button
                  onClick={handleLockScores}
                  disabled={scoresLocked}
                  className="btn-primary"
                >
                  {scoresLocked ? "Scores Locked ✓" : "Lock Scores"}
                </button>
              </div>
            </div>

            <div className="card mb-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-display text-lg text-forest-900">
                  Written Evaluation
                </h2>

                <button
                  onClick={handleGenerateAI}
                  disabled={!selectedId || genAI || !scoresLocked}
                  className="btn-secondary text-xs py-2 px-4 flex items-center gap-1.5"
                >
                  {genAI ? (
                    <>
                      <span className="w-3 h-3 border-2 border-forest-900 border-t-transparent rounded-full animate-spin" />
                      Generating…
                    </>
                  ) : '🤖 Fill with AI'}
                </button>
              </div>

              <div className="space-y-4">
                {[
                  { k: 'summary', label: 'Overall Summary', rows: 3 },
                  { k: 'strengths', label: 'Strengths', rows: 2 },
                  { k: 'weaknesses', label: 'Areas for Improvement', rows: 2 },
                  { k: 'recommendation', label: 'Recommendation', rows: 2 },
                ].map(field => (
                  <div key={field.k}>
                    <label className="label">{field.label}</label>
                    <textarea
                      className="input resize-none"
                      rows={field.rows}
                      value={report[field.k]}
                      onChange={e =>
                        setReport(r => ({ ...r, [field.k]: e.target.value }))
                      }
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="card mb-6">
              <h2 className="font-display text-lg text-forest-900 mb-4">Hire Decision</h2>

              <div className="grid grid-cols-3 gap-3">
                {DECISIONS.map(d => (
                  <button
                    key={d.v}
                    onClick={() =>
                      setReport(r => ({
                        ...r,
                        decision: r.decision === d.v ? '' : d.v
                      }))
                    }
                    className={`py-3 rounded-xl font-semibold text-sm border-2 transition-all ${
                      report.decision === d.v
                        ? `${d.color} text-white border-transparent`
                        : 'border-cream-300 text-forest-700 hover:border-forest-400 bg-white'
                    }`}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => navigate('/interviewer/interviews')}
                className="btn-secondary"
              >
                Cancel
              </button>

              <button
                onClick={handleSubmit}
                disabled={loading || !selectedId || !report.decision}
                className="btn-primary"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Submitting…
                  </span>
                ) : 'Submit Report →'}
              </button>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  )
}