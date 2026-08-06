import { Link } from 'react-router-dom'
import { useEffect } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { useInterviews } from '../../hooks'
import { PageSpinner } from '../../components/ui'
import { DashboardHeader, StatsCard, DashboardPanel, QuickActionCard, PanelEmptyState } from '../../components/dashboard/DashboardParts'
import { format } from 'date-fns'
import api from '../../services/api.js'

export default function CandidateDashboard() {
  const { user } = useAuth()
  const { data, loading } = useInterviews({ per_page: 5 })
  const interviews = data?.items || []


  const upcoming = interviews.filter(iv => iv.status === 'scheduled')
  const completed = interviews.filter(iv => iv.status === 'completed')

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto animate-fade-in">
        <DashboardHeader
          label="Candidate"
          heading={`Welcome, ${user?.first_name} 👋`}
          description="Track your interview journey."
          illustration="candidate"
        />

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatsCard icon="📋" value={data?.total || 0} title="Total Interviews" subtitle="All your interviews" variant="green" />
          <StatsCard icon="📅" value={upcoming.length} title="Upcoming" subtitle="Interviews scheduled" />
          <StatsCard icon="✅" value={completed.length} title="Completed" subtitle="Interviews completed" />
          <StatsCard icon="📊" value={completed.length} title="Feedback Received" subtitle="Reports available" variant="amber" />
        </div>

        <div className="grid sm:grid-cols-2 gap-4 mb-5">
          <QuickActionCard
            to="/candidate/mock-interviews"
            icon="🎯"
            title="Start Mock Interview"
            description="Practice solo with AI-evaluated feedback"
          />
          <QuickActionCard
            to="/candidate/practice"
            icon="📚"
            title="Browse Practice Questions"
            description="Study by role, difficulty, and category"
            tone="amber"
          />
        </div>

        <div className="mb-5">
          <DashboardPanel title="Upcoming Interviews" actionLabel="View all" actionTo="/candidate/interviews">
            {loading ? <PageSpinner /> : upcoming.length === 0 ? (
              <PanelEmptyState icon="📅" title="No upcoming interviews" description="Your recruiter will schedule one soon" />
            ) : (
              <div className="space-y-2">
                {upcoming.map(iv => (
                  <div key={iv.id} className="flex items-center gap-4 p-3 rounded-xl border border-forest-200 bg-forest-50">
                    <div className="w-10 h-10 bg-forest-900 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                      {iv.scheduled_at ? format(new Date(iv.scheduled_at), 'd') : '?'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                      <p className="text-forest-500 text-xs">
                        {iv.scheduled_at ? format(new Date(iv.scheduled_at), 'EEEE, MMMM d · h:mm a') : 'Time TBD'}
                      </p>
                    </div>
                    {iv.meeting_link && (
                      <a href={iv.meeting_link} target="_blank" rel="noopener noreferrer"
                        className="btn-primary text-xs py-2 px-4">Join →</a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </DashboardPanel>
        </div>

        <div className="mb-5">
          <DashboardPanel title="Latest Feedback" actionLabel="View all" actionTo="/candidate/reports">
            {completed.length === 0 ? (
              <PanelEmptyState icon="💬" title="No feedback yet" description="Feedback appears here after your interviews are completed" />
            ) : (
              <div className="space-y-2">
                {completed.map(iv => (
                  <Link key={iv.id} to={`/reports/${iv.id}`}
                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-cream-50 transition-colors">
                    <span className="text-forest-500 text-lg">💬</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                      <p className="text-forest-500 text-xs">
                        {iv.scheduled_at ? format(new Date(iv.scheduled_at), 'MMM d, yyyy') : ''}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </DashboardPanel>
        </div>

        <div className="card-yellow border-amber-200">
          <h3 className="font-display text-lg text-forest-900 mb-3">Interview tips 💡</h3>
          <ul className="space-y-2 text-sm text-forest-700">
            {[
              'Join the meeting link 5 minutes early to check your audio/video',
              'Have a glass of water nearby — stay relaxed and hydrated',
              'Think aloud — interviewers love to understand your reasoning process',
              "It's okay to ask clarifying questions before diving into a solution",
            ].map((tip, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-amber-500 font-bold">·</span> {tip}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </DashboardLayout>
  )
}
