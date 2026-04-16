import api from './api'

const practiceService = {
  async list(params = {}) {
    const res = await api.get('/practice/', { params })
    return res.data
  },

  async getById(id) {
    const res = await api.get(`/practice/${id}`)
    return res.data
  },

  async create(data) {
    const res = await api.post('/practice/', data)
    return res.data
  },

  async seed() {
    const res = await api.post('/practice/seed')
    return res.data
  },
}

export default practiceService
