import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const ROLE_DASHBOARDS = {
  admin: '/admin', recruiter: '/recruiter',
  interviewer: '/interviewer', candidate: '/candidate',
}

export default function NotFoundPage() {
  const { user }   = useAuth()
  const navigate   = useNavigate()
  const dashboard  = user ? ROLE_DASHBOARDS[user.role] : '/'

  return (
    <div className="min-h-screen bg-cream-100 flex items-center justify-center p-6">
      <div className="text-center max-w-md animate-slide-up">

        {/* Big 404 */}
        <div className="relative mb-8">
          <span className="font-display text-[9rem] leading-none font-bold text-cream-300 select-none">
            404
          </span>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-5xl">🔍</span>
          </div>
        </div>

        <h1 className="font-display text-3xl text-forest-900 mb-3">
          Page not found
        </h1>
        <p className="text-forest-500 font-sans text-base leading-relaxed mb-8">
          The page you're looking for doesn't exist, or you may not have permission to view it.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={() => navigate(-1)}
            className="btn-secondary"
          >
            ← Go back
          </button>
          <Link
            to={dashboard}
            className="btn-primary"
          >
            {user ? 'Go to Dashboard' : 'Go Home'} →
          </Link>
        </div>
      </div>
    </div>
  )
}
