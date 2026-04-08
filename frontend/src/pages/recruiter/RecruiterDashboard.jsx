import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { useInterviews } from '../../hooks'
import { StatCard, StatusBadge, PageSpinner } from '../../components/ui'
import { format } from 'date-fns'

export default function RecruiterDashboard() {
  const { user } = useAuth()
  const { data, loading } = useInterviews({ per_page: 5 })

  const interviews = data?.items || []
  const total      = data?.total || 0

  const counts = interviews.reduce((acc, iv) => {
    acc[iv.status] = (acc[iv.status] || 0) + 1
    return acc
  }, {})

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="section-label">Recruiter Dashboard</p>
            <h1 className="font-display text-3xl text-forest-900">Overview</h1>
          </div>
          <Link to="/recruiter/request" className="btn-primary">
            + New Interview
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Interviews" value={total}            icon="📋" variant="green" />
          <StatCard label="Scheduled"        value={counts.scheduled || 0}      icon="📅" />
          <StatCard label="Completed"        value={counts.completed || 0}      icon="✅" />
          <StatCard label="Reports Ready"    value={counts.report_pending || 0} icon="📊" variant="amber" />
        </div>

        {/* Recent interviews */}
        <div className="card">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-display text-xl text-forest-900">Recent Interviews</h2>
            <Link to="/recruiter/interviews" className="text-forest-600 text-sm font-medium hover:text-forest-900">
              View all →
            </Link>
          </div>

          {loading ? <PageSpinner /> : interviews.length === 0 ? (
            <div className="py-12 text-center">
              <div className="text-4xl mb-3">📋</div>
              <p className="text-forest-500 mb-4">No interviews yet</p>
              <Link to="/recruiter/request" className="btn-primary text-sm">Request your first interview</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {interviews.map(iv => (
                <Link key={iv.id} to={`/interviews/${iv.id}`}
                  className="flex items-center gap-4 p-4 rounded-xl hover:bg-cream-50 transition-colors border border-transparent hover:border-cream-200">
                  <div className="w-10 h-10 bg-forest-100 rounded-xl flex items-center justify-center text-forest-700 font-mono text-xs font-bold flex-shrink-0">
                    {iv.difficulty?.[0]?.toUpperCase() || 'M'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                    <p className="text-forest-500 text-xs mt-0.5">
                      {iv.job_role || 'Technical Interview'} ·{' '}
                      {iv.scheduled_at ? format(new Date(iv.scheduled_at), 'MMM d, yyyy') : 'Not scheduled'}
                    </p>
                  </div>
                  <StatusBadge status={iv.status} />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Quick links */}
        <div className="grid sm:grid-cols-2 gap-4 mt-6">
          <Link to="/recruiter/request"
            className="card-yellow border-amber-200 flex items-center gap-4 hover:shadow-card-hover transition-shadow">
            <div className="w-12 h-12 bg-amber-400 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">➕</div>
            <div>
              <p className="font-semibold text-forest-900">Request New Interview</p>
              <p className="text-forest-600 text-sm">Choose tech stack and schedule</p>
            </div>
          </Link>
          <Link to="/recruiter/reports"
            className="card flex items-center gap-4 hover:shadow-card-hover transition-shadow">
            <div className="w-12 h-12 bg-forest-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">📊</div>
            <div>
              <p className="font-semibold text-forest-900">View Reports</p>
              <p className="text-forest-600 text-sm">AI-powered evaluation summaries</p>
            </div>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  )
}
