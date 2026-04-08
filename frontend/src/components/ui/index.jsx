// ── Badge ──────────────────────────────────────────────────────────────────
export function Badge({ children, variant = 'gray' }) {
  const map = {
    green:  'badge-green',
    amber:  'badge-amber',
    red:    'badge-red',
    gray:   'badge-gray',
    blue:   'badge-blue',
  }
  return <span className={map[variant] || 'badge-gray'}>{children}</span>
}

// ── Interview status badge ─────────────────────────────────────────────────
const STATUS_MAP = {
  pending:        { label: 'Pending',        variant: 'gray'  },
  scheduled:      { label: 'Scheduled',      variant: 'blue'  },
  completed:      { label: 'Completed',      variant: 'green' },
  report_pending: { label: 'Report Pending', variant: 'amber' },
  cancelled:      { label: 'Cancelled',      variant: 'red'   },
}

export function StatusBadge({ status }) {
  const { label, variant } = STATUS_MAP[status] || { label: status, variant: 'gray' }
  return <Badge variant={variant}>{label}</Badge>
}

export function DecisionBadge({ decision }) {
  const map = {
    hire:    { label: '✓ Hire',    variant: 'green' },
    hold:    { label: '⏸ Hold',    variant: 'amber' },
    no_hire: { label: '✕ No Hire', variant: 'red'   },
  }
  const { label, variant } = map[decision] || { label: decision, variant: 'gray' }
  return <Badge variant={variant}>{label}</Badge>
}

// ── Avatar ─────────────────────────────────────────────────────────────────
export function Avatar({ name = '', url, size = 'md' }) {
  const sizeMap = { sm: 'w-7 h-7 text-xs', md: 'w-9 h-9 text-sm', lg: 'w-12 h-12 text-base', xl: 'w-16 h-16 text-lg' }
  const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)

  if (url) {
    return <img src={url} alt={name} className={`${sizeMap[size]} rounded-full object-cover ring-2 ring-white`} />
  }
  return (
    <div className={`${sizeMap[size]} rounded-full bg-forest-900 text-white flex items-center justify-center font-semibold font-sans flex-shrink-0`}>
      {initials || '?'}
    </div>
  )
}

// ── Spinner ────────────────────────────────────────────────────────────────
export function Spinner({ size = 'md', color = 'forest' }) {
  const sizeMap = { sm: 'w-4 h-4 border-2', md: 'w-8 h-8 border-3', lg: 'w-12 h-12 border-4' }
  const colorMap = { forest: 'border-forest-900', white: 'border-white', amber: 'border-amber-500' }
  return (
    <div className={`${sizeMap[size]} ${colorMap[color]} border-t-transparent rounded-full animate-spin`} />
  )
}

export function PageSpinner() {
  return (
    <div className="flex-1 flex items-center justify-center min-h-[60vh]">
      <Spinner size="lg" />
    </div>
  )
}

// ── Empty state ────────────────────────────────────────────────────────────
export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="text-5xl mb-4">{icon}</div>}
      <h3 className="font-display text-xl text-forest-900 mb-2">{title}</h3>
      {description && <p className="text-forest-500 font-sans text-sm max-w-xs">{description}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}

// ── Pagination ─────────────────────────────────────────────────────────────
export function Pagination({ page, pages, onNext, onPrev, onGo }) {
  if (pages <= 1) return null
  return (
    <div className="flex items-center justify-center gap-2 mt-6">
      <button
        onClick={onPrev}
        disabled={page <= 1}
        className="px-3 py-1.5 rounded-lg text-sm font-medium border border-cream-300 text-forest-700 hover:bg-cream-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        ← Prev
      </button>
      {Array.from({ length: Math.min(pages, 7) }, (_, i) => i + 1).map(n => (
        <button
          key={n}
          onClick={() => onGo(n)}
          className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
            n === page
              ? 'bg-forest-900 text-white'
              : 'border border-cream-300 text-forest-700 hover:bg-cream-200'
          }`}
        >
          {n}
        </button>
      ))}
      <button
        onClick={onNext}
        disabled={page >= pages}
        className="px-3 py-1.5 rounded-lg text-sm font-medium border border-cream-300 text-forest-700 hover:bg-cream-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        Next →
      </button>
    </div>
  )
}

// ── Score bar ──────────────────────────────────────────────────────────────
export function ScoreBar({ dimension, score, maxScore = 10 }) {
  const pct = Math.round((score / maxScore) * 100)
  const color = pct >= 70 ? 'bg-forest-600' : pct >= 40 ? 'bg-amber-400' : 'bg-red-400'
  return (
    <div className="mb-3">
      <div className="flex justify-between text-xs font-sans mb-1">
        <span className="text-forest-700 font-medium">{dimension}</span>
        <span className="text-forest-500">{score}/{maxScore}</span>
      </div>
      <div className="h-2 bg-cream-200 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

// ── Modal ─────────────────────────────────────────────────────────────────
export function Modal({ open, onClose, title, children, maxWidth = 'max-w-lg' }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-forest-950/40 backdrop-blur-sm" onClick={onClose} />
      <div className={`relative ${maxWidth} w-full bg-white rounded-2xl shadow-card-hover animate-slide-up`}>
        <div className="flex items-center justify-between p-6 border-b border-cream-200">
          <h2 className="font-display text-lg text-forest-900">{title}</h2>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-cream-100 text-forest-500 hover:text-forest-900 transition-colors">✕</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  )
}

// ── Stat card ─────────────────────────────────────────────────────────────
export function StatCard({ label, value, icon, trend, variant = 'default' }) {
  const variants = {
    default: 'bg-white border-cream-200',
    green:   'bg-forest-900 border-forest-800 text-white',
    amber:   'bg-amber-50  border-amber-200',
  }
  const textColor = variant === 'green' ? 'text-white' : 'text-forest-900'
  const subColor  = variant === 'green' ? 'text-forest-200' : 'text-forest-500'

  return (
    <div className={`rounded-2xl border p-5 shadow-card ${variants[variant]}`}>
      <div className="flex items-start justify-between mb-3">
        <span className={`text-2xl`}>{icon}</span>
        {trend && <span className="text-xs font-semibold bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{trend}</span>}
      </div>
      <div className={`text-3xl font-display font-bold ${textColor}`}>{value}</div>
      <div className={`text-sm font-sans mt-1 ${subColor}`}>{label}</div>
    </div>
  )
}

// ── Confirm dialog ─────────────────────────────────────────────────────────
export function ConfirmDialog({ open, onClose, onConfirm, title, message, confirmLabel = 'Confirm', danger = false }) {
  if (!open) return null
  return (
    <Modal open={open} onClose={onClose} title={title} maxWidth="max-w-sm">
      <p className="text-forest-600 text-sm mb-6">{message}</p>
      <div className="flex gap-3 justify-end">
        <button onClick={onClose} className="btn-secondary text-sm px-4 py-2">Cancel</button>
        <button
          onClick={() => { onConfirm(); onClose() }}
          className={danger ? 'inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-600 text-white font-semibold text-sm hover:bg-red-700 transition-colors' : 'btn-primary text-sm px-4 py-2'}
        >
          {confirmLabel}
        </button>
      </div>
    </Modal>
  )
}
