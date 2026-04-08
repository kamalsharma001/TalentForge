import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useInterviews } from '../../hooks'
import { DecisionBadge, EmptyState, PageSpinner } from '../../components/ui'
import { format } from 'date-fns'

export default function RecruiterReports() {
  const { data, loading } = useInterviews({ per_page: 50 })
  const interviews = (data?.items || []).filter(iv => iv.report)

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Recruiter</p>
          <h1 className="font-display text-3xl text-forest-900">Reports</h1>
        </div>

        <div className="card-yellow border-amber-200 mb-6 flex items-start gap-3">
          <span className="text-xl">🤖</span>
          <div>
            <p className="font-semibold text-forest-900 text-sm">AI-Powered Summaries</p>
            <p className="text-forest-600 text-sm">Every report includes AI-generated strengths, weaknesses, and an overall hire recommendation.</p>
          </div>
        </div>

        <div className="card">
          <h2 className="font-display text-xl text-forest-900 mb-4">Completed Interviews</h2>
          {loading ? <PageSpinner /> : interviews.length === 0 ? (
            <EmptyState icon="📊" title="No reports yet"
              description="Reports appear here once interviews are completed" />
          ) : (
            <div className="space-y-3">
              {interviews.map(iv => (
                <div key={iv.id}
                  className="flex items-center gap-4 p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                    <p className="text-forest-500 text-xs mt-0.5">
                      {iv.job_role || 'Technical'} ·{' '}
                      {iv.completed_at ? format(new Date(iv.completed_at), 'MMM d, yyyy') : '—'}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    {iv.overall_score && (
                      <div className="text-right">
                        <p className="text-forest-900 font-bold text-sm">{iv.overall_score}/10</p>
                        <p className="text-forest-400 text-xs">Score</p>
                      </div>
                    )}
                    <Link to={`/reports/${iv.id}`} className="btn-primary text-xs py-2 px-4">View Report</Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
