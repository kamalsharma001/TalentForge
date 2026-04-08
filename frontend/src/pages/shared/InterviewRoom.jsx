import { useParams, useNavigate } from 'react-router-dom'
import { useFetch } from '../../hooks'
import interviewService from '../../services/interviewService'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { PageSpinner } from '../../components/ui'

export default function InterviewRoom() {

  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()

  const { data: interview, loading } = useFetch(
    () => interviewService.getById(id),
    [id]
  )

  if (loading) {
    return (
      <DashboardLayout>
        <PageSpinner />
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

  return (
    <DashboardLayout>

      <div className="max-w-5xl mx-auto animate-fade-in">

        {/* Header */}

        <div className="flex items-center justify-between mb-4">

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
              Leave
            </button>

          </div>

        </div>

        {/* Meeting */}

        {interview?.meeting_link ? (

          <div
            className="rounded-2xl overflow-hidden border border-forest-200"
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

        ) : (

          <div className="card text-center py-16">

            <p className="text-forest-500">
              No meeting link has been set for this interview.
            </p>

          </div>

        )}

      </div>

    </DashboardLayout>
  )
}