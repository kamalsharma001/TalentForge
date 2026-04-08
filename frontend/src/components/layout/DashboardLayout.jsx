import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useNotifications } from '../../hooks'
import { Avatar } from '../ui'

const NAV = {
  admin: [
    { to: '/admin',              icon: '⬛', label: 'Overview'      },
    { to: '/admin/interviews',   icon: '📋', label: 'Interviews'    },
    { to: '/admin/reports',      icon: '📊', label: 'Reports'       },
    { to: '/admin/users',        icon: '👥', label: 'Manage Users'  },
  ],
  recruiter: [
    { to: '/recruiter',          icon: '⬛', label: 'Overview'      },
    { to: '/recruiter/request',  icon: '➕', label: 'New Interview' },
    { to: '/recruiter/interviews',icon: '📋', label: 'Interviews'   },
    { to: '/recruiter/reports',  icon: '📊', label: 'Reports'       },
  ],
  interviewer: [
    { to: '/interviewer',             icon: '⬛', label: 'Overview'      },
    { to: '/interviewer/interviews',  icon: '📋', label: 'My Interviews' },
    { to: '/interviewer/schedule',    icon: '📅', label: 'My Schedule'   },
    { to: '/interviewer/reports',     icon: '📊', label: 'Submit Report' },
  ],
  candidate: [
    { to: '/candidate',          icon: '⬛', label: 'Overview'   },
    { to: '/candidate/interviews',icon: '📋', label: 'Interviews'},
    { to: '/candidate/reports',  icon: '📊', label: 'My Reports' },
    { to: '/candidate/profile',  icon: '👤', label: 'Profile'    },
  ],
}

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth()
  const { unreadCount }  = useNotifications()
  const location  = useLocation()
  const navigate  = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const roleKey = user?.role?.toLowerCase()?.replace('userrole.', '')
  const navItems = NAV[roleKey] || []

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const Sidebar = () => (
    <aside className="flex flex-col h-full bg-white border-r border-cream-200 w-60">
      {/* Logo */}
      <div className="h-16 flex items-center px-5 border-b border-cream-200 flex-shrink-0">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-7 h-7 bg-forest-900 rounded-lg flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4 text-white" stroke="currentColor" strokeWidth="2.5">
              <path d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
            </svg>
          </div>
          <span className="font-display font-bold text-forest-900 text-lg">TalentForge</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 overflow-y-auto">
        <p className="text-forest-400 text-[10px] font-semibold uppercase tracking-widest px-4 mb-2">
          {user?.role}
        </p>
        <div className="space-y-0.5">
          {navItems.map(item => (
            <Link
              key={item.to}
              to={item.to}
              className={`sidebar-link ${location.pathname === item.to ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <span className="text-base leading-none">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </div>

        <div className="divider" />

        <Link
          to={`/${roleKey}/notifications`}
          className={`sidebar-link relative ${location.pathname.includes('notifications') ? 'active' : ''}`}
          onClick={() => setSidebarOpen(false)}
        >
          <span className="text-base">🔔</span>
          <span>Notifications</span>

          {unreadCount > 0 && (
            <span className="ml-auto bg-amber-400 text-forest-900 text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Link>


      </nav>

      {/* User footer */}
      <div className="p-3 border-t border-cream-200">
        <div className="flex items-center gap-3 px-2 py-2">
          <Avatar name={user?.full_name || user?.first_name} url={user?.avatar_url} size="sm" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-forest-900 truncate">{user?.first_name} {user?.last_name}</p>
            <p className="text-xs text-forest-400 capitalize">{user?.role}</p>
          </div>
          <button onClick={handleLogout} title="Log out" className="text-forest-400 hover:text-red-500 transition-colors text-sm">⏻</button>
        </div>
      </div>
    </aside>
  )

  return (
    <div className="flex h-screen overflow-hidden bg-cream-100">
      {/* Desktop sidebar */}
      <div className="hidden md:flex flex-shrink-0">
        <Sidebar />
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div className="flex-shrink-0"><Sidebar /></div>
          <div className="flex-1 bg-forest-950/40 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="h-16 bg-white border-b border-cream-200 flex items-center justify-between px-6 flex-shrink-0">
          <button className="md:hidden p-2 -ml-2 rounded-lg hover:bg-cream-100" onClick={() => setSidebarOpen(true)}>
            <div className="w-5 h-0.5 bg-forest-900 mb-1" />
            <div className="w-5 h-0.5 bg-forest-900 mb-1" />
            <div className="w-5 h-0.5 bg-forest-900" />
          </button>
          <div className="hidden md:block">
            <h1 className="text-forest-400 text-sm font-sans">
              Good {getGreeting()},{' '}
              <span className="text-forest-900 font-semibold">{user?.first_name}</span>
            </h1>
          </div>
          <div className="flex items-center gap-2 ml-auto">
            <Link to={`/${roleKey}/notifications`} className="relative p-2 rounded-full hover:bg-cream-100 transition-colors">
              <span className="text-lg">🔔</span>
              {unreadCount > 0 && (
                <span className="absolute top-0.5 right-0.5 w-4 h-4 bg-amber-400 text-forest-900 text-[10px] font-bold rounded-full flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </Link>
            <Avatar name={user?.full_name || user?.first_name} url={user?.avatar_url} size="sm" />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}
