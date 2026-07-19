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
        redirectToDashboard(user)
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
      toast.success(`Account created! Welcome, ${user.first_name}!`)
      redirectToDashboard(user)
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Could not finish signing up')
    } finally {
      setSubmitting(false)
    }
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-cream-100 flex items-center justify-center p-6">
        <div className="text-forest-700 font-sans">Signing you in with Google…</div>
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
