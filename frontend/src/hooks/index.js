import { useState, useEffect, useCallback, useRef } from 'react'
import { notificationService } from '../services/userService'
import interviewService from '../services/interviewService'

// ── Generic data-fetching hook ────────────────────────────────────────────
export function useFetch(fetchFn, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const mountedRef = useRef(true)
  const fetchRef = useRef(fetchFn)

  // keep latest fetch function without triggering rerenders
  useEffect(() => {
    fetchRef.current = fetchFn
  }, [fetchFn])

  const execute = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await fetchRef.current()
      if (mountedRef.current) setData(result)
    } catch (err) {
      if (mountedRef.current) {
        setError(err?.response?.data?.error || err.message)
      }
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }, [])

  useEffect(() => {
    mountedRef.current = true
    execute()

    return () => {
      mountedRef.current = false
    }
  }, [execute])

  return { data, loading, error, refetch: execute }
}

// ── Interviews list hook ──────────────────────────────────────────────────
export function useInterviews(params = {}) {
  const key = JSON.stringify(params)

  const fetchFn = useCallback(() => {
    return interviewService.list(params)
  }, [key])

  return useFetch(fetchFn, [key])
}

// ── Notifications hook with unread count ─────────────────────────────────
export function useNotifications() {
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const [list, count] = await Promise.all([
        notificationService.list({ per_page: 10 }),
        notificationService.unreadCount(),
      ])

      setNotifications(list.items || [])
      setUnreadCount(count)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()

    const interval = setInterval(load, 30000)

    return () => clearInterval(interval)
  }, [load])

  const markRead = async (id) => {
    await notificationService.markRead(id)

    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, is_read: true } : n))
    )

    setUnreadCount(prev => Math.max(0, prev - 1))
  }

  const markAllRead = async () => {
    await notificationService.markAllRead()

    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    setUnreadCount(0)
  }

  return { notifications, unreadCount, loading, markRead, markAllRead, refetch: load }
}

// ── Pagination hook ───────────────────────────────────────────────────────
export function usePagination(initialPage = 1, perPage = 20) {
  const [page, setPage] = useState(initialPage)
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)

  const next = () => page < pages && setPage(p => p + 1)
  const prev = () => page > 1 && setPage(p => p - 1)
  const go = (n) => setPage(n)

  const update = (paginationData) => {
    setTotal(paginationData.total ?? 0)
    setPages(paginationData.pages ?? 1)
  }

  return { page, perPage, total, pages, next, prev, go, update }
}