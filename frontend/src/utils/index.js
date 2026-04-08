import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns'

// ── Date helpers ──────────────────────────────────────────────────────────

export function fmtDate(dateStr, pattern = 'MMM d, yyyy') {
  if (!dateStr) return '—'
  const d = typeof dateStr === 'string' ? parseISO(dateStr) : dateStr
  return isValid(d) ? format(d, pattern) : '—'
}

export function fmtDateTime(dateStr) {
  return fmtDate(dateStr, 'MMM d, yyyy · h:mm a')
}

export function fmtRelative(dateStr) {
  if (!dateStr) return '—'
  const d = typeof dateStr === 'string' ? parseISO(dateStr) : dateStr
  return isValid(d) ? formatDistanceToNow(d, { addSuffix: true }) : '—'
}

// ── String helpers ────────────────────────────────────────────────────────

export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function truncate(str, max = 60) {
  if (!str || str.length <= max) return str
  return str.slice(0, max).trimEnd() + '…'
}

export function initials(name = '') {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '')
}

// ── API error parser ──────────────────────────────────────────────────────

export function parseApiError(err) {
  if (!err) return 'An unexpected error occurred.'
  const data = err?.response?.data
  if (!data) return err.message || 'Network error'
  if (data.error)   return data.error
  if (data.errors)  return Object.values(data.errors).flat().join(' ')
  if (data.message) return data.message
  return 'An unexpected error occurred.'
}

// ── Score colour helper ───────────────────────────────────────────────────

export function scoreColor(score, max = 10) {
  const pct = (score / max) * 100
  if (pct >= 70) return 'text-green-600'
  if (pct >= 40) return 'text-amber-500'
  return 'text-red-500'
}

// ── Duration formatter ────────────────────────────────────────────────────

export function fmtDuration(minutes) {
  if (!minutes) return '—'
  if (minutes < 60) return `${minutes}m`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m ? `${h}h ${m}m` : `${h}h`
}

// ── Role display names ────────────────────────────────────────────────────

export const ROLE_LABELS = {
  admin:       'Admin',
  recruiter:   'Recruiter',
  interviewer: 'Interviewer',
  candidate:   'Candidate',
}

export const ROLE_DASHBOARDS = {
  admin:       '/admin',
  recruiter:   '/recruiter',
  interviewer: '/interviewer',
  candidate:   '/candidate',
}

// ── Status display ────────────────────────────────────────────────────────

export const STATUS_LABELS = {
  pending:        'Pending',
  scheduled:      'Scheduled',
  completed:      'Completed',
  report_pending: 'Report Pending',
  cancelled:      'Cancelled',
}
