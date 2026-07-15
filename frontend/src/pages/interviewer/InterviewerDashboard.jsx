import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { useInterviews } from '../../hooks'
import { PageSpinner } from '../../components/ui'
import { DashboardHeader, StatsCard, DashboardPanel, QuickActionCard, PanelEmptyState } from '../../components/dashboard/DashboardParts'
import { Link } from 'react-router-dom'
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
    iv => ['completed', 'report_pending'].includes(cleanStatus(iv.status))
  ).length

  const upcoming = interviews.filter(iv => cleanStatus(iv.status) === 'scheduled')
  const pendingReports = interviews.filter(iv => cleanStatus(iv.status) === 'report_pending')

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto animate-fade-in">
        <DashboardHeader
          label="Interviewer Dashboard"
          heading={`Welcome, ${user?.first_name} 👋`}
          description="Here's what's happening with your interviews today."
          illustration="default"
        />

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatsCard icon="📋" value={data?.total || 0} title="Total Assigned" subtitle="Interviews assigned to you" variant="green" />
          <StatsCard icon="📅" value={scheduled} title="Upcoming" subtitle="Interviews scheduled" />
          <StatsCard icon="✅" value={completed} title="Completed" subtitle="Interviews completed" />
          <StatsCard icon="📝" value={pendingReports.length} title="Reports Pending" subtitle="Reports awaiting submission" variant="amber" />
        </div>

        <div className="grid lg:grid-cols-2 gap-5 mb-5">
          <DashboardPanel title="Upcoming Interviews" actionLabel="View all" actionTo="/interviewer/interviews">
            {loading ? <PageSpinner /> : upcoming.length === 0 ? (
              <PanelEmptyState icon="📅" title="No upcoming interviews" description="Check back when you're assigned" />
            ) : (
              <div className="space-y-2">
                {upcoming.map(iv => (
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
          </DashboardPanel>

          <DashboardPanel title="Pending Reports" actionLabel="Submit" actionTo="/interviewer/reports">
            {pendingReports.length === 0 ? (
              <PanelEmptyState icon="📝" title="All reports submitted" description="Great work!" />
            ) : (
              <div className="space-y-2">
                {pendingReports.map(iv => (
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
          </DashboardPanel>
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <QuickActionCard
            to="/interviewer/schedule"
            icon="📅"
            title="Manage Availability"
            description="Update your availability and manage your interview schedule."
          />
          <QuickActionCard
            to="/interviewer/reports"
            icon="📝"
            title="Submit Report"
            description="Submit your interview reports and feedback."
            tone="amber"
          />
        </div>
      </div>
    </DashboardLayout>
  )
}
