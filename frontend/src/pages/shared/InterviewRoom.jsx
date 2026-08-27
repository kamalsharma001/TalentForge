import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useFetch } from '../../hooks'
import interviewService from '../../services/interviewService'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { PageSpinner, StatusBadge } from '../../components/ui'
import { format } from 'date-fns'

export default function InterviewRoom() {

  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()

  const { data: interview, loading, error, refetch } = useFetch(
    () => interviewService.getById(id),
    [id]
  )

  const [now, setNow] = useState(new Date())

  const scheduledTime = interview?.scheduled_at ? new Date(interview.scheduled_at) : null
  const joinAllowedFrom = scheduledTime ? new Date(scheduledTime.getTime() - 5 * 60 * 1000) : null

  useEffect(() => {
    if (!scheduledTime || !joinAllowedFrom) return
    const timer = setInterval(() => {
      const current = new Date()
      setNow(current)
      
      // Auto-refetch the exact second the join window opens to fetch meeting_link
      if (current >= joinAllowedFrom && now < joinAllowedFrom) {
        refetch()
      }
    }, 1000)
    return () => clearInterval(timer)
  }, [scheduledTime, joinAllowedFrom, now, refetch])

  if (loading) {
    return (
      <DashboardLayout>
        <PageSpinner />
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="max-w-xl mx-auto mt-10 card text-center py-16 text-red-600">
          <span className="text-4xl mb-4 block">🚫</span>
          <h3 className="font-display text-xl text-red-950 mb-2">Access Denied</h3>
          <p className="text-forest-600 text-sm">{error || "You are not authorized to join this interview."}</p>
          <button onClick={() => navigate(-1)} className="btn-secondary mt-6 mx-auto">Go Back</button>
        </div>
      </DashboardLayout>
    )
  }

  if (!interview) {
    return (
      <DashboardLayout>
        <div className="card text-center py-16">
          <p className="text-forest-500">Interview not found.</p>
        </div>
      </DashboardLayout>
    )
  }

  const role = user?.role?.split('.').pop()?.toLowerCase()
  const status = interview?.status?.split('.')?.pop()?.toLowerCase()

  const canEndInterview =
    role === 'interviewer' &&
    status === 'scheduled'

  const handleEndInterview = async () => {
    try {
      await interviewService.complete(id, { scores: [] })
      navigate(`/interviewer/reports?interview=${id}`)
    } catch (err) {
      console.error("Failed to complete interview", err)
    }
  }

  const isEarly = joinAllowedFrom && now < joinAllowedFrom

  // Render video or status card based on active status
  let statusContent = null;
  if (status === 'pending') {
    statusContent = (
      <div className="card text-center py-16 bg-cream-50/50 border-cream-200">
        <span className="text-4xl mb-4 block">⏳</span>
        <h3 className="font-display text-xl text-forest-900 mb-2">Interview Pending Scheduling</h3>
        <p className="text-forest-600 text-sm">This interview has not been scheduled yet. You will be notified once a time slot is assigned.</p>
      </div>
    );
  } else if (isEarly) {
    const diffMs = joinAllowedFrom - now;
    const diffSecs = Math.max(0, Math.floor(diffMs / 1000));
    const mins = Math.floor(diffSecs / 60);
    const secs = diffSecs % 60;
    const countdownStr = `${mins}:${secs.toString().padStart(2, '0')}`;

    statusContent = (
      <div className="card text-center py-16 bg-cream-50/50 border-cream-200 shadow-sm">
        <span className="text-4xl mb-4 block">⏰</span>
        <h3 className="font-display text-xl text-forest-900 mb-2">Too Early to Join</h3>
        <p className="text-forest-600 text-sm mb-4">
          You can join this interview 5 minutes before the scheduled start time.
        </p>
        <p className="text-xs text-forest-400 font-sans uppercase tracking-wider">
          Scheduled to start at {format(scheduledTime, 'h:mm a')}
        </p>
        <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-forest-900 text-white rounded-full text-sm font-semibold font-mono">
          <span>⏳ Join opens in</span>
          <span>{countdownStr}</span>
        </div>
      </div>
    );
  } else if (status === 'completed' || status === 'report_pending') {
    statusContent = (
      <div className="card text-center py-16 bg-cream-50/50 border-cream-200">
        <span className="text-4xl mb-4 block">✅</span>
        <h3 className="font-display text-xl text-forest-900 mb-2">Interview Completed</h3>
        <p className="text-forest-600 text-sm font-sans">This interview session has already ended and is marked as completed.</p>
      </div>
    );
  } else if (status === 'cancelled') {
    statusContent = (
      <div className="card text-center py-16 bg-red-50/30 border-red-200 text-red-700">
        <span className="text-4xl mb-4 block">🚫</span>
        <h3 className="font-display text-xl text-red-950 mb-2">Interview Cancelled</h3>
        <p className="text-red-900/70 text-sm">This interview request has been cancelled by the recruiter or administrator.</p>
        {interview.cancellation_reason && (
          <p className="mt-4 text-xs italic font-serif">Reason: "{interview.cancellation_reason}"</p>
        )}
      </div>
    );
  } else if (!interview.meeting_link) {
    statusContent = (
      <div className="card text-center py-16">
        <p className="text-forest-500">No meeting link has been set for this interview.</p>
      </div>
    );
  } else {
    statusContent = (
      <div
        className="rounded-2xl overflow-hidden border border-forest-200 shadow-sm"
        style={{ height: '70vh' }}
      >
        <iframe
          src={interview.meeting_link}
          allow="camera; microphone; fullscreen; display-capture"
          style={{
            width: '100%',
            height: '100%',
            border: 'none'
          }}
          title="Interview Meeting"
        />
      </div>
    );
  }

  return (
    <DashboardLayout>

      <div className="max-w-7xl mx-auto animate-fade-in">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="section-label">Interview Room</p>
            <h1 className="font-display text-2xl text-forest-900">
              {interview?.title}
            </h1>
          </div>

          <div className="flex gap-3">
            {canEndInterview && (
              <button
                onClick={handleEndInterview}
                className="btn-amber text-sm"
              >
                End Interview →
              </button>
            )}
            <button
              onClick={() => navigate(-1)}
              className="btn-secondary text-sm"
            >
              Leave Room
            </button>
          </div>
        </div>

        {/* Layout Grid */}
        <div className="grid lg:grid-cols-4 gap-6">
          
          {/* Main Area */}
          <div className="lg:col-span-3">
            {statusContent}
          </div>

          {/* Details Sidebar */}
          <div className="space-y-4">
            <div className="card border border-cream-200 shadow-sm bg-cream-50/20">
              <h3 className="font-display font-bold text-forest-900 text-base mb-4 pb-2 border-b border-cream-100">
                Session Info
              </h3>
              <div className="space-y-3.5 text-sm">
                <div>
                  <span className="text-forest-400 block text-xs uppercase font-semibold">Target Role</span>
                  <span className="font-medium text-forest-900">{interview?.job_role || "Technical Interview"}</span>
                </div>
                <div>
                  <span className="text-forest-400 block text-xs uppercase font-semibold">Required Tech Stack</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {interview?.tech_stack?.length > 0 ? (
                      interview.tech_stack.map(s => (
                        <span key={s} className="px-2 py-0.5 bg-forest-100 text-forest-800 rounded text-xs font-semibold">
                          {s}
                        </span>
                      ))
                    ) : (
                      <span className="text-forest-500 font-medium">None specified</span>
                    )}
                  </div>
                </div>
                <div>
                  <span className="text-forest-400 block text-xs uppercase font-semibold">Difficulty</span>
                  <span className="font-medium text-forest-800 capitalize">{interview?.difficulty}</span>
                </div>
                <div>
                  <span className="text-forest-400 block text-xs uppercase font-semibold">Duration</span>
                  <span className="font-medium text-forest-800">{interview?.duration_mins} mins</span>
                </div>
                <div>
                  <span className="text-forest-400 block text-xs uppercase font-semibold">Scheduled Date & Time</span>
                  <span className="font-medium text-forest-800">
                    {interview?.scheduled_at ? format(new Date(interview.scheduled_at), 'PPP p') : 'TBD'}
                  </span>
                </div>
                <div>
                  <span className="text-forest-400 block text-xs uppercase font-semibold">Status</span>
                  <span className="inline-block mt-1"><StatusBadge status={status} /></span>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

    </DashboardLayout>
  )
}