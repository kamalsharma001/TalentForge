import { useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useInterviews } from '../../hooks'
import { StatusBadge, EmptyState, PageSpinner } from '../../components/ui'
import { format } from 'date-fns'

export default function InterviewerInterviews() {
  const [activeTab, setActiveTab] = useState('upcoming')
  const { data, loading } = useInterviews({ per_page: 50 })
  const interviews = data?.items || []

  // Filter groups
  const upcoming = interviews.filter(iv => iv.status === 'scheduled')
  const history = interviews.filter(iv => ['completed', 'report_pending'].includes(iv.status))
  const reportHistory = interviews.filter(iv => iv.status === 'completed' && iv.report)

  let displayedInterviews = []
  if (activeTab === 'upcoming') displayedInterviews = upcoming
  else if (activeTab === 'history') displayedInterviews = history
  else if (activeTab === 'reports') displayedInterviews = reportHistory

  const tabs = [
    { id: 'upcoming', label: 'Upcoming', count: upcoming.length },
    { id: 'history', label: 'Completed / History', count: history.length },
    { id: 'reports', label: 'Report History', count: reportHistory.length }
  ]

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Interviewer</p>
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
              description={`You have no ${activeTab === 'reports' ? 'report submissions' : activeTab + ' interviews'} yet.`}
            />
          ) : (
            <div className="space-y-3">
              {displayedInterviews.map(iv => (
                <div key={iv.id} className="p-4 rounded-xl border border-cream-200 hover:border-forest-300 transition-all bg-white shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
                  
                  {/* Info details */}
                  <div className="flex items-start gap-4 min-w-0">
                    <div className="w-10 h-10 bg-forest-900 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                      {(iv.tech_stack?.[0] || 'GEN').slice(0,3).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <Link to={`/interviews/${iv.id}`} className="font-semibold text-forest-900 text-sm hover:underline block truncate">
                        {iv.title}
                      </Link>
                      
                      <div className="text-forest-500 text-xs mt-1 space-y-1">
                        <p>
                          <span className="font-semibold">Candidate:</span> {iv.candidate_email || 'None'}
                        </p>
                        <p>
                          <span className="font-semibold">Tech Stack:</span> {iv.tech_stack?.join(', ') || 'General'}
                        </p>
                        <p>
                          <span className="font-semibold">Date:</span> {iv.scheduled_at ? format(new Date(iv.scheduled_at), 'PPP p') : 'TBD'}
                        </p>
                        {activeTab === 'reports' && iv.report && (
                          <p className="text-forest-700">
                            <span className="font-semibold">Score:</span> {iv.report.overall_score !== null ? `${iv.report.overall_score}/10` : 'Not scored'} ·{' '}
                            <span className="font-semibold">Decision:</span> <span className="capitalize">{iv.report.decision || 'None'}</span>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Actions / Badges */}
                  <div className="flex items-center gap-3 self-end md:self-center">
                    {activeTab === 'reports' && iv.report && (
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        iv.report.is_published 
                          ? 'bg-green-50 text-green-700 border border-green-200' 
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}>
                        {iv.report.is_published ? 'Published' : 'Draft'}
                      </span>
                    )}

                    <StatusBadge status={iv.status} />

                    {activeTab === 'upcoming' && iv.meeting_link && (
                      <Link to={`/interviews/${iv.id}/room`} className="text-xs bg-amber-400 text-forest-900 font-bold px-4.5 py-2 rounded-full hover:bg-amber-300 shadow-sm transition-all">
                        Join
                      </Link>
                    )}

                    {iv.status === 'report_pending' && (
                      <Link to={`/interviewer/reports?interview=${iv.id}`} className="text-xs bg-forest-900 text-white font-semibold px-4.5 py-2 rounded-full hover:bg-forest-800 shadow-sm transition-all">
                        Submit Report
                      </Link>
                    )}

                    {iv.report && (
                      <Link to={`/reports/${iv.id}`} className="text-xs bg-forest-950 text-white font-semibold px-4.5 py-2 rounded-full hover:bg-forest-850 shadow-sm transition-all">
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
