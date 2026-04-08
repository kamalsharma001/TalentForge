import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

const ROLES = [
  { value: 'recruiter',   label: 'Recruiter',   icon: '🏢', desc: 'Request interviews for candidates' },
  { value: 'interviewer', label: 'Interviewer',  icon: '🎙️', desc: 'Conduct expert technical interviews' },
  { value: 'candidate',   label: 'Candidate',    icon: '👤', desc: 'Practice and get evaluated' },
]

const ROLE_DASHBOARDS = {
  admin: '/admin', recruiter: '/recruiter',
  interviewer: '/interviewer', candidate: '/candidate',
}

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()

  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '',
    password: '', role: params.get('role') || 'recruiter',
  })
  const [loading, setLoading] = useState(false)
  const [showPw,  setShowPw]  = useState(false)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      const user = await register(form)
      toast.success(`Account created! Welcome, ${user.first_name}!`)
      navigate(ROLE_DASHBOARDS[user.role] || '/')
    } catch (err) {
      const msg = err?.response?.data?.error || err?.response?.data?.errors?.email?.[0] || 'Registration failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-cream-100 flex items-center justify-center p-6">
      <div className="w-full max-w-lg animate-slide-up">
        <Link to="/" className="flex items-center gap-2 mb-8">
          <div className="w-7 h-7 bg-forest-900 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm font-bold">T</span>
          </div>
          <span className="font-display font-bold text-forest-900 text-lg">TalentForge</span>
        </Link>

        <div className="card shadow-card-hover">
          <h1 className="font-display text-3xl text-forest-900 mb-1">Create your account</h1>
          <p className="text-forest-500 text-sm mb-6">
            Already have one?{' '}
            <Link to="/login" className="text-forest-900 font-semibold hover:underline">Sign in →</Link>
          </p>

          {/* Role selector */}
          <div className="mb-6">
            <label className="label">I am a…</label>
            <div className="grid grid-cols-3 gap-2">
              {ROLES.map(r => (
                <button
                  key={r.value}
                  type="button"
                  onClick={() => set('role', r.value)}
                  className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-sm font-semibold transition-all ${
                    form.role === r.value
                      ? 'border-forest-900 bg-forest-50 text-forest-900'
                      : 'border-cream-300 bg-white text-forest-600 hover:border-forest-400'
                  }`}
                >
                  <span className="text-xl">{r.icon}</span>
                  <span>{r.label}</span>
                  <span className="text-xs font-normal text-forest-400 text-center leading-tight hidden sm:block">
                    {r.desc}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">First name</label>
                <input className="input" placeholder="Jane" value={form.first_name}
                  onChange={e => set('first_name', e.target.value)} required />
              </div>
              <div>
                <label className="label">Last name</label>
                <input className="input" placeholder="Doe" value={form.last_name}
                  onChange={e => set('last_name', e.target.value)} required />
              </div>
            </div>
            <div>
              <label className="label">Work email</label>
              <input className="input" type="email" placeholder="you@company.com" value={form.email}
                onChange={e => set('email', e.target.value)} required autoComplete="email" />
            </div>
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <input
                  className="input pr-10"
                  type={showPw ? 'text' : 'password'}
                  placeholder="Min. 8 characters with uppercase & number"
                  value={form.password}
                  onChange={e => set('password', e.target.value)}
                  required
                />
                <button type="button" onClick={() => setShowPw(p => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-forest-400 text-sm">
                  {showPw ? '🙈' : '👁'}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="btn-primary w-full justify-center py-3.5 text-base mt-2">
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating account…
                </span>
              ) : 'Create account →'}
            </button>
          </form>

          <p className="text-forest-400 text-xs text-center mt-4">
            By registering you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  )
}
