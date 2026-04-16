import { useState } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { EmptyState, PageSpinner, Badge, Pagination } from '../../components/ui'
import { parseApiError } from '../../utils'
import practiceService from '../../services/practiceService'

const CATEGORY_OPTIONS = [
  { value: 'behavioral',    label: 'Behavioral'    },
  { value: 'technical',     label: 'Technical'     },
  { value: 'system_design', label: 'System Design' },
]

const DIFFICULTY_OPTIONS = [
  { value: 'easy',   label: 'Easy'   },
  { value: 'medium', label: 'Medium' },
  { value: 'hard',   label: 'Hard'   },
]

const JOB_ROLE_OPTIONS = [
  { value: 'Software Engineer',        label: 'Software Engineer'        },
  { value: 'Senior Software Engineer', label: 'Senior Software Engineer' },
  { value: 'Staff Engineer',           label: 'Staff Engineer'           },
  { value: 'Backend Engineer',         label: 'Backend Engineer'         },
  { value: 'Frontend Engineer',        label: 'Frontend Engineer'        },
  { value: 'Full Stack Engineer',      label: 'Full Stack Engineer'      },
  { value: 'DevOps Engineer',          label: 'DevOps Engineer'          },
  { value: 'Cloud Engineer',           label: 'Cloud Engineer'           },
  { value: 'Data Engineer',            label: 'Data Engineer'            },
  { value: 'Data Scientist',           label: 'Data Scientist'           },
  { value: 'ML Engineer',              label: 'ML Engineer'              },
  { value: 'AI Engineer',              label: 'AI Engineer'              },
  { value: 'Mobile Engineer',          label: 'Mobile Engineer'          },
  { value: 'iOS Engineer',             label: 'iOS Engineer'             },
  { value: 'Android Engineer',         label: 'Android Engineer'         },
  { value: 'QA Engineer',              label: 'QA Engineer'              },
  { value: 'SDET',                     label: 'SDET'                     },
  { value: 'Security Engineer',        label: 'Security Engineer'        },
  { value: 'Site Reliability Engineer',label: 'Site Reliability Engineer'},
  { value: 'Platform Engineer',        label: 'Platform Engineer'        },
  { value: 'Embedded Engineer',        label: 'Embedded Engineer'        },
  { value: 'Database Administrator',   label: 'Database Administrator'   },
  { value: 'Network Engineer',         label: 'Network Engineer'         },
  { value: 'Solutions Architect',      label: 'Solutions Architect'      },
  { value: 'Engineering Manager',      label: 'Engineering Manager'      },
  { value: 'Technical Lead',           label: 'Technical Lead'           },
  { value: 'Product Manager',          label: 'Product Manager'          },
  { value: 'Technical Program Manager',label: 'Technical Program Manager'},
  { value: 'UI/UX Designer',           label: 'UI/UX Designer'           },
  { value: 'Business Analyst',         label: 'Business Analyst'         },
]

const DIFFICULTY_VARIANT = {
  easy:   'green',
  medium: 'amber',
  hard:   'red',
}

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

export default function PracticeQuestions() {
  const [category, setCategory]     = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [jobRole, setJobRole]       = useState('')
  const [page, setPage]             = useState(1)
  const [expanded, setExpanded]     = useState(null)

  // Questions are NOT fetched by default — only after clicking the button
  const [questions, setQuestions]   = useState([])
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal]           = useState(0)
  const [loading, setLoading]       = useState(false)
  const [fetched, setFetched]       = useState(false)
  const [error, setError]           = useState(null)

  const canSearch = category && difficulty && jobRole

  const fetchQuestions = async (requestedPage = 1) => {
    if (!canSearch) return
    setLoading(true)
    setError(null)
    try {
      const data = await practiceService.list({
        page: requestedPage,
        per_page: 12,
        category,
        difficulty,
        job_role: jobRole,
      })
      setQuestions(data.items || [])
      setTotalPages(data.pages || 1)
      setTotal(data.total || 0)
      setPage(requestedPage)
      setFetched(true)
      setExpanded(null)
    } catch (err) {
      setError(parseApiError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => fetchQuestions(1)

  const handlePageChange = (newPage) => fetchQuestions(newPage)

  const toggleExpand = (id) => {
    setExpanded(prev => prev === id ? null : id)
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="mb-8">
          <p className="section-label">Candidate</p>
          <h1 className="font-display text-3xl text-forest-900">Practice Questions</h1>
          <p className="text-forest-500 text-sm mt-1">Select a role, difficulty, and category — then browse questions with answers</p>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <h2 className="font-display text-lg text-forest-900 mb-4">Choose your filters</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="text-xs font-semibold text-forest-600 block mb-1">Job Role <span className="text-red-400">*</span></label>
              <select
                value={jobRole}
                onChange={(e) => { setJobRole(e.target.value); setFetched(false) }}
                className="w-full px-3 py-2 rounded-lg border border-cream-200 bg-cream-50 text-forest-900 text-sm focus:outline-none focus:ring-2 focus:ring-forest-300"
              >
                <option value="">— Select a role —</option>
                {JOB_ROLE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-forest-600 block mb-1">Difficulty <span className="text-red-400">*</span></label>
              <select
                value={difficulty}
                onChange={(e) => { setDifficulty(e.target.value); setFetched(false) }}
                className="w-full px-3 py-2 rounded-lg border border-cream-200 bg-cream-50 text-forest-900 text-sm focus:outline-none focus:ring-2 focus:ring-forest-300"
              >
                <option value="">— Select difficulty —</option>
                {DIFFICULTY_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-forest-600 block mb-1">Category <span className="text-red-400">*</span></label>
              <select
                value={category}
                onChange={(e) => { setCategory(e.target.value); setFetched(false) }}
                className="w-full px-3 py-2 rounded-lg border border-cream-200 bg-cream-50 text-forest-900 text-sm focus:outline-none focus:ring-2 focus:ring-forest-300"
              >
                <option value="">— Select category —</option>
                {CATEGORY_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
          </div>
          <button
            onClick={handleSearch}
            disabled={!canSearch || loading}
            className="btn-primary text-sm px-6 py-2.5 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? 'Searching…' : '🔍 Get Questions'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="card-yellow border-amber-200 mb-5 flex items-start gap-3">
            <span className="text-lg">⚠️</span>
            <p className="text-forest-700 text-sm">{error}</p>
          </div>
        )}

        {/* Initial state — no search yet */}
        {!fetched && !loading && (
          <div className="card">
            <EmptyState
              icon="📚"
              title="Select your filters above"
              description="Pick a job role, difficulty level, and question category, then click 'Get Questions' to browse practice questions with sample answers"
            />
          </div>
        )}

        {/* Loading */}
        {loading && <PageSpinner />}

        {/* Results */}
        {fetched && !loading && (
          <>
            {/* Results header */}
            <div className="flex items-center justify-between mb-4">
              <p className="text-forest-600 text-sm font-medium">
                {total} question{total !== 1 ? 's' : ''} found for{' '}
                <span className="font-semibold text-forest-900">{jobRole}</span>
                {' · '}
                <Badge variant={DIFFICULTY_VARIANT[difficulty]}>{difficulty}</Badge>
                {' · '}
                <span className="text-forest-700">{CATEGORY_LABELS[category]}</span>
              </p>
            </div>

            {questions.length === 0 ? (
              <div className="card">
                <EmptyState
                  icon="🔍"
                  title="No questions found"
                  description="There are no practice questions matching your selection yet. Try a different combination."
                />
              </div>
            ) : (
              <div className="space-y-3">
                {questions.map((q, idx) => (
                  <div key={q.id} className="card p-0 overflow-hidden">
                    {/* Question header */}
                    <button
                      onClick={() => toggleExpand(q.id)}
                      className="w-full flex items-start gap-4 p-5 text-left hover:bg-cream-50 transition-colors"
                    >
                      <div className="w-8 h-8 bg-forest-900 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                        {idx + 1 + (page - 1) * 12}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-forest-900 text-sm leading-relaxed">{q.question}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant={DIFFICULTY_VARIANT[q.difficulty] || 'gray'}>
                            {q.difficulty}
                          </Badge>
                          <span className="text-forest-400 text-xs">·</span>
                          <span className="text-forest-500 text-xs">{CATEGORY_LABELS[q.category] || q.category}</span>
                          <span className="text-forest-400 text-xs">·</span>
                          <span className="text-forest-500 text-xs">{q.job_role}</span>
                        </div>
                      </div>
                      <span className={`text-forest-400 text-sm transition-transform flex-shrink-0 ${expanded === q.id ? 'rotate-180' : ''}`}>
                        ▾
                      </span>
                    </button>

                    {/* Expanded: hint + sample answer */}
                    {expanded === q.id && (
                      <div className="border-t border-cream-200 p-5 bg-cream-50 animate-fade-in">
                        {q.hint && (
                          <div className="mb-4">
                            <p className="text-xs font-semibold text-forest-600 uppercase tracking-wider mb-1">💡 Hint</p>
                            <p className="text-sm text-forest-700 leading-relaxed">{q.hint}</p>
                          </div>
                        )}
                        {q.sample_answer && (
                          <div>
                            <p className="text-xs font-semibold text-forest-600 uppercase tracking-wider mb-1">✅ Sample Answer</p>
                            <p className="text-sm text-forest-700 leading-relaxed whitespace-pre-wrap">{q.sample_answer}</p>
                          </div>
                        )}
                        {!q.hint && !q.sample_answer && (
                          <p className="text-sm text-forest-400 italic">No hint or sample answer available for this question.</p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            <Pagination
              page={page}
              pages={totalPages}
              onNext={() => handlePageChange(Math.min(page + 1, totalPages))}
              onPrev={() => handlePageChange(Math.max(page - 1, 1))}
              onGo={handlePageChange}
            />
          </>
        )}
      </div>
    </DashboardLayout>
  )
}
