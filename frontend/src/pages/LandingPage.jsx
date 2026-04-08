import { useState } from 'react'
import { Link } from 'react-router-dom'
import PublicNav from '../components/layout/PublicNav'

const TECH_PROFILES = [
  { icon: '</>', label: 'Frontend',     color: 'bg-forest-900' },
  { icon: '>_',  label: 'Backend',      color: 'bg-forest-800' },
  { icon: '⬡',   label: 'Full Stack',   color: 'bg-forest-700' },
  { icon: '⚙',   label: 'DevOps',       color: 'bg-forest-900' },
  { icon: '📱',  label: 'iOS / Android',color: 'bg-forest-800' },
  { icon: '🤖',  label: 'ML / AI',      color: 'bg-forest-700' },
]

const HOW_STEPS = [
  { n: '1', title: 'Select profile & template to request interviewer',  active: true  },
  { n: '2', title: 'Wait for the interview to happen',                   active: false },
  { n: '3', title: 'Make an informed decision with the report',          active: false },
]

const FEATURES = [
  {
    icon: '🎯',
    title: 'Expert Interviewers',
    body:  'Every interviewer is vetted through a 2-round process and rated ≥ 4/5 before being approved.',
  },
  {
    icon: '🎬',
    title: 'Recorded Interviews',
    body:  'All sessions are recorded and stored securely. Revisit any moment before making a decision.',
  },
  {
    icon: '🤖',
    title: 'AI-Generated Reports',
    body:  'Detailed evaluation reports with AI summaries are ready within 5 minutes of interview completion.',
  },
  {
    icon: '📅',
    title: 'Flexible Scheduling',
    body:  'Match candidate availability with expert interviewers across every timezone effortlessly.',
  },
]

const TESTIMONIALS = [
  {
    quote: "TalentForge saved us 40+ engineering hours last quarter. The reports are incredibly detailed.",
    name: 'Priya Sharma',
    role: 'VP Engineering, Fintech Startup',
    initials: 'PS',
  },
  {
    quote: "The AI feedback summaries are spot-on. We make hiring decisions with full confidence now.",
    name: 'Marcus Chen',
    role: 'Head of Talent, Scale-up',
    initials: 'MC',
  },
  {
    quote: "Being an interviewer on TalentForge is a great way to stay sharp and earn on the side.",
    name: 'Aditi Patel',
    role: 'Senior Engineer & Interviewer',
    initials: 'AP',
  },
]

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState('org')

  return (
    <div className="min-h-screen bg-cream-100">
      <PublicNav />

      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="relative bg-cream-100 overflow-hidden">
        {/* Subtle texture */}
        <div className="absolute inset-0 opacity-30"
          style={{ backgroundImage: 'radial-gradient(circle at 20% 50%, #d4c99a 0%, transparent 50%), radial-gradient(circle at 80% 20%, #b5dbcc 0%, transparent 50%)' }} />

        <div className="relative max-w-7xl mx-auto px-6 pt-16 pb-8">
          {/* Org / Candidate toggle */}
          <div className="flex justify-center mb-10">
            <div className="inline-flex bg-white rounded-full p-1 shadow-card border border-cream-200">
              <button
                onClick={() => setActiveTab('org')}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold transition-all duration-200 ${
                  activeTab === 'org'
                    ? 'bg-amber-300 text-forest-900 shadow-sm'
                    : 'text-forest-600 hover:text-forest-900'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${activeTab === 'org' ? 'bg-forest-900' : 'bg-cream-300'}`} />
                For Organisations
                <span className="text-xs font-normal opacity-70 hidden sm:block">Outsource your interviews to us</span>
              </button>
              <button
                onClick={() => setActiveTab('candidate')}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold transition-all duration-200 ${
                  activeTab === 'candidate'
                    ? 'bg-amber-300 text-forest-900 shadow-sm'
                    : 'text-forest-600 hover:text-forest-900'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${activeTab === 'candidate' ? 'bg-forest-900' : 'bg-cream-300'}`} />
                For Candidates
                <span className="text-xs font-normal opacity-70 hidden sm:block">Practice with top tech experts</span>
              </button>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left copy */}
            <div className="animate-slide-up">
              {activeTab === 'org' ? (
                <>
                  <p className="section-label">Outsource technical interviews</p>
                  <h1 className="font-display text-5xl md:text-6xl text-forest-900 leading-tight mb-4">
                    Save your engineering<br />bandwidth
                  </h1>
                  <p className="text-forest-600 font-sans text-lg mb-4">
                    Outsource your interviews in just 2 simple steps
                  </p>
                  {/* Search bar mirroring the screenshot */}
                  <div className="flex items-center gap-2 bg-white rounded-full border border-cream-300 shadow-sm px-4 py-3 mb-8 max-w-md">
                    <svg className="w-4 h-4 text-forest-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                    <span className="text-forest-400 text-sm">Search by tech stack, role…</span>
                  </div>
                  {/* Tech icons */}
                  <div className="flex flex-wrap gap-4 mb-8">
                    {TECH_PROFILES.map(p => (
                      <div key={p.label} className="flex flex-col items-center gap-1.5 cursor-pointer group">
                        <div className={`w-12 h-12 ${p.color} rounded-xl flex items-center justify-center text-white text-lg font-mono font-bold shadow-sm group-hover:scale-110 transition-transform`}>
                          {p.icon}
                        </div>
                        <span className="text-xs text-forest-600 font-sans">{p.label}</span>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-3">
                    <Link to="/register?role=recruiter" className="btn-amber text-base px-7 py-3 font-bold">
                      Request → 
                    </Link>
                    <Link to="/login" className="btn-secondary">
                      Login
                    </Link>
                  </div>
                </>
              ) : (
                <>
                  <p className="section-label">Practice with real experts</p>
                  <h1 className="font-display text-5xl md:text-6xl text-forest-900 leading-tight mb-4">
                    Ace your next<br />tech interview
                  </h1>
                  <p className="text-forest-600 font-sans text-lg mb-8">
                    Get interviewed by FAANG engineers, get detailed feedback, and land your dream job.
                  </p>
                  <Link to="/register?role=candidate" className="btn-primary text-base px-7 py-3">
                    Get started →
                  </Link>
                </>
              )}
            </div>

            {/* Right — 3-step cards */}
          <div className="space-y-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>

            {/* Card 1 — Select Tech Stack */}
            <div className="card-yellow border-amber-200 shadow-sm hover:shadow-md transition-all duration-200">
              <p className="section-label mb-3 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-forest-800 text-white text-xs flex items-center justify-center">
                  1
                </span>
                Select Tech Stack
              </p>

              <div className="flex gap-3 flex-wrap">
                {TECH_PROFILES.slice(0,5).map(p => (
                  <div
                    key={p.label}
                    className={`w-11 h-11 ${p.color} rounded-xl flex items-center justify-center text-white text-sm font-mono font-bold hover:scale-105 transition-transform cursor-pointer`}
                  >
                    {p.icon}
                  </div>
                ))}

                <div className="w-11 h-11 border-2 border-dashed border-forest-400 rounded-xl flex items-center justify-center text-forest-600 text-sm font-bold hover:bg-forest-50 transition cursor-pointer">
                  +
                </div>
              </div>
            </div>


            {/* Card 2 — Choose Interviewer */}
            <div className="card-yellow border-amber-200 shadow-sm hover:shadow-md transition-all duration-200">
              <p className="section-label mb-3 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-forest-800 text-white text-xs flex items-center justify-center">
                  2
                </span>
                Choose Interviewer
              </p>

              <div className="flex gap-3">
                {['Senior Engineer', 'Staff Engineer', 'Hiring Manager'].map(label => (
                  <button
                    key={label}
                    className="flex-1 flex items-center gap-2 bg-forest-800 hover:bg-forest-700 shadow-sm hover:shadow-md text-white rounded-xl px-3 py-2.5 text-sm font-semibold transition-all"
                  >
                    <div className="w-6 h-6 bg-forest-600 rounded-full flex-shrink-0" />
                    {label}
                  </button>
                ))}
              </div>
            </div>


            {/* Card 3 — Schedule */}
            <div className="card-yellow border-amber-200 shadow-sm hover:shadow-md transition-all duration-200">
              <p className="section-label mb-3 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-forest-800 text-white text-xs flex items-center justify-center">
                  3
                </span>
                Pick Interview Slot
              </p>

              <div className="flex gap-3">
                {['Today', 'Tomorrow', 'This Week'].map(label => (
                  <button
                    key={label}
                    className="flex-1 bg-forest-800 hover:bg-forest-700 shadow-sm hover:shadow-md text-white rounded-xl px-3 py-2.5 text-sm font-semibold transition-all"
                  >
                    {label}
                  </button>
                ))}
              </div>

              <button className="w-full mt-3 bg-amber-500 hover:bg-amber-600 text-white rounded-xl px-3 py-2.5 text-sm font-semibold transition">
                Schedule Interview →
              </button>
            </div>
          </div>
          </div>
        </div>
      </section>

      {/* ── How it works ────────────────────────────────────────────── */}
      <section id="how-it-works" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="font-display text-4xl text-forest-900 mb-2">Here's how it works</h2>
            <p className="text-forest-500 font-sans">Get started now</p>
          </div>

          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Steps */}
            <div className="space-y-4">
              {HOW_STEPS.map(step => (
                <div key={step.n} className={`flex items-center gap-4 px-5 py-4 rounded-2xl font-sans font-semibold text-base transition-colors ${
                  step.active
                    ? 'bg-forest-900 text-white shadow-btn'
                    : 'bg-cream-100 text-forest-700'
                }`}>
                  <span className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${step.active ? 'bg-white text-forest-900' : 'bg-cream-300 text-forest-600'}`}>
                    {step.n}
                  </span>
                  {step.title}
                </div>
              ))}
            </div>

            {/* Preview UI */}
            <div className="relative">
              <div className="bg-forest-800 rounded-2xl p-4 shadow-card-hover">
                <div className="flex items-center gap-2 bg-forest-700 rounded-xl px-3 py-2 mb-4">
                  <svg className="w-4 h-4 text-forest-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                  <span className="text-forest-300 text-sm">Search</span>
                </div>
                <div className="grid grid-cols-3 gap-2 mb-4">
                  {TECH_PROFILES.map(p => (
                    <div key={p.label} className="bg-forest-700 rounded-xl p-3 flex flex-col items-center gap-1.5">
                      <span className="text-white text-xl font-mono">{p.icon}</span>
                      <span className="text-forest-300 text-xs">{p.label}</span>
                    </div>
                  ))}
                </div>
              </div>
              {/* Floating card */}
              <div className="absolute -bottom-4 -right-4 bg-white rounded-xl shadow-card-hover p-4 w-52">
                <div className="flex items-center gap-1.5 mb-3">
                  <span className="text-amber-500 text-sm">↗</span>
                  <span className="text-forest-900 font-semibold text-sm">Request Interviewer</span>
                </div>
                <div className="space-y-2">
                  <div>
                    <p className="text-forest-500 text-xs mb-1">Profile</p>
                    <div className="bg-cream-200 rounded-lg px-3 py-1.5 text-forest-700 text-sm">Backend</div>
                  </div>
                  <div>
                    <p className="text-forest-500 text-xs mb-1">Role</p>
                    <div className="bg-cream-200 rounded-lg px-3 py-1.5 text-forest-700 text-sm">Python developer</div>
                  </div>
                  <button className="w-full bg-forest-900 text-white rounded-lg py-2 text-sm font-semibold">
                    Request Now →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ────────────────────────────────────────────────── */}
      <section id="for-recruiters" className="py-20 bg-cream-100">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-14">
            <p className="section-label">Interview reports & quality</p>
            <h2 className="font-display text-4xl text-forest-900 mb-3">Detailed reports with video recording</h2>
            <p className="text-forest-500 font-sans max-w-xl mx-auto">
              TalentForge's reports allow you to understand a candidate's technical aptitude and problem-solving skills in depth.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map(f => (
              <div key={f.title} className="card group">
                <div className="text-3xl mb-4">{f.icon}</div>
                <h3 className="font-display text-lg text-forest-900 mb-2">{f.title}</h3>
                <p className="text-forest-500 font-sans text-sm leading-relaxed">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Interviewer vetting ──────────────────────────────────────── */}
      <section id="for-interviewers" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Form card */}
            <div className="card shadow-card-hover max-w-md">
              <h3 className="font-display text-xl text-forest-900 mb-1">Tell us a bit more about you</h3>
              <p className="text-forest-500 text-sm mb-6">These details help us evaluate your interviewing skills better</p>
              <div className="space-y-4">
                <div>
                  <label className="label">Your phone number:</label>
                  <input className="input" placeholder="+1 (555) 000-0000" type="tel" />
                </div>
                <div>
                  <label className="label">Your designation:</label>
                  <input className="input" placeholder="e.g. Senior Software Engineer" />
                </div>
                <Link to="/register?role=interviewer" className="btn-primary w-full justify-center mt-2">
                  Submit
                </Link>
              </div>
            </div>

            {/* Vetting process */}
            <div>
              <h2 className="font-display text-4xl text-forest-900 mb-8">Interview vetting process</h2>
              <ul className="space-y-4">
                {[
                  'New interviewers choose technical parameters',
                  'An expert on our platform takes their technical interview based on those parameters',
                  'New interviewers also undergo a shadow interview round to test for interviewing skills',
                  'Only if they receive a rating of 4/5 in both rounds, they are onboarded as new interviewers',
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-forest-700 font-sans">
                    <span className="w-5 h-5 rounded-full bg-amber-400 text-forest-900 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                      ✓
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ── Testimonials ─────────────────────────────────────────────── */}
      <section className="py-20 bg-forest-900">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="font-display text-4xl text-white text-center mb-14">Trusted by engineering teams</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {TESTIMONIALS.map(t => (
              <div key={t.name} className="bg-forest-800 rounded-2xl p-6 border border-forest-700">
                <p className="text-forest-200 font-sans text-sm leading-relaxed mb-6">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 bg-amber-400 rounded-full flex items-center justify-center text-forest-900 font-bold text-sm">
                    {t.initials}
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">{t.name}</p>
                    <p className="text-forest-400 text-xs">{t.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────────── */}
      <section className="py-20 bg-cream-100">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <h2 className="font-display text-4xl text-forest-900 mb-4">Ready to forge better talent?</h2>
          <p className="text-forest-500 font-sans mb-8">Join hundreds of companies saving engineering hours while making better hiring decisions.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register?role=recruiter" className="btn-primary text-base px-8 py-3.5">
              Start as Recruiter →
            </Link>
            <Link to="/register?role=interviewer" className="btn-secondary text-base px-8 py-3.5">
              Become an Interviewer
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <footer className="bg-forest-950 text-forest-400 py-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-forest-700 rounded-md flex items-center justify-center">
              <span className="text-white text-xs font-bold">T</span>
            </div>
            <span className="text-white font-display font-bold">TalentForge</span>
          </div>
          <p className="text-sm">© {new Date().getFullYear()} TalentForge. AI-powered technical interviews.</p>
          <div className="flex gap-5 text-sm">
            <Link to="/login" className="hover:text-white transition-colors">Login</Link>
            <Link to="/register" className="hover:text-white transition-colors">Sign up</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
