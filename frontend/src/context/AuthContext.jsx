import { createContext, useContext, useState, useEffect, useCallback } from 'react'
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

  // LOGOUT
  const logout = useCallback(async () => {

    try {
      await authService.logout()
    } catch (err) {
      console.warn("Logout request failed:", err)
    }

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)

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
        refreshUser
      }}
    >
      {children}
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