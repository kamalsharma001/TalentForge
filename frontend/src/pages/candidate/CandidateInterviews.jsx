import { useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useInterviews } from '../../hooks'
import { StatusBadge, EmptyState, PageSpinner } from '../../components/ui'
import { format } from 'date-fns'

export function CandidateInterviews() {
  const [activeTab, setActiveTab] = useState('upcoming')
  const { data, loading } = useInterviews({ per_page: 50 })
  const interviews = data?.items || []

  const upcoming = interviews.filter(iv => iv.status === 'scheduled')
  const history = interviews.filter(iv => iv.status === 'completed')
  const publishedReports = interviews.filter(iv => iv.status === 'completed' && iv.report && iv.report.is_published)

  let displayedInterviews = []
  if (activeTab === 'upcoming') displayedInterviews = upcoming
  else if (activeTab === 'history') displayedInterviews = history
  else if (activeTab === 'published') displayedInterviews = publishedReports

  const tabs = [
    { id: 'upcoming', label: 'Upcoming', count: upcoming.length },
    { id: 'history', label: 'Completed / History', count: history.length },
    { id: 'published', label: 'Published Reports', count: publishedReports.length }
  ]

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Candidate</p>
          <h1 className="font-display text-3xl text-forest-900">My Interviews</h1>
        </div>

        {/* Tab Selection */}
        <div className="flex border-b border-cream-200 gap-6 mb-6">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 text-sm font-semibold transition-all relative ${
                activeTab === tab.id
                  ? 'text-forest-900 border-b-2 border-forest-900'
                  : 'text-forest-400 hover:text-forest-600'
              }`}
            >
              {tab.label}
              <span className="ml-1.5 px-2 py-0.5 text-xs bg-cream-100 rounded-full text-forest-600">
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        <div className="card">
          {loading ? (
            <PageSpinner />
          ) : displayedInterviews.length === 0 ? (
            <EmptyState
              icon="📋"
              title="No interviews found"
              description={`You have no ${activeTab === 'published' ? 'published reports' : activeTab + ' interviews'} yet.`}
            />
          ) : (
            <div className="space-y-3">
              {displayedInterviews.map(iv => (
                <div key={iv.id} className="flex items-center justify-between p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors">
                  <Link to={`/interviews/${iv.id}`} className="flex items-center gap-4 flex-1 min-w-0">
                    <div className="w-10 h-10 bg-forest-100 rounded-xl flex items-center justify-center text-forest-700 font-mono font-bold text-xs">
                      {(iv.tech_stack?.[0] || 'GEN').slice(0,3).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                      <p className="text-forest-500 text-xs mt-0.5">
                        {iv.tech_stack?.slice(0,3).join(', ') || 'General'} ·{' '}
                        {iv.scheduled_at ? format(new Date(iv.scheduled_at), 'MMM d, yyyy · h:mma') : 'Not yet scheduled'}
                      </p>
                    </div>
                  </Link>

                  <div className="flex items-center gap-3">
                    <StatusBadge status={iv.status} />

                    {activeTab === 'upcoming' && iv.meeting_link && (
                      <Link to={`/interviews/${iv.id}/room`} className="text-xs bg-amber-400 text-forest-900 font-bold px-3 py-1.5 rounded-full hover:bg-amber-300">
                        Join
                      </Link>
                    )}

                    {activeTab === 'published' && iv.report && (
                      <Link to={`/reports/${iv.id}`} className="text-xs bg-forest-900 text-white font-semibold px-3 py-1.5 rounded-full hover:bg-forest-800">
                        View Report
                      </Link>
                    )}
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

export function CandidateReports() {
  const { data, loading } = useInterviews({ status: 'completed', per_page: 30 })
  const interviews = data?.items || []
  const published = interviews.filter(iv => iv.report && iv.report.is_published)

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
          {loading ? <PageSpinner /> : published.length === 0 ? (
            <EmptyState icon="📊" title="No reports yet" description="Complete an interview to see your evaluation" />
          ) : (
            <div className="space-y-3">
              {published.map(iv => (
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
