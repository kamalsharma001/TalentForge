import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import authService from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {

  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const handleAuthLogout = () => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
    }
    window.addEventListener('auth-logout', handleAuthLogout)
    return () => window.removeEventListener('auth-logout', handleAuthLogout)
  }, [])

  // Restore session on page refresh
  useEffect(() => {

    const token = localStorage.getItem('access_token')

    if (!token) {
      setLoading(false)
      return
    }

    authService.getMe()
      .then((u) => {
        setUser(u)
      })
      .catch((err) => {

        console.error("Session restore failed:", err)

        if (err?.response?.status === 401) {
          console.warn("Access token expired, interceptor will try refresh")
        }

      })
      .finally(() => {
        setLoading(false)
      })

  }, [])

  // LOGIN
  const login = useCallback(async (email, password) => {

    const data = await authService.login(email, password)

    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }

    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token)
    }

    setUser(data.user)
    setLoading(false)

    return data.user

  }, [])

  // REGISTER
  const register = useCallback(async (payload) => {

    const data = await authService.register(payload)

    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }

    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token)
    }

    setUser(data.user)
    setLoading(false)

    return data.user

  }, [])

  // Used after a successful Google OAuth exchange (see AuthCallbackPage) —
  // the backend has already returned the same {access_token, refresh_token,
  // user} shape as login()/register(), this just applies it to app state.
  const setSessionFromAuthPayload = useCallback((data) => {
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token)
    }
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token)
    }
    setUser(data.user)
    setLoading(false)
    return data.user
  }, [])

  const [loggingOut, setLoggingOut] = useState(false)

  // LOGOUT
  const logout = useCallback(async () => {
    setLoggingOut(true)

    try {
      await authService.logout()
    } catch (err) {
      console.warn("Logout request failed:", err)
    }

    // Brief 800ms delay for visual feedback before navigation
    setTimeout(() => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      setLoggingOut(false)
    }, 800)
  }, [])

  // Manual refresh user
  const refreshUser = useCallback(async () => {

    const u = await authService.getMe()
    setUser(u)

    return u

  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        refreshUser,
        setSessionFromAuthPayload,
        loggingOut
      }}
    >
      {children}
      {loggingOut && (
        <div className="fixed inset-0 bg-cream-100/80 backdrop-blur-sm z-[9999] flex flex-col items-center justify-center gap-3 select-none animate-[fadeIn_0.2s_ease-out]">
          {/* Minimal lock icon */}
          <svg className="w-8 h-8 text-forest-900 animate-[pulse_1.5s_infinite]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <span className="text-sm font-semibold text-forest-900 tracking-wide">Signing out...</span>
        </div>
      )}
    </AuthContext.Provider>
  )
}

export function useAuth() {

  const ctx = useContext(AuthContext)

  if (!ctx) {
    throw new Error('useAuth must be used inside AuthProvider')
  }

  return ctx

}