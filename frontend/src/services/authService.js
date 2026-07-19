import api from './api'
import supabase from './supabaseClient'

const authService = {
  async register(data) {
    const res = await api.post('/auth/register', data)
    _saveTokens(res.data)
    return res.data
  },

  async login(email, password) {
    const res = await api.post('/auth/login', { email, password })

    const { access_token, refresh_token } = res.data

    if (access_token) {
      localStorage.setItem("access_token", access_token)
    }

    if (refresh_token) {
      localStorage.setItem("refresh_token", refresh_token)
    }

    return res.data
  },

  // ── Google OAuth (via Supabase Auth) ─────────────────────────────────────
  // Step 0: kick off the redirect to Google. The browser leaves the app
  // here and comes back to /auth/callback once Google + Supabase finish.
  async loginWithGoogle() {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    })
    if (error) throw error
  },

  // Step 1 (called from /auth/callback once Supabase has a session):
  // exchange the Supabase access token for either TalentForge session
  // tokens (existing account) or a "needs_registration" response.
  async oauthGoogleStart(supabaseAccessToken) {
    const res = await api.post('/auth/oauth/google', {
      supabase_access_token: supabaseAccessToken,
    })
    if (res.data?.access_token) {
      _saveTokens(res.data)
    }
    return res.data
  },

  // Step 2 (only when step 1 returned needs_registration): finish
  // account creation with a user-chosen role — same roles offered by
  // the normal registration form, never hardcoded.
  async oauthGoogleComplete(supabaseAccessToken, { role, first_name, last_name, phone }) {
    const res = await api.post('/auth/oauth/google/complete', {
      supabase_access_token: supabaseAccessToken,
      role,
      first_name,
      last_name,
      phone,
    })
    _saveTokens(res.data)
    return res.data
  },

  async getMe() {
    const res = await api.get('/auth/me')
    return res.data
  },

  async logout() {
    try { await api.post('/auth/logout') } catch {}
    try { await supabase.auth.signOut() } catch {}
    localStorage.clear()
  },

  async changePassword(oldPassword, newPassword) {
    const res = await api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return res.data
  },
}

function _saveTokens({ access_token, refresh_token }) {
  if (access_token)  localStorage.setItem('access_token',  access_token)
  if (refresh_token) localStorage.setItem('refresh_token', refresh_token)
}

export default authService
