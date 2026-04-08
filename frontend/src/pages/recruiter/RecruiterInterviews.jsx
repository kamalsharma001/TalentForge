import { useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useInterviews } from '../../hooks'
import { StatusBadge, EmptyState, PageSpinner, Pagination } from '../../components/ui'
import { format } from 'date-fns'

const STATUSES = ['', 'pending', 'scheduled', 'completed', 'report_pending', 'cancelled']

export default function RecruiterInterviews() {
  const [status, setStatus] = useState('')
  const [page,   setPage]   = useState(1)
  const { data, loading, refetch } = useInterviews({ status: status || undefined, page, per_page: 15 })

  const interviews = data?.items || []

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

        {/* Filters */}
        <div className="flex flex-wrap gap-2 mb-5">
          {STATUSES.map(s => (
            <button key={s} onClick={() => { setStatus(s); setPage(1) }}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold border transition-all capitalize ${
                status === s
                  ? 'bg-forest-900 text-white border-forest-900'
                  : 'bg-white border-cream-300 text-forest-600 hover:border-forest-600'
              }`}>
              {s || 'All'}
            </button>
          ))}
        </div>

        <div className="card">
          {loading ? <PageSpinner /> : interviews.length === 0 ? (
            <EmptyState icon="📋" title="No interviews found"
              description="Adjust filters or create a new interview request"
              action={<Link to="/recruiter/request" className="btn-primary text-sm">Request Interview</Link>} />
          ) : (
            <div className="space-y-3">
              {interviews.map(iv => (
                <Link key={iv.id} to={`/interviews/${iv.id}`}
                  className="flex items-center gap-4 p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors">

                  <div className="w-10 h-10 bg-forest-100 rounded-xl flex items-center justify-center text-forest-700 font-bold text-xs">
                    {(iv.tech_stack?.[0] || 'GEN').slice(0,3).toUpperCase()}
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-forest-900 text-sm truncate">{iv.title}</p>

                    <p className="text-forest-500 text-xs mt-0.5">
                      {iv.scheduled_at
                        ? format(new Date(iv.scheduled_at), 'MMM d, yyyy · h:mma')
                        : 'Not yet scheduled'}
                    </p>
                  </div>

                  <StatusBadge status={iv.status} />

                </Link>
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
