/* ────────────────────────────────────────────────────────────────────────
   Shared brand logo — a single source of truth so the mark + wordmark
   look identical in the dashboard top nav, the public landing nav, and
   the footer.
   ──────────────────────────────────────────────────────────────────── */

const SIZE_MAP = {
  sm: { box: 'w-8 h-8',  icon: 'w-5 h-5',  text: 'text-lg'  },
  md: { box: 'w-10 h-10', icon: 'w-6 h-6', text: 'text-xl'  },
  lg: { box: 'w-12 h-12', icon: 'w-7 h-7', text: 'text-2xl' },
}

export function LogoMark({ size = 'md', className = '', tone = 'default' }) {
  const s = SIZE_MAP[size] || SIZE_MAP.md
  const boxTone = tone === 'onDark' ? 'bg-white/10' : 'bg-forest-900'
  return (
    <div className={`${s.box} ${boxTone} rounded-2xl flex items-center justify-center flex-shrink-0 ${className}`}>
      <svg viewBox="0 0 24 24" fill="none" className={`${s.icon} text-white`} stroke="currentColor" strokeWidth="2">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M9 12.75l1.75 1.75L15 10M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
        />
      </svg>
    </div>
  )
}

export default function Logo({ size = 'md', tone = 'default', textClassName = '', showText = true }) {
  const s = SIZE_MAP[size] || SIZE_MAP.md
  const textTone = tone === 'onDark' ? 'text-white' : 'text-forest-900'
  return (
    <div className="flex items-center gap-2.5">
      <LogoMark size={size} tone={tone} />
      {showText && (
        <span className={`font-display font-bold ${textTone} ${s.text} ${textClassName}`}>
          TalentForge
        </span>
      )}
    </div>
  )
}
