import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import authService from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {

  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

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

    // Delay session clear by 1.2s to show premium signing out animation
    setTimeout(() => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      setLoggingOut(false)
      toast.success("Successfully logged out.")
    }, 1200)
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
        <div className="fixed inset-0 bg-forest-950/90 backdrop-blur-md z-[9999] flex flex-col items-center justify-center text-center p-6 select-none animate-[fadeIn_0.3s_ease-out]">
          <div className="w-full max-w-md space-y-6">
            {/* Spinning loader animation */}
            <div className="relative w-20 h-20 mx-auto">
              {/* Outer rotating forest ring */}
              <div className="absolute inset-0 border-4 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin" />
              {/* Inner counter-rotating amber ring */}
              <div className="absolute inset-2 border-4 border-amber-400/20 border-b-amber-400 rounded-full animate-[spin_1.2s_linear_infinite_reverse]" />
            </div>
            <div className="space-y-2">
              <h3 className="text-3xl font-display font-extrabold text-white">Signing out</h3>
              <p className="text-forest-200 text-sm animate-pulse">Safely clearing your session and workspace...</p>
            </div>
          </div>
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