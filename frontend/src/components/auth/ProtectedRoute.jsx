import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const ROLE_DASHBOARDS = {
  admin: '/admin',
  recruiter: '/recruiter',
  interviewer: '/interviewer',
  candidate: '/candidate',
}

export default function ProtectedRoute({ children, roles }) {

  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // 🔴 Normalize role
  let role = user.role

  if (role && role.includes(".")) {
    role = role.split(".")[1]
  }

  console.log("ProtectedRoute role:", role)

  if (roles && !roles.includes(role)) {
    const dashboard = ROLE_DASHBOARDS[role] || '/'
    return <Navigate to={dashboard} replace />
  }

  return children
}