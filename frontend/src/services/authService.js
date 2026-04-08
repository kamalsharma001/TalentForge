import api from './api'

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

  async getMe() {
    const res = await api.get('/auth/me')
    return res.data
  },

  async logout() {
    try { await api.post('/auth/logout') } catch {}
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
