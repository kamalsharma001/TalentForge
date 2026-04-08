import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { useInterviews } from '../../hooks'
import { StatCard, StatusBadge, EmptyState, PageSpinner } from '../../components/ui'
import { format } from 'date-fns'

export default function InterviewerDashboard() {
  const { user } = useAuth()
  const { data, loading } = useInterviews({ per_page: 5 })
  const interviews = data?.items || []

  const cleanStatus = status => status?.split(".").pop()

  const scheduled = interviews.filter(
  iv => cleanStatus(iv.status) === 'scheduled'
  ).length

  const completed = interviews.filter(
  iv => ['completed','report_pending'].includes(cleanStatus(iv.status))
  ).length


  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto animate-fade-in">
        <div className="mb-8">
          <p className="section-label">Interviewer Dashboard</p>
          <h1 className="font-display text-3xl text-forest-900">Welcome, {user?.first_name}</h1>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Assigned"   value={data?.total || 0} icon="📋" variant="green" />
          <StatCard label="Upcoming"         value={scheduled}         icon="📅" />
          <StatCard label="Completed"        value={completed}         icon="✅" />
          <StatCard label="Reports Pending"  value={interviews.filter(iv => cleanStatus(iv.status) === 'report_pending').length} icon="📝" variant="amber" />
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-xl text-forest-900">Upcoming Interviews</h2>
              <Link to="/interviewer/interviews" className="text-forest-600 text-sm hover:text-forest-900">View all →</Link>
            </div>
            {loading ? <PageSpinner /> : interviews.filter(iv => cleanStatus(iv.status) === 'scheduled').length === 0 ? (
              <EmptyState icon="📅" title="No upcoming interviews" description="Check back when you're assigned" />
            ) : (
              <div className="space-y-3">
                {interviews.filter(iv => cleanStatus(iv.status) === 'scheduled').map(iv => (
                  <Link key={iv.id} to={`/interviews/${iv.id}`}
                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-cream-50 transition-colors">
                    <div className="w-9 h-9 bg-forest-100 rounded-lg flex items-center justify-center text-forest-700 text-sm font-bold">
                      {format(new Date(iv.scheduled_at), 'd')}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                      <p className="text-forest-500 text-xs">{format(new Date(iv.scheduled_at), 'MMM d, h:mma')}</p>
                    </div>
                    {iv.meeting_link && (
                      <a href={iv.meeting_link} target="_blank" rel="noopener noreferrer"
                        className="text-xs bg-forest-900 text-white px-3 py-1.5 rounded-full hover:bg-forest-800"
                        onClick={e => e.stopPropagation()}>
                        Join
                      </a>
                    )}
                  </Link>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-xl text-forest-900">Pending Reports</h2>
              <Link to="/interviewer/reports" className="text-forest-600 text-sm hover:text-forest-900">Submit →</Link>
            </div>
            {interviews.filter(iv => cleanStatus(iv.status) === 'report_pending').length === 0 ? (
              <EmptyState icon="📝" title="All reports submitted" description="Great work!" />
            ) : (
              <div className="space-y-3">
                {interviews.filter(iv => cleanStatus(iv.status) === 'report_pending').map(iv => (
                  <Link key={iv.id} to={`/interviewer/reports?interview=${iv.id}`}
                    className="flex items-center gap-3 p-3 rounded-xl bg-amber-50 border border-amber-200 hover:border-amber-400 transition-colors">
                    <span className="text-amber-500 text-lg">⏳</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                      <p className="text-forest-500 text-xs">Report due</p>
                    </div>
                    <span className="text-xs font-semibold text-amber-600">Submit</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="grid sm:grid-cols-2 gap-4 mt-6">
          <Link to="/interviewer/schedule"
            className="card flex items-center gap-4 hover:shadow-card-hover transition-shadow">
            <div className="w-12 h-12 bg-forest-100 rounded-xl flex items-center justify-center text-2xl">📅</div>
            <div>
              <p className="font-semibold text-forest-900">Manage Availability</p>
              <p className="text-forest-500 text-sm">Set your free slots</p>
            </div>
          </Link>
          <Link to="/interviewer/reports"
            className="card-yellow border-amber-200 flex items-center gap-4 hover:shadow-card-hover transition-shadow">
            <div className="w-12 h-12 bg-amber-400 rounded-xl flex items-center justify-center text-2xl">📝</div>
            <div>
              <p className="font-semibold text-forest-900">Submit Report</p>
              <p className="text-forest-600 text-sm">Evaluate your candidates</p>
            </div>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  )
}
