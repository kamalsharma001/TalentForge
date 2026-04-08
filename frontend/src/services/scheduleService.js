import api from './api'

const scheduleService = {
  async addSlot(data) {
    const res = await api.post('/scheduling/slots', data)
    return res.data
  },

  async deleteSlot(slotId) {
    const res = await api.delete(`/scheduling/slots/${slotId}`)
    return res.data
  },

  async listSlots(params = {}) {
    const res = await api.get('/scheduling/slots', { params })
    return res.data
  },

  async matchInterviewers({ tech_stack, requested_at, duration_mins }) {
    const res = await api.get('/scheduling/match', {
      params: {
        tech_stack: tech_stack.join(','),
        requested_at,
        duration_mins,
      },
    })
    return res.data
  },
}

export default scheduleService
