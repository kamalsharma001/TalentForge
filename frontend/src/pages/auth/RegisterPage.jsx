import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import Logo from '../../components/ui/Logo'
import authService from '../../services/authService'

const ROLES = [
  { value: 'recruiter',   label: 'Recruiter',   icon: '🏢', desc: 'Request interviews for candidates', tagline: 'Find top talent' },
  { value: 'interviewer', label: 'Interviewer',  icon: '🎙️', desc: 'Conduct expert technical interviews', tagline: 'Assess with confidence' },
  { value: 'candidate',   label: 'Candidate',    icon: '👤', desc: 'Practice and get evaluated', tagline: 'Showcase your best' },
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
  const [googleLoading, setGoogleLoading] = useState(false)

  const handleGoogleSignup = async () => {
    if (googleLoading) return
    setGoogleLoading(true)
    try {
      await authService.loginWithGoogle()
    } catch (err) {
      toast.error('Could not start Google sign-in')
      setGoogleLoading(false)
    }
  }

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
    <div className="min-h-screen bg-cream-100 flex">

      {/* ── Left panel — brand / illustration ─────────────────────────── */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-forest-900 flex-col justify-between p-12 overflow-hidden rounded-r-[2.5rem]">

        {/* ambient dotted grid, top-right */}
        <div
          className="absolute top-0 right-0 w-72 h-72 opacity-40 pointer-events-none"
          style={{
            backgroundImage: 'radial-gradient(rgba(255,255,255,0.18) 1px, transparent 1px)',
            backgroundSize: '18px 18px',
            maskImage: 'radial-gradient(circle at top right, black, transparent 70%)',
          }}
        />

        <Link to="/" className="flex items-center animate-fade-in relative z-10">
          <Logo size="sm" tone="onDark" />
        </Link>

        <div className="relative z-10">
          <h2 className="font-display font-extrabold text-5xl leading-[1.1] text-white mb-5 animate-slide-up">
            Build your role.
            <br />
            Shape the <span className="text-amber-400">future</span>.
          </h2>

          <p className="text-forest-200 text-base max-w-sm mb-14 animate-slide-up" style={{ animationDelay: '0.08s' }}>
            Create your account and start building exceptional teams.
          </p>

          {/* Floating role-card illustration */}
          <div className="relative h-64 flex items-center justify-center">

            {/* glow + pulsing rings behind the cards */}
            <div className="absolute w-40 h-40 rounded-full bg-amber-400/20 blur-2xl" />
            <div className="absolute w-56 h-56 rounded-full border border-dashed border-amber-300/25 animate-[spin_30s_linear_infinite]" />
            <div className="absolute w-24 h-24 rounded-2xl bg-cream-50 rotate-45 shadow-[0_0_50px_10px_rgba(251,191,36,0.35)] flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="none" className="w-8 h-8 text-forest-900 -rotate-45" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75l1.75 1.75L15 10M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
            </div>

            {/* Recruiter — back left */}
            <div
              className="absolute left-2 -top-2 w-32 rounded-2xl bg-forest-800/90 border border-forest-600/60 backdrop-blur-sm p-4 shadow-card-hover -rotate-6 animate-slide-up"
              style={{ animationDelay: '0.2s' }}
            >
              <span className="text-2xl">🏢</span>
              <p className="text-white font-semibold text-sm mt-2">Recruiter</p>
              <p className="text-forest-300 text-xs leading-tight">Find top talent</p>
            </div>

            {/* Candidate — back right */}
            <div
              className="absolute right-2 -top-4 w-32 rounded-2xl bg-forest-950/90 border border-forest-700/60 backdrop-blur-sm p-4 shadow-card-hover rotate-6 animate-slide-up"
              style={{ animationDelay: '0.3s' }}
            >
              <span className="text-2xl">👤</span>
              <p className="text-white font-semibold text-sm mt-2">Candidate</p>
              <p className="text-forest-300 text-xs leading-tight">Showcase your best</p>
            </div>

            {/* Interviewer — front & centre */}
            <div
              className="absolute w-36 rounded-2xl bg-forest-800 border border-amber-400/30 p-4 shadow-card-hover animate-slide-up"
              style={{ animationDelay: '0.12s' }}
            >
              <span className="text-2xl">🎙️</span>
              <p className="text-white font-semibold text-sm mt-2">Interviewer</p>
              <p className="text-forest-300 text-xs leading-tight">Assess with confidence</p>
            </div>

            {/* scattered accent dots */}
            <span className="absolute left-8 bottom-2 w-1.5 h-1.5 rounded-full bg-amber-300/70" />
            <span className="absolute right-10 top-1 w-1 h-1 rounded-full bg-amber-300/50" />
            <span className="absolute right-1/3 bottom-0 w-1 h-1 rounded-full bg-amber-300/60" />
          </div>
        </div>

        <div className="flex items-center gap-2 text-forest-400 text-xs relative z-10">
          <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4 text-forest-400" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Your data is secure with us. We never share your information.</span>
        </div>
      </div>

      {/* ── Right panel — form ─────────────────────────────────────────── */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-lg animate-slide-up">

          <Link to="/" className="flex items-center justify-center mb-6 lg:hidden">
            <Logo size="sm" />
          </Link>

          <div className="relative">
            {/* floating seal badge, overlapping the top edge of the card */}
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 z-10 w-12 h-12 rounded-2xl bg-forest-900 shadow-btn flex items-center justify-center animate-[slideUp_0.5s_ease-out]">
              <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6 text-white" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <div className="card shadow-card-hover pt-10">
              <h1 className="font-display text-3xl text-forest-900 mb-1 text-center">Create your account</h1>
              <p className="text-forest-500 text-sm mb-6 text-center">
                Already have one?{' '}
                <Link to="/login" className="text-forest-900 font-semibold hover:underline">Sign in →</Link>
              </p>

              {/* Decorative step indicator (this form collects everything on one page,
                  the three labels below just narrate what's coming) */}
              <div className="flex items-center justify-center gap-2 mb-7 text-xs font-semibold text-forest-400 select-none">
                <span className="flex items-center gap-1.5 text-forest-900">
                  <span className="w-5 h-5 rounded-full bg-forest-900 text-white flex items-center justify-center text-[11px]">1</span>
                  Tell us who you are
                </span>
                <span className="w-6 h-px bg-cream-300" />
                <span className="flex items-center gap-1.5">
                  <span className="w-5 h-5 rounded-full border border-cream-300 flex items-center justify-center text-[11px]">2</span>
                  Your details
                </span>
                <span className="w-6 h-px bg-cream-300" />
                <span className="flex items-center gap-1.5">
                  <span className="w-5 h-5 rounded-full border border-cream-300 flex items-center justify-center text-[11px]">3</span>
                  Secure it
                </span>
              </div>

              {/* Role selector */}
              <div className="mb-6">
                <label className="label">I am a…</label>
                <div className="grid grid-cols-3 gap-2">
                  {ROLES.map(r => (
                    <button
                      key={r.value}
                      type="button"
                      onClick={() => set('role', r.value)}
                      className={`relative flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-sm font-semibold transition-all ${
                        form.role === r.value
                          ? 'border-forest-900 bg-forest-50 text-forest-900'
                          : 'border-cream-300 bg-white text-forest-600 hover:border-forest-400'
                      }`}
                    >
                      {form.role === r.value && (
                        <span className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-forest-900 flex items-center justify-center">
                          <svg viewBox="0 0 24 24" fill="none" className="w-2.5 h-2.5 text-white" stroke="currentColor" strokeWidth="3">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        </span>
                      )}
                      <span className="text-xl">{r.icon}</span>
                      <span>{r.label}</span>
                      <span className="text-xs font-normal text-forest-400 text-center leading-tight hidden sm:block">
                        {r.desc}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              <p className="text-xs font-semibold text-forest-400 uppercase tracking-wide mb-3">Let's get to know you</p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">First name</label>
                    <div className="relative">
                      <svg viewBox="0 0 24 24" fill="none" className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-forest-400" stroke="currentColor" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <input className="input pl-10" placeholder="Jane" value={form.first_name}
                        onChange={e => set('first_name', e.target.value)} required />
                    </div>
                  </div>
                  <div>
                    <label className="label">Last name</label>
                    <div className="relative">
                      <svg viewBox="0 0 24 24" fill="none" className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-forest-400" stroke="currentColor" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <input className="input pl-10" placeholder="Doe" value={form.last_name}
                        onChange={e => set('last_name', e.target.value)} required />
                    </div>
                  </div>
                </div>
                <div>
                  <label className="label">Work email</label>
                  <div className="relative">
                    <svg viewBox="0 0 24 24" fill="none" className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-forest-400" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <input className="input pl-10" type="email" placeholder="you@company.com" value={form.email}
                      onChange={e => set('email', e.target.value)} required autoComplete="email" />
                  </div>
                </div>
                <div>
                  <label className="label">Password</label>
                  <div className="relative">
                    <svg viewBox="0 0 24 24" fill="none" className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-forest-400" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    <input
                      className="input pl-10 pr-10"
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
                  ) : <>Create account <span aria-hidden="true">→</span></>}
                </button>
              </form>

              {/* Google OAuth */}
              <div className="flex items-center gap-3 my-6">
                <div className="flex-1 h-px bg-cream-300" />
                <span className="text-xs text-forest-400 font-semibold">OR</span>
                <div className="flex-1 h-px bg-cream-300" />
              </div>

              <button
                type="button"
                onClick={handleGoogleSignup}
                disabled={googleLoading}
                className="btn-secondary w-full justify-center"
              >
                <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
                  <path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.9c1.7-1.57 2.7-3.88 2.7-6.62z"/>
                  <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.9-2.26c-.8.54-1.84.86-3.06.86-2.35 0-4.34-1.59-5.05-3.72H.98v2.33A9 9 0 0 0 9 18z"/>
                  <path fill="#FBBC05" d="M3.95 10.7A5.4 5.4 0 0 1 3.67 9c0-.59.1-1.16.28-1.7V4.97H.98A9 9 0 0 0 0 9c0 1.45.35 2.83.98 4.03z"/>
                  <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.46 3.44 1.35l2.58-2.58C13.46.89 11.43 0 9 0A9 9 0 0 0 .98 4.97L3.95 7.3C4.66 5.17 6.65 3.58 9 3.58z"/>
                </svg>
                {googleLoading ? 'Redirecting...' : 'Continue with Google'}
              </button>

              <p className="text-forest-400 text-xs text-center mt-4">
                By registering you agree to our Terms of Service and Privacy Policy.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
