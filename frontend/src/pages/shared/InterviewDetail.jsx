import { useState } from "react"
import { useParams, Link, useNavigate } from "react-router-dom"
import DashboardLayout from "../../components/layout/DashboardLayout"
import { useAuth } from "../../context/AuthContext"
import { useFetch } from "../../hooks"
import interviewService from "../../services/interviewService"
import scheduleService from "../../services/scheduleService"
import {
  StatusBadge,
  ScoreBar,
  PageSpinner,
  Modal
} from "../../components/ui"
import toast from "react-hot-toast"
import { format } from "date-fns"
import PageHeader from "../../components/ui/PageHeader"

export default function InterviewDetail() {

  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()

  const { data: interview, loading } =
    useFetch(() => interviewService.getById(id), [id])

  const [showAssign, setShowAssign] = useState(false)
  const [showCancel, setShowCancel] = useState(false)

  const [cancelReason, setCancelReason] = useState("")
  const [assigning, setAssigning] = useState(false)
  const [cancelling, setCancelling] = useState(false)

  const [assignForm, setAssignForm] = useState({
    interviewer_id: "",
    slot_id: ""
  })

  /* Load slots only when assign modal opens */

  const { data: slotsData } = useFetch(
  () => scheduleService.listSlots({ available_only: true, per_page: 20 }),
  [showAssign]
  )
  
  const cleanStatus = status => status?.split(".").pop()

  /* Permission logic */
  console.log("role:", user?.role)
  console.log("status:", interview?.status)

  
  const role = user?.role?.split(".").pop()?.toLowerCase()
  const status = interview?.status?.split(".").pop()?.toLowerCase()

  const canAssign =
    role === "admin" &&
    status === "pending"

  const canJoin =
    status === "scheduled" &&
    interview?.meeting_link
    
  const canCancel =
  cleanStatus(interview?.status) !== "completed" &&
  cleanStatus(interview?.status) !== "cancelled"


  const canSubmitReport =
    user?.role === "interviewer" &&
    interview?.status === "report_pending"

  /* Assign interviewer */

  const handleAssign = async () => {

    if (!assignForm.slot_id) {
      toast.error("Select a slot")
      return
    }

    setAssigning(true)

    try {
      console.log("Assign payload:", assignForm)
      await interviewService.assign(id, assignForm)

      toast.success("Interviewer assigned")

      setShowAssign(false)

      navigate("/admin")

    } catch (err) {

      toast.error(
        err?.response?.data?.error || "Assignment failed"
      )

    } finally {

      setAssigning(false)

    }
  }

  /* Cancel interview */

  const handleCancel = async () => {

    setCancelling(true)

    try {

      await interviewService.cancel(id, cancelReason)

      toast.success("Interview cancelled")

      setShowCancel(false)

      navigate(-1)

    } catch (err) {

      toast.error(
        err?.response?.data?.error || "Cancellation failed"
      )

    } finally {

      setCancelling(false)

    }
  }

  if (loading)
    return (
      <DashboardLayout>
        <PageSpinner />
      </DashboardLayout>
    )

  if (!interview)
    return (
      <DashboardLayout>
        <div className="text-center py-20">
          Interview not found
        </div>
      </DashboardLayout>
    )

  return (
    <DashboardLayout>

      <div className="max-w-3xl mx-auto animate-fade-in">

        {/* Header */}

        <PageHeader
          title={interview.title}
          subtitle={interview.job_role || "Technical Interview"}
          badge={<StatusBadge status={cleanStatus(interview.status)} />}
          onBack={() => navigate(-1)}
          actions={
            <>
              {canAssign && (
                <button
                  onClick={() => setShowAssign(true)}
                  className="btn-primary text-sm h-10 px-4 flex items-center justify-center"
                >
                  Assign Interviewer
                </button>
              )}

              {canSubmitReport && (
                <Link
                  to={`/interviewer/reports?interview=${id}`}
                  className="btn-amber text-sm"
                >
                  Submit Report
                </Link>
              )}

              {canCancel && (
                <button
                  onClick={() => setShowCancel(true)}
                  className="btn-ghost text-red-500"
                >
                  Cancel
                </button>
              )}

              {canJoin && (
                <Link
                  to={`/interviews/${id}/room`}
                  className="btn-primary text-sm"
                >
                  Join Meeting →
                </Link>
              )}
            </>
          }
        />


        {/* Details */}

        <div className="grid sm:grid-cols-2 gap-4 mb-5">

          {[
            {
              label: "Tech Stack",
              value: interview.tech_stack?.join(", ") || "—"
            },
            {
              label: "Difficulty",
              value: interview.difficulty
            },
            {
              label: "Duration",
              value: `${interview.duration_mins} minutes`
            },
            {
              label: "Timezone",
              value: interview.timezone
            },
            {
              label: "Scheduled",
              value: interview.scheduled_at
                ? format(new Date(interview.scheduled_at), "PPP p")
                : "Not scheduled"
            }
          ].map(row => (

            <div key={row.label} className="card">

              <p className="text-xs text-forest-400">
                {row.label}
              </p>

              <p className="font-medium">
                {row.value}
              </p>

            </div>

          ))}

        </div>


        {/* Scores */}

        {interview.scores?.length > 0 && (

          <div className="card mb-5">

            <h2 className="font-display text-lg mb-4">
              Evaluation Scores
            </h2>

            {interview.scores.map(s => (
              <ScoreBar
                key={s.id}
                dimension={s.dimension}
                score={s.score}
                maxScore={s.max_score}
              />
            ))}

          </div>

        )}

      </div>


      {/* Assign Modal */}

      <Modal
        open={showAssign}
        onClose={() => setShowAssign(false)}
        title="Assign Interviewer"
        maxWidth="max-w-md"
      >

        <div className="space-y-4">

            <select
              className="input"
              value={assignForm.slot_id}
              onChange={e => {

                const slot = slotsData?.items?.find(
                  s => s.id === e.target.value
                )

                if (!slot) return

                setAssignForm({
                  interviewer_id: slot.interviewer_id,
                  slot_id: slot.id
                })

              }}
            >

            <option value="">
              Select available slot
            </option>

            {slotsData?.items?.map(slot => (

              <option key={slot.id} value={slot.id}>

                {format(new Date(slot.start_time),"MMM d, h:mma")} — {slot.interviewer_name}

              </option>

            ))}

          </select>

          <button
            onClick={handleAssign}
            disabled={assigning}
            className="btn-primary w-full"
          >
            {assigning
              ? "Assigning..."
              : "Confirm Assignment"}
          </button>

        </div>

      </Modal>


      {/* Cancel Modal */}

      <Modal
        open={showCancel}
        onClose={() => setShowCancel(false)}
        title="Cancel Interview"
      >

        <textarea
          className="input"
          rows={3}
          placeholder="Reason"
          value={cancelReason}
          onChange={e => setCancelReason(e.target.value)}
        />

        <button
          onClick={handleCancel}
          disabled={cancelling}
          className="w-full mt-4 bg-red-600 text-white font-semibold py-3 rounded-xl transition-all duration-200 hover:bg-red-700 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {cancelling ? "Cancelling..." : "Confirm Cancellation"}
        </button>

      </Modal>

    </DashboardLayout>
  )
}