import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import interviewService from '../../services/interviewService'
import toast from 'react-hot-toast'

const TECH_PROFILES = ['Frontend','Backend','Full Stack','iOS','Android','DevOps','ML/AI','Data Engineering','System Design','Python','Java','Node.js','React','AWS','PostgreSQL']
const DIFFICULTIES  = [
  { v: 'easy',   label: 'Entry Level',  desc: '0-2 years experience' },
  { v: 'medium', label: 'Mid Level',    desc: '2-5 years experience' },
  { v: 'hard',   label: 'Senior Level', desc: '5+ years experience' },
]

const STEPS = ['Profile & Role', 'Schedule', 'Review & Submit']

export default function RequestInterview() {
  const navigate  = useNavigate()
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)

  const [form, setForm] = useState({
    title: '', job_role: '', candidate_email: '',
    tech_stack: [], difficulty: 'medium',
    duration_mins: 60, instructions: '',
    scheduled_at: '', timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    // org + candidate IDs — in production these come from real data
    organization_id: '',
  })

  const toggle = (skill) => setForm(f => ({
    ...f,
    tech_stack: f.tech_stack.includes(skill)
      ? f.tech_stack.filter(s => s !== skill)
      : [...f.tech_stack, skill],
  }))

  const next = () => setStep(s => s + 1)
  const back = () => setStep(s => s - 1)

  const handleSubmit = async () => {
    if (!form.title) { toast.error('Interview title is required'); return }
    if (!form.candidate_email) { toast.error('Candidate email is required'); return } 
    setLoading(true)
    try {
      // Demo: we use placeholder UUIDs — in production these come from org/candidate lookup
      const payload = {
        title: form.title,
        job_role: form.job_role,
        candidate_email: form.candidate_email,
        organization_id: "550e8400-e29b-41d4-a716-446655440000",
        tech_stack: form.tech_stack,
        difficulty: form.difficulty,
        duration_mins: form.duration_mins,
        instructions: form.instructions,
        scheduled_at: form.scheduled_at || null,
        timezone: form.timezone
      }
      const iv = await interviewService.create(payload)
      toast.success('Interview request created!')
      navigate(`/interviews/${iv.id}`)
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Failed to create interview')
    } finally {
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto animate-fade-in">
        <div className="mb-8">
          <p className="section-label">Recruiter</p>
          <h1 className="font-display text-3xl text-forest-900">Request an Interview</h1>
          <p className="text-forest-500 text-sm mt-1">Fill in 3 simple steps to get started</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-8">
          {STEPS.map((label, i) => (
            <div key={i} className="flex items-center gap-2 flex-1">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 transition-colors ${
                i < step ? 'bg-forest-900 text-white' :
                i === step ? 'bg-amber-400 text-forest-900' :
                'bg-cream-300 text-forest-500'
              }`}>
                {i < step ? '✓' : i + 1}
              </div>
              <span className={`text-xs font-medium hidden sm:block ${i === step ? 'text-forest-900' : 'text-forest-400'}`}>
                {label}
              </span>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-0.5 rounded-full ${i < step ? 'bg-forest-900' : 'bg-cream-300'}`} />
              )}
            </div>
          ))}
        </div>

        <div className="card shadow-card-hover">
          {/* Step 0: Profile & Role */}
          {step === 0 && (
            <div className="space-y-5 animate-fade-in">
              <h2 className="font-display text-xl text-forest-900">Profile & Role</h2>

              <div>
                <label className="label">Interview title *</label>
                <input className="input" placeholder="e.g. Senior Backend Engineer Interview"
                  value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
              </div>

              <div>
                <label className="label">Job role</label>
                <input className="input" placeholder="e.g. Python Developer"
                  value={form.job_role} onChange={e => setForm(f => ({ ...f, job_role: e.target.value }))} />
              </div>

              <div>
                <label className="label">Tech stack / profiles</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {TECH_PROFILES.map(skill => (
                    <button key={skill} type="button" onClick={() => toggle(skill)}
                      className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                        form.tech_stack.includes(skill)
                          ? 'bg-forest-900 text-white border-forest-900'
                          : 'bg-white border-cream-300 text-forest-600 hover:border-forest-600'
                      }`}>
                      {skill}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="label">Difficulty level</label>
                <div className="grid grid-cols-3 gap-3">
                  {DIFFICULTIES.map(d => (
                    <button key={d.v} type="button" onClick={() => setForm(f => ({ ...f, difficulty: d.v }))}
                      className={`p-3 rounded-xl border-2 text-left transition-all ${
                        form.difficulty === d.v
                          ? 'border-forest-900 bg-forest-50'
                          : 'border-cream-300 hover:border-forest-400'
                      }`}>
                      <p className="font-semibold text-forest-900 text-sm">{d.label}</p>
                      <p className="text-forest-500 text-xs mt-0.5">{d.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="label">Duration</label>
                <select className="input" value={form.duration_mins}
                  onChange={e => setForm(f => ({ ...f, duration_mins: +e.target.value }))}>
                  {[30,45,60,90,120].map(m => (
                    <option key={m} value={m}>{m} minutes</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Special instructions for the interviewer</label>
                <textarea className="input resize-none" rows={3}
                  placeholder="Focus on system design, ask about distributed systems…"
                  value={form.instructions}
                  onChange={e => setForm(f => ({ ...f, instructions: e.target.value }))} />
              </div>
            </div>
          )}

          {/* Step 1: Schedule */}
          {step === 1 && (
            <div className="space-y-5 animate-fade-in">
              <h2 className="font-display text-xl text-forest-900">Schedule</h2>

              <div className="card-yellow border-amber-200">
                <p className="text-forest-700 font-sans text-sm">
                  💡 You can schedule now or leave it blank. Our team will contact you to arrange a suitable time.
                </p>
              </div>

              <div>
                <label className="label">Preferred date & time</label>
                <input className="input" type="datetime-local"
                  value={form.scheduled_at}
                  onChange={e => setForm(f => ({ ...f, scheduled_at: e.target.value }))} />
              </div>

              <div>
                <label className="label">Timezone</label>
                <input className="input" value={form.timezone}
                  onChange={e => setForm(f => ({ ...f, timezone: e.target.value }))}
                  placeholder="e.g. America/New_York" />
              </div>

              <div>
                <label className="label">Candidate email *</label>
                <input className="input" type="email" required placeholder="candidate@email.com"
                  value={form.candidate_email}
                  onChange={e => setForm(f => ({ ...f, candidate_email: e.target.value }))} />
              </div>
            </div>
          )}

          {/* Step 2: Review */}
          {step === 2 && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="font-display text-xl text-forest-900">Review & Submit</h2>
              <div className="space-y-3">
                {[
                  { label: 'Title',      value: form.title },
                  { label: 'Role',       value: form.job_role || '—' },
                  { label: 'Tech stack', value: form.tech_stack.join(', ') || '—' },
                  { label: 'Difficulty', value: DIFFICULTIES.find(d => d.v === form.difficulty)?.label },
                  { label: 'Duration',   value: `${form.duration_mins} minutes` },
                  { label: 'Scheduled',  value: form.scheduled_at ? new Date(form.scheduled_at).toLocaleString() : 'To be arranged' },
                ].map(row => (
                  <div key={row.label} className="flex items-start gap-4 py-2 border-b border-cream-200 last:border-0">
                    <span className="text-forest-500 text-sm w-28 flex-shrink-0">{row.label}</span>
                    <span className="text-forest-900 font-medium text-sm">{row.value}</span>
                  </div>
                ))}
              </div>
              {form.instructions && (
                <div className="bg-cream-100 rounded-xl p-3 text-sm text-forest-700">
                  <span className="font-semibold">Instructions: </span>{form.instructions}
                </div>
              )}
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-5 border-t border-cream-200">
            {step > 0 ? (
              <button onClick={back} className="btn-secondary">← Back</button>
            ) : <div />}
            {step < STEPS.length - 1 ? (
              <button onClick={next} disabled={step === 0 && !form.title} className="btn-primary">
                Next →
              </button>
            ) : (
              <button onClick={handleSubmit} disabled={loading} className="btn-primary">
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Submitting…
                  </span>
                ) : 'Submit Request →'}
              </button>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
