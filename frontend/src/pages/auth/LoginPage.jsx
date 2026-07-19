import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import Logo from '../../components/ui/Logo'
import authService from '../../services/authService'

const ROLE_DASHBOARDS = {
  admin: '/admin',
  recruiter: '/recruiter',
  interviewer: '/interviewer',
  candidate: '/candidate',
}

export default function LoginPage() {

  const { login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [showPw, setShowPw] = useState(false)

  const handleSubmit = async (e) => {

  e.preventDefault()

  if (loading) return

  setLoading(true)

  try {

    const user = await login(form.email, form.password)

    let role = user?.role

    if (role && role.includes(".")) {
      role = role.split(".")[1]
    }

    toast.success(`Welcome back, ${user.first_name}!`)

    // DIRECT REDIRECT
    if (role === "candidate") {
      navigate("/candidate", { replace: true })
    }

    else if (role === "recruiter") {
      navigate("/recruiter", { replace: true })
    }

    else if (role === "interviewer") {
      navigate("/interviewer", { replace: true })
    }

    else if (role === "admin") {
      navigate("/admin", { replace: true })
    }

    else {
      navigate("/", { replace: true })
    }

  } catch (err) {

    toast.error(err?.response?.data?.error || "Invalid email or password")

  } finally {

    setLoading(false)

  }
}

const [googleLoading, setGoogleLoading] = useState(false)

const handleGoogleLogin = async () => {
  if (googleLoading) return
  setGoogleLoading(true)
  try {
    await authService.loginWithGoogle()
    // Browser now redirects to Google; nothing else to do here.
  } catch (err) {
    toast.error('Could not start Google sign-in')
    setGoogleLoading(false)
  }
}

  return (
    <div className="min-h-screen bg-cream-100 flex">

      {/* ── Left panel — brand / product illustration ─────────────────── */}
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
          <span
            className="badge bg-forest-800 text-amber-300 border border-amber-400/20 mb-5 animate-slide-up"
          >
            ✨ All-in-one Interview Platform
          </span>

          <h2 className="font-display font-extrabold text-5xl leading-[1.1] text-white mb-5 animate-slide-up" style={{ animationDelay: '0.05s' }}>
            Great teams
            <br />
            are <span className="text-amber-400">forged</span>
            <br />
            here.
          </h2>

          <p className="text-forest-200 text-base max-w-sm mb-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            Manage interviews, evaluate candidates and make better hiring decisions.
          </p>

          <div className="flex items-center gap-2 mb-10 animate-slide-up" style={{ animationDelay: '0.15s' }}>
            {[
              { icon: 'M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-1.13a4 4 0 10-4-4 4 4 0 004 4zm6-4a4 4 0 11-8 0 4 4 0 018 0z', label: 'Manage Interviews' },
              { icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', label: 'Review Reports' },
              { icon: 'M9 19V6l8-2v13M9 19c0 1.105-1.79 2-4 2s-4-.895-4-2 1.79-2 4-2 4 .895 4 2zm8-2c0 1.105-1.79 2-4 2s-4-.895-4-2 1.79-2 4-2 4 .895 4 2zM9 10l8-2', label: 'Track Performance' },
            ].map((chip) => (
              <span key={chip.label} className="flex items-center gap-1.5 bg-white/5 border border-white/10 rounded-full pl-2 pr-3 py-1.5">
                <span className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center">
                  <svg viewBox="0 0 24 24" fill="none" className="w-3.5 h-3.5 text-forest-200" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d={chip.icon} />
                  </svg>
                </span>
                <span className="text-forest-200 text-xs font-medium">{chip.label}</span>
              </span>
            ))}
          </div>

          {/* Dashboard mockup illustration */}
          <div className="relative w-full max-w-sm animate-slide-up" style={{ animationDelay: '0.2s' }}>

            {/* potted plant, bottom-left */}
            <svg viewBox="0 0 60 80" className="absolute -left-14 bottom-0 w-14 h-20 opacity-90" aria-hidden="true">
              <path d="M18 78h24l4-26H14z" fill="#1a4538" />
              <path d="M30 52c0-14-16-18-16-32 10 2 16 12 16 20 0-16 10-24 20-26-2 16-8 24-20 30z" fill="#52a285" />
            </svg>

            <div className="rounded-2xl bg-forest-800/80 border border-forest-600/50 backdrop-blur-sm p-3 shadow-card-hover">
              <div className="flex items-center gap-1.5 mb-3">
                <span className="w-2 h-2 rounded-full bg-red-400/70" />
                <span className="w-2 h-2 rounded-full bg-amber-300/70" />
                <span className="w-2 h-2 rounded-full bg-forest-300/70" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="col-span-2 bg-forest-900/60 rounded-lg p-2 h-16 flex items-end">
                  <svg viewBox="0 0 100 30" className="w-full h-full" preserveAspectRatio="none">
                    <polyline points="0,24 15,18 30,20 45,8 60,14 75,4 100,10" fill="none" stroke="#fbbf24" strokeWidth="2.5" />
                  </svg>
                </div>
                <div className="bg-forest-900/60 rounded-lg p-2 h-14 flex items-center justify-center">
                  <div
                    className="w-8 h-8 rounded-full"
                    style={{ background: 'conic-gradient(#fbbf24 0% 65%, #318669 65% 100%)' }}
                  />
                </div>
                <div className="bg-forest-900/60 rounded-lg p-2 h-14 space-y-1.5 flex flex-col justify-center">
                  <span className="block w-full h-1.5 rounded-full bg-forest-600/70" />
                  <span className="block w-2/3 h-1.5 rounded-full bg-forest-600/70" />
                  <span className="block w-4/5 h-1.5 rounded-full bg-forest-600/70" />
                </div>
              </div>
            </div>

            {/* floating stat card */}
            <div className="absolute -right-6 -bottom-6 w-40 bg-cream-50 rounded-xl p-3 shadow-card-hover animate-[bounce_4s_ease-in-out_infinite]">
              <p className="text-forest-500 text-[11px] leading-tight">Interview<br />Success Rate</p>
              <p className="font-display font-extrabold text-2xl text-forest-900">87%</p>
              <svg viewBox="0 0 60 20" className="w-full h-4 mt-1">
                <polyline points="0,16 12,10 24,13 36,4 48,8 60,2" fill="none" stroke="#f59e0b" strokeWidth="2" />
              </svg>
            </div>
          </div>
        </div>

        <p className="text-forest-400 text-xs relative z-10">
          © {new Date().getFullYear()} TalentForge. All rights reserved.
        </p>
      </div>

      {/* ── Right panel — form ─────────────────────────────────────────── */}
      <div className="flex-1 flex items-center justify-center p-6">

        <div className="w-full max-w-md animate-slide-up">

          <Link to="/" className="flex items-center justify-center mb-6 lg:hidden">
            <Logo size="sm" />
          </Link>

          <div className="relative">
            {/* floating seal badge, overlapping the top edge of the card */}
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 z-10 w-14 h-14 rounded-full bg-cream-50 shadow-card-hover flex items-center justify-center">
              <span className="w-10 h-10 rounded-full bg-forest-900 flex items-center justify-center">
                <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-white" stroke="currentColor" strokeWidth="2.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5 1c0 4.5-3.5 8.25-8 9.5-4.5-1.25-8-5-8-9.5V6l8-3 8 3v5z" />
                </svg>
              </span>
            </div>

            <div className="card shadow-card-hover pt-10 text-center">
              <h1 className="font-display text-3xl text-forest-900 mb-1">
                Welcome back <span aria-hidden="true">👋</span>
              </h1>
              <p className="text-forest-500 text-sm mb-7">Sign in to continue</p>

              <form onSubmit={handleSubmit} className="space-y-5 text-left">

                <div>
                  <label className="label">Email address</label>
                  <div className="relative">
                    <svg viewBox="0 0 24 24" fill="none" className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-forest-400" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <input
                      type="email"
                      className="input pl-10"
                      placeholder="you@company.com"
                      value={form.email}
                      onChange={(e) =>
                        setForm({ ...form, email: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="label">Password</label>

                  <div className="relative">
                    <svg viewBox="0 0 24 24" fill="none" className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-forest-400" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>

                    <input
                      type={showPw ? "text" : "password"}
                      className="input pl-10 pr-10"
                      placeholder="Your password"
                      value={form.password}
                      onChange={(e) =>
                        setForm({ ...form, password: e.target.value })
                      }
                      required
                    />

                    <button
                      type="button"
                      onClick={() => setShowPw(!showPw)}
                      className="absolute right-3 top-1/2 -translate-y-1/2"
                    >
                      {showPw ? "🙈" : "👁"}
                    </button>

                  </div>

                  <div className="text-right mt-1.5">
                    <button
                      type="button"
                      onClick={() => toast('Contact your admin to reset your password.')}
                      className="text-forest-700 text-xs font-semibold hover:underline"
                    >
                      Forgot password?
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full justify-center py-3.5 text-base"
                >

                  {loading ? "Signing in..." : <>Sign in <span aria-hidden="true">→</span></>}

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
                onClick={handleGoogleLogin}
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

              {/* Demo accounts */}
              <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl text-left">
                <p className="text-xs font-semibold text-amber-700 mb-2">Demo accounts</p>

                <div className="space-y-1 text-xs text-amber-600 font-mono">
                  <p>admin@gmail.com / Admin@123</p>
                  <p>recruiter123@gmail.com / Recruiter@123</p>
                  <p>interviewer123@gmail.com / Interviewer@123</p>
                  <p>candidate123@gmail.com / Candidate@123</p>
                </div>
              </div>

              <p className="text-forest-500 text-sm mt-6">
                Don't have an account?{' '}
                <Link to="/register" className="text-forest-900 font-semibold hover:underline">Sign up →</Link>
              </p>
            </div>
          </div>

        </div>

      </div>

    </div>
  )
}
