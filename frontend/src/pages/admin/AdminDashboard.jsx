import { useState } from "react"
import DashboardLayout from "../../components/layout/DashboardLayout"
import { useFetch, useInterviews } from "../../hooks"
import { userService } from "../../services/userService"

import {
  StatCard,
  Avatar,
  Badge,
  StatusBadge,
  EmptyState,
  PageSpinner,
  ConfirmDialog
} from "../../components/ui"

import toast from "react-hot-toast"
import { format } from "date-fns"
import { Link } from "react-router-dom"



/* ================= ADMIN DASHBOARD ================= */

export function AdminDashboard() {

  const { data: usersData } = useFetch(
    () => userService.listUsers({ per_page: 100 }),
    []
  )

  const { data: intData } = useInterviews({ per_page: 100 })

  const cleanStatus = (status) => status?.split(".").pop()

  const users = usersData?.items || []
  const interviews = intData?.items || []
  console.log(interviews)

  const pendingInterviews = interviews.filter(i => {
  const status = cleanStatus(i.status)
  return status === "pending"
  })

  const scheduledInterviews = interviews.filter(
    i => cleanStatus(i.status) === "scheduled"
  )

  const completedInterviews = interviews.filter(
    i => cleanStatus(i.status) === "completed"
  )

  return (
    <DashboardLayout>

      <div className="max-w-6xl mx-auto animate-fade-in">

        {/* Header */}

        <div className="mb-8">
          <p className="section-label">Admin</p>
          <h1 className="font-display text-3xl text-forest-900">
            Platform Overview
          </h1>
        </div>


        {/* Stats */}

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">

          <StatCard
            label="Total Users"
            value={usersData?.total || 0}
            icon="👥"
            variant="green"
          />

          <StatCard
            label="Total Interviews"
            value={interviews.length}
            icon="📋"
          />

          <StatCard
            label="Scheduled Interviews"
            value={scheduledInterviews.length}
            icon="📅"
          />

          <StatCard
            label="Completed Interviews"
            value={completedInterviews.length}
            icon="✅"
          />

        </div>



        {/* Pending Interviews */}

        <div className="card">

          <div className="flex items-center justify-between mb-4">

            <h2 className="font-display text-lg text-forest-900">
              Interviews Awaiting Assignment
            </h2>

            <Link
              to="/admin/interviews"
              className="text-forest-600 text-sm hover:text-forest-900"
            >
              View all →
            </Link>

          </div>


          {pendingInterviews.length === 0 ? (

            <EmptyState
              icon="📋"
              title="No interviews waiting for assignment"
            />

          ) : (

            <div className="space-y-2">

              {pendingInterviews.slice(0,5).map(iv => (

                <div
                  key={iv.id}
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-cream-50"
                >

                  <div className="flex-1 min-w-0">

                    <p className="text-sm font-medium text-forest-900">
                      {iv.title}
                    </p>

                    <p className="text-xs text-forest-400">
                      {iv.job_role || "—"}
                    </p>

                  </div>

                  <StatusBadge status={cleanStatus(iv.status)} />

                  {cleanStatus(iv.status) === "pending" && (
                    <Link
                      to={`/interviews/${iv.id}`}
                      className="text-xs bg-forest-900 text-white px-3 py-1.5 rounded-full hover:bg-forest-800"
                    >
                      Assign
                    </Link>
                  )}

                </div>

              ))}

            </div>

          )}

        </div>

      </div>

    </DashboardLayout>
  )
}



/* ================= ADMIN USERS PAGE ================= */

export function AdminUsers() {

  const { data, loading, refetch } =
    useFetch(() => userService.listUsers({ per_page: 50 }), [])

  const users = data?.items || []

  const [confirmDeactivate, setConfirmDeactivate] = useState(null)

  const handleDeactivate = async () => {

    if (!confirmDeactivate) return

    try {

      await userService.deactivate(confirmDeactivate)

      toast.success("User deactivated")

      refetch()

    } catch {

      toast.error("Failed")

    }

  }

  return (
    <DashboardLayout>

      <div className="max-w-6xl mx-auto">

        <h1 className="font-display text-3xl text-forest-900 mb-6">
          Users
        </h1>

        <div className="card">

          {loading ? (

            <PageSpinner />

          ) : (

            users.map(u => (

              <div
                key={u.id}
                className="flex justify-between items-center border-b p-3"
              >

                <div className="flex items-center gap-2">

                  <Avatar name={u.full_name} size="sm" />

                  <div>
                    <p className="font-medium">
                      {u.full_name}
                    </p>
                    <p className="text-xs text-forest-500">
                      {u.email}
                    </p>
                  </div>

                </div>

                <Badge variant="gray">
                  {u.role}
                </Badge>

              </div>

            ))

          )}

        </div>

      </div>

      <ConfirmDialog
        open={!!confirmDeactivate}
        onClose={() => setConfirmDeactivate(null)}
        onConfirm={handleDeactivate}
        title="Deactivate User"
        message="This user will lose access."
        confirmLabel="Deactivate"
        danger
      />

    </DashboardLayout>
  )
}



/* ================= ADMIN INTERVIEWS PAGE ================= */

export function AdminInterviews() {

  const { data, loading } = useInterviews({ per_page: 50 })

  const cleanStatus = (status) => status?.split(".").pop()
  
  const interviews = data?.items || []

  return (

    <DashboardLayout>

      <div className="max-w-6xl mx-auto">

        <h1 className="font-display text-3xl text-forest-900 mb-6">
          All Interviews
        </h1>

        <div className="card">

          {loading ? (

            <PageSpinner />

          ) : (

            interviews.map(iv => (

              <div
                key={iv.id}
                className="flex justify-between items-center border-b p-3"
              >

                <div>

                  <p className="font-medium">
                    {iv.title}
                  </p>

                  <p className="text-xs text-forest-500">
                    {iv.job_role || "—"}
                  </p>

                </div>

                <StatusBadge status={cleanStatus(iv.status)} />

                <Link
                  to={`/interviews/${iv.id}`}
                  className="text-forest-600 text-xs font-medium"
                >
                  View →
                </Link>

              </div>

            ))

          )}

        </div>

      </div>

    </DashboardLayout>

  )
}



export default AdminDashboard