import api from './api'

export const notificationService = {
  async list(params = {}) {
    const res = await api.get('/notifications/', { params })
    return res.data
  },

  async unreadCount() {
    const res = await api.get('/notifications/unread-count')
    return res.data.unread_count
  },

  async markRead(id) {
    const res = await api.patch(`/notifications/${id}/read`)
    return res.data
  },

  async markAllRead() {
    const res = await api.post('/notifications/mark-all-read')
    return res.data
  },
}

export const userService = {
  async getMe() {
    const res = await api.get('/users/me')
    return res.data
  },

  async updateMe(data) {
    const res = await api.patch('/users/me', data)
    return res.data
  },

  async listUsers(params = {}) {
    const res = await api.get('/users/', { params })
    return res.data
  },

  async listInterviewers(params = {}) {
    const res = await api.get('/users/interviewers', { params })
    return res.data
  },

  async approveInterviewer(id) {
    const res = await api.patch(`/users/interviewers/${id}/approve`)
    return res.data
  },

  async deactivate(id) {
    const res = await api.patch(`/users/${id}/deactivate`)
    return res.data
  },
}
