import api from './api'

const interviewService = {
  async create(data) {
    const res = await api.post('/interviews/', data)
    return res.data
  },

  async list(params = {}) {
    const res = await api.get('/interviews/', { params })
    return res.data
  },

  async getById(id) {
    const res = await api.get(`/interviews/${id}`)
    return res.data
  },

  async update(id, data) {
    const res = await api.patch(`/interviews/${id}`, data)
    return res.data
  },

  async assign(id, { interviewer_id, slot_id }) {
    const res = await api.post(`/interviews/${id}/assign`, { interviewer_id, slot_id })
    return res.data
  },

  async complete(id, data) {
    const res = await api.post(`/interviews/${id}/complete`, data)
    return res.data
  },

  async cancel(id, reason) {
    const res = await api.post(`/interviews/${id}/cancel`, { reason })
    return res.data
  },
}

export default interviewService
