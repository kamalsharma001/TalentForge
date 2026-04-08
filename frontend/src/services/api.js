import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
})

// attach access token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// refresh logic
api.interceptors.response.use(
  (response) => response,
  async (error) => {

    const original = error.config

    if (error.response?.status === 401 && !original._retry) {

      original._retry = true

      try {

        const refresh = localStorage.getItem('refresh_token')

        if (!refresh) {
          console.warn("No refresh token available — using existing access token")
          return Promise.reject(error)
        }

        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refresh
        })

        localStorage.setItem("access_token", data.access_token)

        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${data.access_token}`

        return api(original)

      } catch (err) {

        console.warn("Refresh failed — clearing session")

        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")

        return Promise.reject(err)
      }
    }

    return Promise.reject(error)
  }
)

export default api