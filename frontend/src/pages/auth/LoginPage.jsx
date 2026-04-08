import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

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

  return (
    <div className="min-h-screen bg-cream-100 flex">

      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-forest-900 flex-col justify-between p-12">

        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">T</span>
          </div>
          <span className="font-bold text-white text-xl">TalentForge</span>
        </Link>

        <div>
          <h2 className="text-4xl text-white mb-4">
            Welcome back to the platform
          </h2>

          <p className="text-forest-200">
            Continue managing interviews and reviewing reports.
          </p>
        </div>

        <p className="text-forest-400 text-xs">
          © {new Date().getFullYear()} TalentForge
        </p>

      </div>

      {/* Right Panel */}
      <div className="flex-1 flex items-center justify-center p-6">

        <div className="w-full max-w-md">

          <h1 className="text-3xl text-forest-900 mb-2">
            Sign in
          </h1>

          <form onSubmit={handleSubmit} className="space-y-5">

            <div>
              <label>Email</label>
              <input
                type="email"
                className="input"
                placeholder="you@company.com"
                value={form.email}
                onChange={(e) =>
                  setForm({ ...form, email: e.target.value })
                }
                required
              />
            </div>

            <div>
              <label>Password</label>

              <div className="relative">

                <input
                  type={showPw ? "text" : "password"}
                  className="input pr-10"
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
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >

              {loading ? "Signing in..." : "Sign in"}

            </button>

          </form>

          {/* Demo accounts */}
          <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl">
            <p className="text-xs font-semibold text-amber-700 mb-2">Demo accounts</p>

            <div className="space-y-1 text-xs text-amber-600 font-mono">
              <p>admin@gmail.com.dev / Admin@123</p>
              <p>recruiter123@gmail.com / Recruiter@123</p>
              <p>interviewer123@gmail.com / Interviewer@123</p>
              <p>candidate123@gmail.com / Candidate@123</p>
            </div>
          </div>

        </div>

      </div>

    </div>
  )
}