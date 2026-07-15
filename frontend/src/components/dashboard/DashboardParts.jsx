import { Link } from 'react-router-dom'

/* ────────────────────────────────────────────────────────────────────────
   Decorative illustrations — simple, on-brand, no external assets.
   Kept intentionally light/abstract so they never fight for attention
   with the real content.
   ──────────────────────────────────────────────────────────────────── */
export function HeaderIllustration({ variant = 'default' }) {
  const common = 'w-full h-full'
  if (variant === 'admin') {
    return (
      <svg viewBox="0 0 200 140" className={common} fill="none">
        <circle cx="100" cy="70" r="58" fill="#f0f7f4" />
        <rect x="46" y="52" width="72" height="52" rx="8" fill="#ffffff" stroke="#d9ede5" strokeWidth="2" />
        <rect x="58" y="64" width="32" height="4" rx="2" fill="#163a2f" opacity="0.5" />
        <rect x="58" y="74" width="48" height="4" rx="2" fill="#84c2ab" />
        <rect x="58" y="84" width="24" height="4" rx="2" fill="#84c2ab" />
        <circle cx="132" cy="46" r="16" fill="#163a2f" />
        <path d="M126 46l4 4 8-8" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="52" cy="36" r="10" fill="#fbbf24" opacity="0.9" />
      </svg>
    )
  }
  if (variant === 'recruiter') {
    return (
      <svg viewBox="0 0 200 140" className={common} fill="none">
        <circle cx="102" cy="72" r="58" fill="#f0f7f4" />
        <rect x="52" y="48" width="56" height="70" rx="10" fill="#ffffff" stroke="#d9ede5" strokeWidth="2" />
        <circle cx="80" cy="70" r="10" fill="#163a2f" opacity="0.85" />
        <rect x="64" y="86" width="32" height="6" rx="3" fill="#84c2ab" />
        <rect x="64" y="98" width="24" height="6" rx="3" fill="#f0ead6" />
        <rect x="118" y="60" width="40" height="46" rx="8" fill="#163a2f" />
        <path d="M128 78l6 6 12-12" stroke="#fbbf24" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  }
  if (variant === 'candidate') {
    return (
      <svg viewBox="0 0 200 140" className={common} fill="none">
        <circle cx="100" cy="70" r="58" fill="#f0f7f4" />
        <rect x="58" y="40" width="60" height="80" rx="10" fill="#ffffff" stroke="#d9ede5" strokeWidth="2" />
        <circle cx="88" cy="66" r="12" fill="#163a2f" />
        <rect x="70" y="86" width="36" height="5" rx="2.5" fill="#84c2ab" />
        <rect x="70" y="98" width="24" height="5" rx="2.5" fill="#f0ead6" />
        <circle cx="132" cy="42" r="14" fill="#fbbf24" />
        <path d="M126 42l4 4 8-8" stroke="#163a2f" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  }
  // default / interviewer
  return (
    <svg viewBox="0 0 200 140" className={common} fill="none">
      <circle cx="100" cy="70" r="58" fill="#f0f7f4" />
      <rect x="112" y="30" width="52" height="40" rx="6" fill="#ffffff" stroke="#d9ede5" strokeWidth="2" />
      <rect x="120" y="40" width="30" height="3" rx="1.5" fill="#84c2ab" />
      <rect x="120" y="48" width="20" height="3" rx="1.5" fill="#f0ead6" />
      <ellipse cx="86" cy="100" rx="8" ry="18" fill="#84c2ab" opacity="0.7" />
      <rect x="80" y="60" width="14" height="42" rx="7" fill="#163a2f" />
      <circle cx="87" cy="46" r="14" fill="#163a2f" />
      <circle cx="150" cy="96" r="10" fill="#163a2f" />
      <path d="M144 96l4 4 8-8" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

/* ────────────────────────────────────────────────────────────────────────
   DashboardHeader — label · big serif welcome heading · description ·
   illustration top-right. Shared by all four roles.
   ──────────────────────────────────────────────────────────────────── */
export function DashboardHeader({ label, heading, description, illustration = 'default', actions }) {
  return (
    <div className="relative overflow-hidden rounded-3xl bg-white border border-cream-200 shadow-card px-6 sm:px-8 py-7 mb-6">
      <div className="relative z-10 max-w-xl">
        {label && <p className="section-label">{label}</p>}
        <h1 className="font-display text-2xl sm:text-3xl font-bold text-forest-900 leading-tight">{heading}</h1>
        {description && <p className="text-forest-500 font-sans text-sm mt-2">{description}</p>}
        {actions && <div className="mt-4 flex flex-wrap gap-3">{actions}</div>}
      </div>
      <div className="hidden sm:block absolute -right-4 -top-2 w-44 h-36 pointer-events-none select-none">
        <HeaderIllustration variant={illustration} />
      </div>
    </div>
  )
}

/* ────────────────────────────────────────────────────────────────────────
   StatsCard — icon · large number · title · subtitle · decorative
   sparkline in the corner. First card in a row is typically `variant="green"`.
   ──────────────────────────────────────────────────────────────────── */
function Sparkline({ tone = 'green' }) {
  const stroke = tone === 'onDark' ? '#ffffff' : tone === 'amber' ? '#f59e0b' : '#236b54'
  const fill = tone === 'onDark' ? 'rgba(255,255,255,0.12)' : tone === 'amber' ? 'rgba(245,158,11,0.12)' : 'rgba(35,107,84,0.10)'
  return (
    <svg viewBox="0 0 96 40" className="absolute bottom-0 right-0 w-24 h-10 opacity-90" preserveAspectRatio="none">
      <path d="M0 30 L14 24 L28 28 L42 14 L56 20 L70 8 L84 14 L96 4 L96 40 L0 40 Z" fill={fill} />
      <path d="M0 30 L14 24 L28 28 L42 14 L56 20 L70 8 L84 14 L96 4" fill="none" stroke={stroke} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function StatsCard({ icon, value, title, subtitle, variant = 'default' }) {
  const isDark = variant === 'green'
  const isAmber = variant === 'amber'

  const wrap = isDark
    ? 'bg-forest-900 border-forest-800 text-white'
    : isAmber
      ? 'bg-amber-50 border-amber-200'
      : 'bg-white border-cream-200'

  const iconWrap = isDark
    ? 'bg-white/10 text-white'
    : isAmber
      ? 'bg-amber-400 text-forest-900'
      : 'bg-forest-50 text-forest-800'

  const titleColor = isDark ? 'text-white' : 'text-forest-900'
  const subColor = isDark ? 'text-forest-200' : 'text-forest-400'

  return (
    <div className={`relative overflow-hidden rounded-2xl border p-5 shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:shadow-card-hover ${wrap}`}>
      <div className="relative z-10">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg mb-4 ${iconWrap}`}>
          {icon}
        </div>
        <div className={`font-display text-3xl font-bold ${titleColor}`}>{value}</div>
        <div className={`text-sm font-semibold mt-1 ${titleColor}`}>{title}</div>
        {subtitle && <div className={`text-xs mt-0.5 ${subColor}`}>{subtitle}</div>}
      </div>
      <Sparkline tone={isDark ? 'onDark' : isAmber ? 'amber' : 'green'} />
    </div>
  )
}

/* ────────────────────────────────────────────────────────────────────────
   DashboardPanel — header (title + optional "View all" link) + content.
   ──────────────────────────────────────────────────────────────────── */
export function DashboardPanel({ title, actionLabel, actionTo, onAction, children, className = '' }) {
  return (
    <div className={`card flex flex-col ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display text-lg text-forest-900">{title}</h2>
        {actionLabel && actionTo && (
          <Link to={actionTo} className="text-forest-600 text-sm font-medium hover:text-forest-900 transition-colors">
            {actionLabel} →
          </Link>
        )}
        {actionLabel && onAction && !actionTo && (
          <button onClick={onAction} className="text-forest-600 text-sm font-medium hover:text-forest-900 transition-colors">
            {actionLabel} →
          </button>
        )}
      </div>
      <div className="flex-1">{children}</div>
    </div>
  )
}

/* ────────────────────────────────────────────────────────────────────────
   QuickActionCard — icon · title · description · arrow. Horizontal.
   ──────────────────────────────────────────────────────────────────── */
export function QuickActionCard({ to, icon, title, description, tone = 'default' }) {
  const iconWrap = tone === 'amber' ? 'bg-amber-400 text-forest-900' : 'bg-forest-100 text-forest-800'
  const cardCls = tone === 'amber' ? 'card-yellow border-amber-200' : 'card'

  return (
    <Link
      to={to}
      className={`${cardCls} flex items-center gap-4 group hover:-translate-y-0.5 hover:shadow-card-hover transition-all duration-200`}
    >
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0 group-hover:scale-105 transition-transform duration-200 ${iconWrap}`}>
        {icon}
      </div>
      <div className="min-w-0 flex-1">
        <p className="font-display font-semibold text-forest-900 truncate">{title}</p>
        <p className="text-forest-500 text-sm mt-0.5 truncate">{description}</p>
      </div>
      <span className="text-forest-400 group-hover:text-forest-900 group-hover:translate-x-0.5 transition-all duration-200 flex-shrink-0">→</span>
    </Link>
  )
}

/* ────────────────────────────────────────────────────────────────────────
   PanelEmptyState — a small, friendly empty state used inside panels.
   ──────────────────────────────────────────────────────────────────── */
export function PanelEmptyState({ icon = '📭', title, description }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-10">
      <div className="w-14 h-14 rounded-2xl bg-cream-100 flex items-center justify-center text-2xl mb-3">
        {icon}
      </div>
      <p className="font-display text-base text-forest-900">{title}</p>
      {description && <p className="text-forest-400 text-xs mt-1 max-w-[220px]">{description}</p>}
    </div>
  )
}
