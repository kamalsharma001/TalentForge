import api from './api'

const mockInterviewService = {
  async create(data) {
    const res = await api.post('/mock-interviews/', data)
    return res.data
  },

  async list(params = {}) {
    const res = await api.get('/mock-interviews/', { params })
    return res.data
  },

  async getById(id) {
    const res = await api.get(`/mock-interviews/${id}`)
    return res.data
  },

  async submit(id, answerText) {
    const res = await api.post(`/mock-interviews/${id}/submit`, { answer_text: answerText })
    return res.data
  },

  async generateFeedback(id) {
    const res = await api.post(`/mock-interviews/${id}/feedback`)
    return res.data
  },
}

export default mockInterviewService
