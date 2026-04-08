import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function PublicNav() {

  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const ROLE_DASHBOARDS = {
    admin: '/admin/dashboard',
    recruiter: '/recruiter/dashboard',
    interviewer: '/interviewer/dashboard',
    candidate: '/candidate/dashboard',
  }

  // normalize backend role
  const getRole = () => {
    if (!user) return null

    let role = user.role

    if (role && role.includes(".")) {
      role = role.split(".")[1]
    }

    return role
  }

  const role = getRole()

  return (
    <nav className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-cream-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-forest-900 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">T</span>
          </div>
          <span className="font-display font-bold text-forest-900 text-xl">
            TalentForge
          </span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-8">

          {/* How it Works */}
          <div className="relative group">
            <Link to="/#how-it-works" className="nav-link">
              How it Works
            </Link>

            <div className="absolute top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition duration-200 pointer-events-none group-hover:pointer-events-auto">
              <div className="w-56 bg-white shadow-lg border rounded-xl p-3 text-sm text-gray-600">
                Learn how TalentForge helps companies outsource technical interviews efficiently.
              </div>
            </div>
          </div>

          {/* For Recruiters */}
          <div className="relative group">
            <Link to="/#for-recruiters" className="nav-link">
              For Recruiters
            </Link>

            <div className="absolute top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition duration-200">
              <div className="w-56 bg-white shadow-lg border rounded-xl p-3 text-sm text-gray-600">
                Save engineering time by outsourcing technical screening to experts.
              </div>
            </div>
          </div>

          {/* For Interviewers */}
          <div className="relative group">
            <Link to="/#for-interviewers" className="nav-link">
              For Interviewers
            </Link>

            <div className="absolute top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition duration-200">
              <div className="w-56 bg-white shadow-lg border rounded-xl p-3 text-sm text-gray-600">
                Conduct paid technical interviews and help companies hire better engineers.
              </div>
            </div>
          </div>

        </div>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-3">

          {user ? (
            <>
              <Link
                to={ROLE_DASHBOARDS[role] || '/'}
                className="btn-ghost text-sm"
              >
                Dashboard
              </Link>

              <button
                onClick={handleLogout}
                className="btn-secondary text-sm py-2 px-4"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-ghost">
                Login
              </Link>

              <Link
                to="/register"
                className="btn-primary py-2.5 px-5"
              >
                Get started →
              </Link>
            </>
          )}

        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden p-2 rounded-lg hover:bg-cream-100"
          onClick={() => setMobileOpen(o => !o)}
        >
          ☰
        </button>

      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-cream-200 bg-white px-6 py-4 space-y-3">

          <Link to="/#how-it-works" className="block py-2">
            How it Works
          </Link>

          <Link to="/#for-recruiters" className="block py-2">
            For Recruiters
          </Link>

          {user ? (
            <Link
              to={ROLE_DASHBOARDS[role] || '/'}
              className="btn-primary w-full justify-center"
            >
              Dashboard
            </Link>
          ) : (
            <Link
              to="/register"
              className="btn-primary w-full justify-center"
            >
              Get started →
            </Link>
          )}

        </div>
      )}

    </nav>
  )
}