import api from './api'

const reportService = {
  async create(interviewId, data) {
    const res = await api.post(`/reports/${interviewId}`, data)
    return res.data
  },

  async getByInterview(interviewId) {
    const res = await api.get(`/reports/${interviewId}`)
    return res.data
  },

  async update(reportId, data) {
    const res = await api.patch(`/reports/${reportId}/edit`, data)
    return res.data
  },

  async publish(reportId) {
    const res = await api.post(`/reports/${reportId}/publish`)
    return res.data
  },

  async generateAI(interviewId) {
    const res = await api.post(`/feedback/${interviewId}/generate`)
    return res.data
  },

  async previewAI(interviewId) {
    const res = await api.get(`/feedback/${interviewId}/preview`)
    return res.data
  },
}

export default reportService
