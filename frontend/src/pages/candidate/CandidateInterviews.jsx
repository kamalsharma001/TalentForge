import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useInterviews } from '../../hooks'
import { StatusBadge, EmptyState, PageSpinner } from '../../components/ui'
import { format } from 'date-fns'

export function CandidateInterviews() {
  const { data, loading } = useInterviews({ per_page: 30 })
  const interviews = data?.items || []

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Candidate</p>
          <h1 className="font-display text-3xl text-forest-900">My Interviews</h1>
        </div>
        <div className="card">
          {loading ? <PageSpinner /> : interviews.length === 0 ? (
            <EmptyState icon="📋" title="No interviews yet" description="Your recruiter will add you to an interview soon" />
          ) : (
            <div className="space-y-3">
              {interviews.map(iv => (
                <Link key={iv.id} to={`/interviews/${iv.id}`}
                  className="flex items-center gap-4 p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors">
                  <div className="w-10 h-10 bg-forest-100 rounded-xl flex items-center justify-center text-forest-700 font-mono font-bold text-xs">
                    {(iv.tech_stack?.[0] || 'GEN').slice(0,3).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                    <p className="text-forest-500 text-xs mt-0.5">
                      {iv.scheduled_at ? format(new Date(iv.scheduled_at), 'MMM d, yyyy · h:mma') : 'Not yet scheduled'}
                    </p>
                  </div>
                  <StatusBadge status={iv.status} />
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}

export function CandidateReports() {
  const { data, loading } = useInterviews({ status: 'completed', per_page: 30 })
  const interviews = data?.items || []

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Candidate</p>
          <h1 className="font-display text-3xl text-forest-900">My Reports</h1>
        </div>

        <div className="card-yellow border-amber-200 mb-5 flex items-start gap-3">
          <span className="text-lg">ℹ️</span>
          <p className="text-forest-700 text-sm">Reports are visible once your recruiter publishes them after reviewing.</p>
        </div>

        <div className="card">
          {loading ? <PageSpinner /> : interviews.length === 0 ? (
            <EmptyState icon="📊" title="No reports yet" description="Complete an interview to see your evaluation" />
          ) : (
            <div className="space-y-3">
              {interviews.map(iv => (
                <Link key={iv.id} to={`/reports/${iv.id}`}
                  className="flex items-center gap-4 p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors">
                  <div className="text-2xl">📊</div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-forest-900 text-sm">{iv.title}</p>
                    <p className="text-forest-500 text-xs mt-0.5">
                      {iv.completed_at ? format(new Date(iv.completed_at), 'MMM d, yyyy') : '—'}
                    </p>
                  </div>
                  <span className="text-xs text-forest-600 font-medium hover:text-forest-900">View →</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}

export default CandidateInterviews
