import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { useInterviews } from '../../hooks'
import { StatusBadge, PageSpinner } from '../../components/ui'
import { DashboardHeader, StatsCard, DashboardPanel, QuickActionCard, PanelEmptyState } from '../../components/dashboard/DashboardParts'
import { format } from 'date-fns'

export default function RecruiterDashboard() {
  const { user } = useAuth()
  const { data, loading } = useInterviews({ per_page: 5 })

  const interviews = data?.items || []
  const total = data?.total || 0

  const counts = interviews.reduce((acc, iv) => {
    acc[iv.status] = (acc[iv.status] || 0) + 1
    return acc
  }, {})

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto animate-fade-in">
        <DashboardHeader
          label="Recruiter Dashboard"
          heading={`Welcome back, ${user?.first_name} 👋`}
          description="Track hiring progress and manage interviews."
          illustration="recruiter"
          actions={
            <Link to="/recruiter/request" className="btn-primary">
              + New Interview
            </Link>
          }
        />

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatsCard icon="📋" value={total} title="Total Interviews" subtitle="All requested interviews" variant="green" />
          <StatsCard icon="📅" value={counts.scheduled || 0} title="Scheduled" subtitle="Interviews scheduled" />
          <StatsCard icon="✅" value={counts.completed || 0} title="Completed" subtitle="Interviews completed" />
          <StatsCard icon="📊" value={counts.report_pending || 0} title="Reports Ready" subtitle="Awaiting review" variant="amber" />
        </div>

        <div className="mb-5">
          <DashboardPanel title="Recent Interviews" actionLabel="View all" actionTo="/recruiter/interviews">
            {loading ? <PageSpinner /> : interviews.length === 0 ? (
              <PanelEmptyState
                icon="📋"
                title="No interviews yet"
                description="Request your first interview to get started"
              />
            ) : (
              <div className="space-y-2">
                {interviews.map(iv => (
                  <Link key={iv.id} to={`/interviews/${iv.id}`}
                    className="flex items-center gap-4 p-3 rounded-xl hover:bg-cream-50 transition-colors border border-transparent hover:border-cream-200">
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
          </DashboardPanel>
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <QuickActionCard
            to="/recruiter/request"
            icon="➕"
            title="Create Interview"
            description="Choose tech stack and schedule a new interview."
            tone="amber"
          />
          <QuickActionCard
            to="/recruiter/interviews"
            icon="📋"
            title="View Candidates"
            description="Browse candidates and interview pipeline."
          />
        </div>
      </div>
    </DashboardLayout>
  )
}
