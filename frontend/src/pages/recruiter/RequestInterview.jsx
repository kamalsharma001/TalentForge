import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import interviewService from '../../services/interviewService'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

const TECH_PROFILES = ['Frontend','Backend','Full Stack','iOS','Android','DevOps','ML/AI','Data Engineering','System Design','Python','Java','Node.js','React','AWS','PostgreSQL']
const DIFFICULTIES  = [
  { v: 'easy',   label: 'Entry Level',  desc: '0-2 years experience' },
  { v: 'medium', label: 'Mid Level',    desc: '2-5 years experience' },
  { v: 'hard',   label: 'Senior Level', desc: '5+ years experience' },
]

const STEPS = ['Profile & Role', 'Schedule', 'Review & Submit']

export default function RequestInterview() {
  const navigate  = useNavigate()
  const { user } = useAuth()
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
    if (form.scheduled_at && new Date(form.scheduled_at) <= new Date()) {
      toast.error('Interview must be scheduled for a future date and time')
      return
    }
    setLoading(true)
    try {
      // Demo: we use placeholder UUIDs — in production these come from org/candidate lookup
      const payload = {
        title: form.title,
        job_role: form.job_role,
        candidate_email: form.candidate_email,
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

        {user?.approval_status !== 'APPROVED' ? (
          <div className="card shadow-card-hover text-center py-10 px-6">
            <span className="text-4xl mb-4 block">⏳</span>
            <h2 className="font-display text-2xl text-forest-900 mb-2">Verification Required</h2>
            <p className="text-forest-600 text-sm max-w-md mx-auto mb-6">
              Your recruiter account is currently awaiting admin verification. You will be able to create interviews once your account is approved.
            </p>
            <button onClick={() => navigate('/recruiter/dashboard')} className="btn-primary">
              Return to Dashboard
            </button>
          </div>
        ) : (
          <div className="card shadow-card-hover">
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
                  <label className="label">Target job role</label>
                  <input className="input" placeholder="e.g. Backend Engineer, Core Platforms"
                    value={form.job_role} onChange={e => setForm(f => ({ ...f, job_role: e.target.value }))} />
                </div>

                <div>
                  <label className="label font-semibold text-forest-900 mb-2 block">Required Tech Stack / Skills</label>
                  <div className="flex flex-wrap gap-2 p-3 bg-cream-50/50 border border-cream-200 rounded-xl">
                    {TECH_PROFILES.map(skill => {
                      const selected = form.tech_stack.includes(skill);
                      return (
                        <button
                          key={skill}
                          type="button"
                          onClick={() => toggle(skill)}
                          className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                            selected
                              ? 'bg-forest-900 text-white border-forest-900 shadow-sm'
                              : 'bg-white text-forest-700 border-cream-300 hover:border-forest-400'
                          }`}
                        >
                          {skill}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="label">Candidate email *</label>
                  <input className="input" type="email" placeholder="candidate@example.com"
                    value={form.candidate_email} onChange={e => setForm(f => ({ ...f, candidate_email: e.target.value }))} />
                </div>

                <div>
                  <label className="label">Difficulty level</label>
                  <div className="grid sm:grid-cols-3 gap-3">
                    {DIFFICULTIES.map(d => (
                      <button key={d.v} onClick={() => setForm(f => ({ ...f, difficulty: d.v }))}
                        className={`p-3 rounded-xl border text-left transition-all ${
                          form.difficulty === d.v
                            ? 'border-forest-900 bg-forest-50 ring-2 ring-forest-950/10'
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
                  <label className="label">Scheduled Time (Optional)</label>
                  <input className="input" type="datetime-local"
                    min={new Date().toISOString().slice(0, 16)}
                    value={form.scheduled_at} onChange={e => setForm(f => ({ ...f, scheduled_at: e.target.value }))} />
                </div>

                <div>
                  <label className="label">Timezone</label>
                  <input className="input bg-cream-50" readOnly value={form.timezone} />
                </div>
              </div>
            )}

            {/* Step 2: Review & Submit */}
            {step === 2 && (
              <div className="space-y-5 animate-fade-in">
                <h2 className="font-display text-xl text-forest-900">Review & Submit</h2>

                <div className="border border-cream-200 rounded-xl divide-y divide-cream-100 bg-cream-50/50">
                  <div className="p-4 flex justify-between gap-4">
                    <span className="text-forest-500 text-sm">Title</span>
                    <span className="font-semibold text-forest-900 text-sm text-right">{form.title}</span>
                  </div>
                  <div className="p-4 flex justify-between gap-4">
                    <span className="text-forest-500 text-sm">Role</span>
                    <span className="font-semibold text-forest-900 text-sm text-right">{form.job_role || 'Not specified'}</span>
                  </div>
                  <div className="p-4 flex justify-between gap-4">
                    <span className="text-forest-500 text-sm">Required Tech Stack</span>
                    <span className="font-semibold text-forest-900 text-sm text-right">
                      {form.tech_stack.length > 0 ? form.tech_stack.join(', ') : 'None specified'}
                    </span>
                  </div>
                  <div className="p-4 flex justify-between gap-4">
                    <span className="text-forest-500 text-sm">Candidate</span>
                    <span className="font-semibold text-forest-900 text-sm text-right font-mono">{form.candidate_email}</span>
                  </div>
                  <div className="p-4 flex justify-between gap-4">
                    <span className="text-forest-500 text-sm">Difficulty</span>
                    <span className="font-semibold text-forest-900 text-sm text-right capitalize">{form.difficulty}</span>
                  </div>
                  <div className="p-4 flex justify-between gap-4">
                    <span className="text-forest-500 text-sm">Duration</span>
                    <span className="font-semibold text-forest-900 text-sm text-right">{form.duration_mins} mins</span>
                  </div>
                  <div className="p-4 flex justify-between gap-4">
                    <span className="text-forest-500 text-sm">Schedule</span>
                    <span className="font-semibold text-forest-900 text-sm text-right">
                      {form.scheduled_at ? new Date(form.scheduled_at).toLocaleString() : 'Arrange later'}
                    </span>
                  </div>
                </div>

                <div className="p-4 bg-forest-50/50 border border-forest-100 rounded-xl">
                  <p className="text-xs text-forest-600 leading-relaxed">
                    By submitting this request, you authorize TalentForge to reach out to the candidate and assign an approved interviewer.
                  </p>
                </div>
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
        )}
      </div>
    </DashboardLayout>
  )
}
