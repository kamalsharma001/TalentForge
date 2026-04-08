import { useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useInterviews } from '../../hooks'
import { StatusBadge, EmptyState, PageSpinner } from '../../components/ui'
import { format } from 'date-fns'

export default function InterviewerInterviews() {
  const [status, setStatus] = useState('')
  const { data, loading } = useInterviews({ status: status || undefined, per_page: 20 })
  const interviews = data?.items || []

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Interviewer</p>
          <h1 className="font-display text-3xl text-forest-900">My Interviews</h1>
        </div>

        <div className="flex gap-2 mb-5 flex-wrap">
          {['', 'scheduled', 'completed', 'report_pending'].map(s => (
            <button key={s} onClick={() => setStatus(s)}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold border transition-all capitalize ${
                status === s ? 'bg-forest-900 text-white border-forest-900' : 'bg-white border-cream-300 text-forest-600 hover:border-forest-600'
              }`}>
              {s || 'All'}
            </button>
          ))}
        </div>

        <div className="card">
          {loading ? <PageSpinner /> : interviews.length === 0 ? (
            <EmptyState icon="📋" title="No interviews assigned yet"
              description="Add availability slots so recruiters can book you" />
          ) : (
            <div className="space-y-3">
              {interviews.map(iv => (
                <Link key={iv.id} to={`/interviews/${iv.id}`}
                  className="flex items-center gap-4 p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors">
                  <div className="w-10 h-10 bg-forest-900 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                    {(iv.tech_stack?.[0] || 'T').slice(0,2).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>
                    <p className="text-forest-500 text-xs mt-0.5">
                      {iv.tech_stack?.slice(0,3).join(', ') || 'General'} ·{' '}
                      {iv.scheduled_at ? format(new Date(iv.scheduled_at), 'MMM d, h:mma') : 'TBD'}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <StatusBadge status={iv.status} />
                    {iv.status === 'scheduled' && iv.meeting_link && (
                      <a href={iv.meeting_link} target="_blank" rel="noopener noreferrer"
                        className="text-xs bg-amber-400 text-forest-900 font-bold px-3 py-1.5 rounded-full hover:bg-amber-300"
                        onClick={e => e.stopPropagation()}>
                        Join
                      </a>
                    )}
                    {iv.status === 'report_pending' && (
                      <Link to={`/interviewer/reports?interview=${iv.id}`}
                        className="text-xs bg-forest-900 text-white font-semibold px-3 py-1.5 rounded-full hover:bg-forest-800"
                        onClick={e => e.stopPropagation()}>
                        Submit Report
                      </Link>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
