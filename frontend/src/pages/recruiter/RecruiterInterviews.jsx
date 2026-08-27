import { useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useInterviews } from '../../hooks'
import { StatusBadge, EmptyState, PageSpinner, Pagination } from '../../components/ui'
import { format } from 'date-fns'

export default function RecruiterInterviews() {
  const [activeTab, setActiveTab] = useState('upcoming')
  const [page, setPage] = useState(1)
  const { data, loading } = useInterviews({ page, per_page: 40 })

  const interviews = data?.items || []

  const upcoming = interviews.filter(iv => ['pending', 'scheduled'].includes(iv.status))
  const history = interviews.filter(iv => ['completed', 'report_pending'].includes(iv.status))
  const cancelled = interviews.filter(iv => iv.status === 'cancelled')

  let displayedInterviews = []
  if (activeTab === 'upcoming') displayedInterviews = upcoming
  else if (activeTab === 'history') displayedInterviews = history
  else if (activeTab === 'cancelled') displayedInterviews = cancelled

  const tabs = [
    { id: 'upcoming', label: 'Upcoming', count: upcoming.length },
    { id: 'history', label: 'Completed / History', count: history.length },
    { id: 'cancelled', label: 'Cancelled', count: cancelled.length }
  ]

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="section-label">Recruiter</p>
            <h1 className="font-display text-3xl text-forest-900">Interviews</h1>
          </div>
          <Link to="/recruiter/request" className="btn-primary">+ New Interview</Link>
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
              description={`You have no ${activeTab} interviews at the moment.`}
              action={activeTab === 'upcoming' && <Link to="/recruiter/request" className="btn-primary text-sm">Request Interview</Link>}
            />
          ) : (
            <div className="space-y-3">
              {displayedInterviews.map(iv => (
                <div key={iv.id} className="flex items-center justify-between p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors">
                  <Link to={`/interviews/${iv.id}`} className="flex items-center gap-4 flex-1 min-w-0">
                    <div className="w-10 h-10 bg-forest-100 rounded-xl flex items-center justify-center text-forest-700 font-bold text-xs">
                      {(iv.tech_stack?.[0] || 'GEN').slice(0,3).toUpperCase()}
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                      <p className="text-forest-500 text-xs mt-0.5">
                        {iv.tech_stack?.slice(0,3).join(', ') || 'General'} ·{' '}
                        {iv.scheduled_at
                          ? format(new Date(iv.scheduled_at), 'MMM d, yyyy · h:mma')
                          : 'Not yet scheduled'}
                      </p>
                    </div>
                  </Link>

                  <div className="flex items-center gap-3">
                    <StatusBadge status={iv.status} />

                    {activeTab === 'history' && iv.report && (
                      <Link
                        to={`/reports/${iv.id}`}
                        className="text-xs bg-forest-950 text-white font-semibold px-3.5 py-1.5 rounded-full hover:bg-forest-800 transition-colors"
                      >
                        View Report
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
          <Pagination page={page} pages={data?.pages || 1}
            onNext={() => setPage(p => p + 1)} onPrev={() => setPage(p => p - 1)} onGo={setPage} />
        </div>
      </div>
    </DashboardLayout>
  )
}
