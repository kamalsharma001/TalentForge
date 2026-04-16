import { useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useFetch } from '../../hooks'
import { StatCard, EmptyState, PageSpinner, Badge } from '../../components/ui'
import { fmtRelative } from '../../utils'
import mockInterviewService from '../../services/mockInterviewService'

const CATEGORY_LABELS = {
  behavioral:    'Behavioral',
  technical:     'Technical',
  system_design: 'System Design',
}

const CATEGORY_ICONS = {
  behavioral:    '🗣️',
  technical:     '💻',
  system_design: '🏗️',
}

const STATUS_VARIANT = {
  pending:     'gray',
  in_progress: 'blue',
  completed:   'green',
}

const STATUS_LABEL = {
  pending:     'Pending',
  in_progress: 'In Progress',
  completed:   'Completed',
}

export default function MockInterviews() {
  const navigate = useNavigate()
  const [creating, setCreating] = useState(false)

  const fetchFn = useCallback(() => mockInterviewService.list({ per_page: 30 }), [])
  const { data, loading, refetch } = useFetch(fetchFn)
  const sessions = data?.items || []

  const stats = {
    total:       data?.total || 0,
    in_progress: sessions.filter(s => s.status === 'in_progress').length,
    completed:   sessions.filter(s => s.status === 'completed').length,
    avgScore:    sessions.filter(s => s.ai_score).length > 0
                   ? Math.round(sessions.filter(s => s.ai_score).reduce((a, s) => a + s.ai_score, 0) / sessions.filter(s => s.ai_score).length)
                   : '—',
  }

  const handleStart = async (category) => {
    setCreating(true)
    try {
      const session = await mockInterviewService.create({ category, difficulty: 'medium' })
      navigate(`/candidate/mock-interviews/${session.id}`)
    } catch (err) {
      console.error(err)
      setCreating(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="mb-8">
          <p className="section-label">Candidate</p>
          <h1 className="font-display text-3xl text-forest-900">Mock Interviews</h1>
          <p className="text-forest-500 text-sm mt-1">Practice solo with AI-evaluated feedback</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Sessions" value={stats.total} icon="🎯" variant="green" />
          <StatCard label="In Progress" value={stats.in_progress} icon="⏳" />
          <StatCard label="Completed" value={stats.completed} icon="✅" />
          <StatCard label="Avg Score" value={stats.avgScore} icon="📈" variant="amber" />
        </div>

        {/* Start new session */}
        <div className="card mb-6">
          <h2 className="font-display text-xl text-forest-900 mb-4">Start a New Session</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {['behavioral', 'technical', 'system_design'].map(cat => (
              <button
                key={cat}
                onClick={() => handleStart(cat)}
                disabled={creating}
                className="flex items-center gap-3 p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors text-left disabled:opacity-50"
              >
                <span className="text-2xl">{CATEGORY_ICONS[cat]}</span>
                <div>
                  <p className="font-semibold text-forest-900 text-sm">{CATEGORY_LABELS[cat]}</p>
                  <p className="text-forest-500 text-xs mt-0.5">Medium difficulty</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Past sessions */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-xl text-forest-900">Past Sessions</h2>
          </div>

          {loading ? <PageSpinner /> : sessions.length === 0 ? (
            <EmptyState icon="🎯" title="No sessions yet" description="Start a mock interview above to practice" />
          ) : (
            <div className="space-y-3">
              {sessions.map(s => (
                <Link
                  key={s.id}
                  to={`/candidate/mock-interviews/${s.id}`}
                  className="flex items-center gap-4 p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors"
                >
                  <div className="text-2xl flex-shrink-0">{CATEGORY_ICONS[s.category] || '📝'}</div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-forest-900 text-sm truncate">
                      {CATEGORY_LABELS[s.category] || s.category} — {s.difficulty}
                    </p>
                    <p className="text-forest-500 text-xs mt-0.5 truncate">{s.question_text}</p>
                    <p className="text-forest-400 text-xs mt-0.5">{fmtRelative(s.created_at)}</p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    {s.ai_score && (
                      <span className="text-xs font-bold text-forest-700 bg-forest-100 px-2 py-1 rounded-full">
                        {s.ai_score}/10
                      </span>
                    )}
                    <Badge variant={STATUS_VARIANT[s.status] || 'gray'}>
                      {STATUS_LABEL[s.status] || s.status}
                    </Badge>
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
