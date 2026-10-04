import api from './api'

const aiPrepService = {
  /**
   * Fetch candidate profile context and upcoming scheduled interviews.
   */
  async getContext() {
    const res = await api.get('/ai-prep/context')
    return res.data
  },

  /**
   * Generate an AI preparation strategy and prioritized focus areas.
   */
  async generatePlan(data) {
    const res = await api.post('/ai-prep/plan', data)
    return res.data
  },

  /**
   * Generate interview practice questions tailored to role and tech stack.
   */
  async generateQuestions(data) {
    const res = await api.post('/ai-prep/questions/generate', data)
    return res.data
  },

  /**
   * Evaluate a candidate's answer to an individual practice question.
   */
  async evaluateAnswer(data) {
    const res = await api.post('/ai-prep/questions/evaluate', data)
    return res.data
  },

  /**
   * Start a live multi-turn AI mock interview session.
   */
  async startMockSession(data) {
    const res = await api.post('/ai-prep/mock/start', data)
    return res.data
  },

  /**
   * List candidate's past and active mock interview sessions.
   */
  async listMockSessions(limit = 20) {
    const res = await api.get('/ai-prep/mock/sessions', { params: { limit } })
    return res.data
  },

  /**
   * Get session transcript and current status.
   */
  async getMockSession(sessionId) {
    const res = await api.get(`/ai-prep/mock/${sessionId}`)
    return res.data
  },

  /**
   * Send candidate message and receive adaptive follow-up question.
   */
  async sendMockMessage(sessionId, message) {
    const res = await api.post(`/ai-prep/mock/${sessionId}/message`, { message })
    return res.data
  },

  /**
   * Conclude the mock interview and generate a multi-dimensional rubric report.
   */
  async endMockSession(sessionId, reason) {
    const payload = reason ? { reason } : {}
    const res = await api.post(`/ai-prep/mock/${sessionId}/end`, payload)
    return res.data
  },

  /**
   * Retrieve the final evaluation report for a session.
   */
  async getMockReport(sessionId) {
    const res = await api.get(`/ai-prep/mock/${sessionId}/report`)
    return res.data
  },

  /**
   * Upload and analyze candidate resume with Gemini.
   */
  async uploadResume(file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/ai-prep/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return res.data
  },

  /**
   * List all uploaded resumes and structured intelligence for candidate.
   */
  async listResumes() {
    const res = await api.get('/ai-prep/resumes')
    return res.data
  },
}

export default aiPrepService

