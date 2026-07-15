import { useEffect, useRef, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useNotifications } from '../../hooks'
import { Avatar } from '../ui'
import Logo from '../ui/Logo'

const NAV = {
  admin: [
    { to: '/admin/dashboard',  icon: '⬛', label: 'Overview'   },
    { to: '/admin/users',      icon: '👥', label: 'Users'      },
    { to: '/admin/interviews', icon: '📋', label: 'Interviews' },
    { to: '/admin/reports',    icon: '📊', label: 'Reports'    },
  ],
  recruiter: [
    { to: '/recruiter/dashboard',  icon: '⬛', label: 'Overview'           },
    { to: '/recruiter/request',    icon: '➕', label: 'Interview Requests' },
    { to: '/recruiter/interviews', icon: '📋', label: 'Candidates'         },
    { to: '/recruiter/reports',    icon: '📊', label: 'Reports'            },
  ],
  interviewer: [
    { to: '/interviewer/dashboard',  icon: '⬛', label: 'Overview'      },
    { to: '/interviewer/interviews', icon: '📋', label: 'My Interviews' },
    { to: '/interviewer/schedule',   icon: '📅', label: 'My Schedule'   },
    { to: '/interviewer/reports',    icon: '📝', label: 'Submit Report' },
  ],
  candidate: [
    { to: '/candidate/dashboard',        icon: '⬛', label: 'Overview'  },
    { to: '/candidate/interviews',       icon: '📋', label: 'My Interviews' },
    { to: '/candidate/reports',          icon: '📊', label: 'Feedback'  },
    { to: '/candidate/profile',          icon: '👤', label: 'Profile'   },
  ],
}

function formatRole(role) {
  if (!role) return ''
  const clean = role.includes('.') ? role.split('.').pop() : role
  return clean.charAt(0).toUpperCase() + clean.slice(1)
}

export default function TopNavbar() {
  const { user, logout } = useAuth()
  const { unreadCount } = useNotifications()
  const location = useLocation()
  const navigate = useNavigate()

  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const dropdownRef = useRef(null)

  const roleKey = user?.role?.toLowerCase()?.replace('userrole.', '')
  const navItems = NAV[roleKey] || []
  const roleLabel = formatRole(user?.role)

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    setMobileOpen(false)
    setDropdownOpen(false)
  }, [location.pathname])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const isActive = (to) => location.pathname === to

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-cream-200">
      <div className="h-16 px-4 sm:px-6 flex items-center gap-4 max-w-[1400px] mx-auto">
        {/* Left — logo + brand */}
        <Link to="/" className="flex items-center flex-shrink-0">
          <Logo size="sm" />
        </Link>

        {/* Center — role nav (desktop) */}
        <nav className="hidden md:flex items-center gap-1 mx-auto">
          {navItems.map(item => (
            <Link
              key={item.to}
              to={item.to}
              className={`relative px-4 py-2 text-sm font-medium font-sans transition-colors duration-200 border-b-2 ${
                isActive(item.to)
                  ? 'text-forest-900 border-forest-900'
                  : 'text-forest-500 border-transparent hover:text-forest-800'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Right — notifications + avatar */}
        <div className="flex items-center gap-1.5 sm:gap-2 ml-auto md:ml-0">
          <Link
            to={`/${roleKey}/notifications`}
            className="relative p-2 rounded-full hover:bg-cream-100 transition-colors duration-150"
            aria-label="Notifications"
          >
            <span className="text-lg">🔔</span>
            {unreadCount > 0 && (
              <span className="absolute top-0.5 right-0.5 min-w-[16px] h-4 px-0.5 bg-amber-400 text-forest-900 text-[10px] font-bold rounded-full flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </Link>

          {/* Avatar + dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(o => !o)}
              className="rounded-full transition-transform duration-150 hover:scale-105"
              aria-haspopup="true"
              aria-expanded={dropdownOpen}
            >
              <Avatar name={user?.full_name || user?.first_name} url={user?.avatar_url} size="sm" />
            </button>

            {dropdownOpen && (
              <div
                className="absolute right-0 mt-2 w-60 bg-white rounded-2xl shadow-card-hover border border-cream-200 py-2 origin-top-right animate-dropdown-in"
              >
                <div className="flex items-center gap-3 px-4 py-3">
                  <Avatar name={user?.full_name || user?.first_name} url={user?.avatar_url} size="md" />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-forest-900 truncate">
                      {user?.full_name || `${user?.first_name || ''} ${user?.last_name || ''}`.trim()}
                    </p>
                    <p className="text-xs text-forest-400">{roleLabel}</p>
                  </div>
                </div>
                <div className="border-t border-cream-200 my-1" />
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-red-500 hover:bg-red-50 transition-colors duration-150"
                >
                  <span>⏻</span> Logout
                </button>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 -mr-1 rounded-lg hover:bg-cream-100"
            onClick={() => setMobileOpen(o => !o)}
            aria-label="Toggle navigation"
          >
            <div className="w-5 h-0.5 bg-forest-900 mb-1 transition-transform" />
            <div className="w-5 h-0.5 bg-forest-900 mb-1" />
            <div className="w-5 h-0.5 bg-forest-900" />
          </button>
        </div>
      </div>

      {/* Mobile nav sheet */}
      {mobileOpen && (
        <nav className="md:hidden border-t border-cream-200 bg-white px-4 py-2 animate-fade-in">
          {navItems.map(item => (
            <Link
              key={item.to}
              to={item.to}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                isActive(item.to) ? 'bg-forest-900 text-white' : 'text-forest-700 hover:bg-cream-100'
              }`}
            >
              <span className="text-base leading-none">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  )
}
