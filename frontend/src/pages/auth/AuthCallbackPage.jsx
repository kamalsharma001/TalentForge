import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import supabase from '../../services/supabaseClient'
import authService from '../../services/authService'
import { useAuth } from '../../context/AuthContext'
import Logo from '../../components/ui/Logo'

const ROLE_DASHBOARDS = {
  admin: '/admin',
  recruiter: '/recruiter',
  interviewer: '/interviewer',
  candidate: '/candidate',
}

const ROLES = [
  { value: 'recruiter',   label: 'Recruiter',   icon: '🏢', desc: 'Request interviews for candidates' },
  { value: 'interviewer', label: 'Interviewer',  icon: '🎙️', desc: 'Conduct expert technical interviews' },
  { value: 'candidate',   label: 'Candidate',    icon: '👤', desc: 'Practice and get evaluated' },
]

function normalizeRole(role) {
  if (role && role.includes('.')) return role.split('.')[1]
  return role
}

export default function AuthCallbackPage() {
  const navigate = useNavigate()
  const { setSessionFromAuthPayload } = useAuth()

  const [status, setStatus] = useState('loading') // loading | needs_registration | error
  const [pendingProfile, setPendingProfile] = useState(null)
  const [supabaseToken, setSupabaseToken] = useState(null)
  const [role, setRole] = useState('candidate')
  const [submitting, setSubmitting] = useState(false)

  const redirectToDashboard = (user) => {
    const cleanRole = normalizeRole(user?.role)
    toast.success(`Welcome, ${user?.first_name || 'there'}!`)
    navigate(ROLE_DASHBOARDS[cleanRole] || '/', { replace: true })
  }

  useEffect(() => {
    let cancelled = false

    async function run() {
      // Surface an OAuth error the user/Google may have thrown before we
      // even got a session (e.g. they cancelled the Google consent screen).
      const params = new URLSearchParams(window.location.search)
      const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ''))
      const oauthError = params.get('error_description') || hashParams.get('error_description')
      if (oauthError) {
        if (!cancelled) {
          toast.error(oauthError)
          navigate('/login', { replace: true })
        }
        return
      }

      const { data, error } = await supabase.auth.getSession()

      if (cancelled) return

      if (error || !data?.session?.access_token) {
        toast.error('Google sign-in failed. Please try again.')
        navigate('/login', { replace: true })
        return
      }

       const token = data.session.access_token

      try {
        const result = await authService.oauthGoogleStart(token)

        if (cancelled) return

        if (result.needs_registration) {
          setSupabaseToken(token)
          setPendingProfile(result)
          setStatus('needs_registration')
          return
        }

        const user = setSessionFromAuthPayload(result)
        
        // Show success animation before redirect
        setStatus('success')
        setTimeout(() => {
          redirectToDashboard(user)
        }, 1500)
      } catch (err) {
        if (cancelled) return
        toast.error(err?.response?.data?.error || 'Google sign-in failed.')
        navigate('/login', { replace: true })
      }
    }

    run()
    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleCompleteSignup = async (e) => {
    e.preventDefault()
    if (submitting) return
    setSubmitting(true)

    try {
      const result = await authService.oauthGoogleComplete(supabaseToken, {
        role,
        first_name: pendingProfile?.first_name,
        last_name: pendingProfile?.last_name,
      })
      const user = setSessionFromAuthPayload(result)
      
      // Show success animation before redirect
      setStatus('success')
      setTimeout(() => {
        toast.success(`Account created! Welcome, ${user.first_name}!`)
        redirectToDashboard(user)
      }, 1500)
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Could not finish signing up')
      setSubmitting(false)
    }
  }

  if (status === 'loading' || status === 'success') {
    return (
      <div className="min-h-screen bg-cream-100 flex items-center justify-center p-6">
        <div className="w-full max-w-md animate-slide-up relative">
          {/* floating seal badge, overlapping the top edge of the card */}
          <div className="absolute -top-6 left-1/2 -translate-x-1/2 z-30 w-14 h-14 rounded-full bg-cream-50 shadow-card-hover flex items-center justify-center">
            <span className="w-10 h-10 rounded-full bg-forest-900 flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-white" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5 1c0 4.5-3.5 8.25-8 9.5-4.5-1.25-8-5-8-9.5V6l8-3 8 3v5z" />
              </svg>
            </span>
          </div>

          {/* Rotating processing border line */}
          {status === 'loading' && (
            <div className="absolute inset-0 -m-[3px] rounded-[19px] overflow-hidden pointer-events-none z-0">
              <div className="absolute inset-[-50%] bg-[conic-gradient(from_0deg,transparent_30%,#15803d_50%,transparent_70%)] animate-[spin_1.5s_linear_infinite]" />
            </div>
          )}

          <div className="card shadow-card-hover pt-12 pb-10 text-center relative z-10 bg-white overflow-hidden min-h-[300px] flex flex-col items-center justify-center">
            {status === 'success' ? (
              <div className="space-y-4 text-center animate-pop-badge">
                <svg className="w-16 h-16 text-emerald-600 mx-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" className="checkmark-circle-new" />
                  <path d="M8 12l3 3 5-5" className="checkmark-check-new" />
                </svg>
                <div className="space-y-1">
                  <h3 className="text-xl font-bold text-forest-900 font-display">Success</h3>
                  <p className="text-xs text-forest-500">Preparing dashboard...</p>
                </div>
              </div>
            ) : (
              <div className="space-y-5 text-center">
                <div className="w-14 h-14 border-4 border-forest-100 border-t-forest-700 rounded-full animate-spin mx-auto mb-2" />
                <h3 className="text-2xl font-bold text-forest-900 font-display">Verifying Account</h3>
                <p className="text-sm text-forest-500 animate-pulse">Communicating with Google OAuth and loading your TalentForge profile...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // status === 'needs_registration' — first time signing in with this
  // Google account: ask which role they are, exactly like normal signup.
  return (
    <div className="min-h-screen bg-cream-100 flex items-center justify-center p-6">
      <div className="w-full max-w-lg animate-slide-up">
        <div className="flex items-center mb-8">
          <Logo size="sm" />
        </div>

        <div className="card shadow-card-hover">
          <h1 className="font-display text-3xl text-forest-900 mb-1">One last step</h1>
          <p className="text-forest-500 text-sm mb-6">
            Welcome{pendingProfile?.first_name ? `, ${pendingProfile.first_name}` : ''}! Tell us who you are
            so we can set up your account.
          </p>

          <form onSubmit={handleCompleteSignup} className="space-y-5">
            <div className="mb-6">
              <label className="label">I am a…</label>
              <div className="grid grid-cols-3 gap-2">
                {ROLES.map(r => (
                  <button
                    key={r.value}
                    type="button"
                    onClick={() => setRole(r.value)}
                    className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-sm font-semibold transition-all ${
                      role === r.value
                        ? 'border-forest-900 bg-forest-50 text-forest-900'
                        : 'border-cream-300 bg-white text-forest-600 hover:border-forest-400'
                    }`}
                  >
                    <span className="text-xl">{r.icon}</span>
                    {r.label}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="btn-primary w-full justify-center"
            >
              {submitting ? 'Setting up your account...' : 'Continue'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
