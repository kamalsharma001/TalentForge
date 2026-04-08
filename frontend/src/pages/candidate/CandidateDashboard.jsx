import { Link } from 'react-router-dom'
import { useEffect } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { useInterviews } from '../../hooks'
import { StatCard, EmptyState, PageSpinner } from '../../components/ui'
import { format } from 'date-fns'
import api from '../../services/api.js'

export default function CandidateDashboard() {
  const { user } = useAuth()
  const { data, loading } = useInterviews({ per_page: 5 })
  const interviews = data?.items || []

  useEffect(() => {
    api.get("/interviews/")
      .then(res => console.log("API RESPONSE:", res.data))
      .catch(err => console.log("API ERROR:", err.response || err))
  }, [])

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="mb-8">
          <p className="section-label">Candidate</p>
          <h1 className="font-display text-3xl text-forest-900">Hello, {user?.first_name} 👋</h1>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Interviews" value={data?.total || 0} icon="📋" variant="green" />
          <StatCard label="Upcoming" value={interviews.filter(iv => iv.status === 'scheduled').length} icon="📅" />
          <StatCard label="Completed" value={interviews.filter(iv => iv.status === 'completed').length} icon="✅" />
          <StatCard label="Reports Ready" value={interviews.filter(iv => iv.status === 'completed').length} icon="📊" variant="amber" />
        </div>

        {/* Upcoming */}
        <div className="card mb-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-xl text-forest-900">Upcoming Interviews</h2>
            <Link to="/candidate/interviews" className="text-forest-600 text-sm hover:text-forest-900">View all →</Link>
          </div>
          {loading ? <PageSpinner /> : (
            interviews.filter(iv => iv.status === 'scheduled').length === 0 ? (
              <EmptyState icon="📅" title="No upcoming interviews" description="Your recruiter will schedule one soon" />
            ) : (
              <div className="space-y-3">
                {interviews.filter(iv => iv.status === 'scheduled').map(iv => (
                  <div key={iv.id} className="flex items-center gap-4 p-4 rounded-xl border border-forest-200 bg-forest-50">
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
            )
          )}
        </div>

        {/* Tips */}
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
