import { useState } from "react"
import DashboardLayout from "../../components/layout/DashboardLayout"
import { useFetch, useInterviews } from "../../hooks"
import { userService } from "../../services/userService"
import interviewService from "../../services/interviewService"

import {
  StatCard,
  Avatar,
  Badge,
  StatusBadge,
  EmptyState,
  PageSpinner,
  ConfirmDialog
} from "../../components/ui"

import { DashboardHeader, StatsCard, DashboardPanel, QuickActionCard, PanelEmptyState } from "../../components/dashboard/DashboardParts"

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

        <DashboardHeader
          label="Admin Dashboard"
          heading="Welcome, Admin 👋"
          description="Manage platform operations and monitor activity."
          illustration="admin"
        />

        {/* Stats */}

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">

          <StatsCard
            title="Total Users"
            value={usersData?.total || 0}
            icon="👥"
            subtitle="Registered accounts"
            variant="green"
          />

          <StatsCard
            title="Active Interviews"
            value={scheduledInterviews.length}
            icon="📅"
            subtitle="Scheduled interviews"
          />

          <StatsCard
            title="Completed Interviews"
            value={completedInterviews.length}
            icon="✅"
            subtitle="Interviews completed"
          />

          <StatsCard
            title="Platform Activity"
            value={interviews.length}
            icon="📊"
            subtitle="Total interviews"
            variant="amber"
          />

        </div>

        <div className="grid lg:grid-cols-2 gap-5 mb-5">

          {/* Recent Activity */}
          <DashboardPanel title="Recent Activity" actionLabel="View all" actionTo="/admin/interviews">
            {interviews.length === 0 ? (
              <PanelEmptyState icon="📊" title="No activity yet" description="Platform activity will show up here" />
            ) : (
              <div className="space-y-2">
                {interviews.slice(0, 5).map(iv => (
                  <div key={iv.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-cream-50 transition-colors">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-forest-900 truncate">{iv.title}</p>
                      <p className="text-xs text-forest-400">{iv.job_role || "—"}</p>
                    </div>
                    <StatusBadge status={cleanStatus(iv.status)} />
                  </div>
                ))}
              </div>
            )}
          </DashboardPanel>

          {/* Pending Assignments */}
          <DashboardPanel title="Pending Assignments" actionLabel="View all" actionTo="/admin/interviews">
            {pendingInterviews.length === 0 ? (
              <PanelEmptyState
                icon="📋"
                title="No interviews waiting for assignment"
              />
            ) : (
              <div className="space-y-2">
                {pendingInterviews.slice(0, 5).map(iv => (
                  <div
                    key={iv.id}
                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-cream-50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-forest-900 truncate">
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
                        className="text-xs bg-forest-900 text-white px-3 py-1.5 rounded-full hover:bg-forest-800 flex-shrink-0"
                      >
                        Assign
                      </Link>
                    )}
                  </div>
                ))}
              </div>
            )}
          </DashboardPanel>

        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <QuickActionCard
            to="/admin/users"
            icon="👥"
            title="Manage Users"
            description="View, promote, or deactivate platform users."
          />
          <QuickActionCard
            to="/admin/interviews"
            icon="📋"
            title="View Interviews"
            description="Review and assign all platform interviews."
            tone="amber"
          />
        </div>

      </div>

    </DashboardLayout>
  )
}



/* ================= ADMIN USERS PAGE ================= */

export function AdminUsers() {
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const { data, loading, refetch } = useFetch(
    () => userService.listUsers({
      per_page: 100,
      ...(roleFilter ? { role: roleFilter } : {}),
      ...(statusFilter ? { approval_status: statusFilter } : {})
    }),
    [roleFilter, statusFilter]
  )

  const users = data?.items || []

  const handleApprove = async (userId) => {
    try {
      await userService.approveUser(userId)
      toast.success("User approved successfully")
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || "Failed to approve user")
    }
  }

  const handleReject = async (userId) => {
    try {
      await userService.rejectUser(userId)
      toast.success("User rejected successfully")
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || "Failed to reject user")
    }
  }

  const handleDelete = async () => {
    if (!confirmDelete) return
    setIsDeleting(true)
    try {
      await userService.deleteUser(confirmDelete)
      toast.success("User deleted successfully")
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || "Failed to delete user")
    } finally {
      setIsDeleting(false)
      setConfirmDelete(null)
    }
  }

  const getStatusBadge = (status) => {
    switch (status?.toUpperCase()) {
      case 'APPROVED':
        return <Badge variant="green">Approved</Badge>
      case 'PENDING':
        return <Badge variant="warning">Pending</Badge>
      case 'REJECTED':
        return <Badge variant="danger">Rejected</Badge>
      default:
        return <Badge variant="gray">{status}</Badge>
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto animate-fade-in">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <p className="section-label">Admin</p>
            <h1 className="font-display text-3xl text-forest-900">Manage Users</h1>
            <p className="text-forest-500 text-sm mt-1">Verify accounts and manage platform permissions.</p>
          </div>
        </div>

        {/* Filter controls */}
        <div className="card mb-6 flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px]">
            <label className="label">Filter by Role</label>
            <select
              value={roleFilter}
              onChange={e => setRoleFilter(e.target.value)}
              className="input"
            >
              <option value="">All Roles</option>
              <option value="recruiter">Recruiter</option>
              <option value="interviewer">Interviewer</option>
              <option value="candidate">Candidate</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div className="flex-1 min-w-[200px]">
            <label className="label">Filter by Status</label>
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="input"
            >
              <option value="">All Statuses</option>
              <option value="APPROVED">Approved</option>
              <option value="PENDING">Pending</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>

        {/* Users list */}
        <div className="card shadow-card">
          {loading ? (
            <PageSpinner />
          ) : users.length === 0 ? (
            <EmptyState
              icon="👥"
              title="No users found"
              description="Try adjusting your filters or search criteria."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-cream-100 text-xs font-semibold uppercase text-forest-500">
                    <th className="pb-3 pl-2">User</th>
                    <th className="pb-3">Role</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3 text-right pr-2">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cream-100 text-sm">
                  {users.map(u => (
                    <tr key={u.id} className="hover:bg-cream-50/50 transition-colors">
                      <td className="py-4 pl-2">
                        <div className="flex items-center gap-3">
                          <Avatar name={u.full_name} size="sm" />
                          <div>
                            <p className="font-semibold text-forest-900">{u.full_name}</p>
                            <p className="text-xs text-forest-500 font-mono">{u.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 capitalize font-medium text-forest-700">
                        {u.role}
                      </td>
                      <td className="py-4">
                        {getStatusBadge(u.approval_status)}
                      </td>
                      <td className="py-4 text-right pr-2">
                        <div className="flex items-center justify-end gap-2">
                          {(u.role === 'recruiter' || u.role === 'interviewer') && (
                            <>
                              {u.approval_status !== 'APPROVED' && (
                                <button
                                  onClick={() => handleApprove(u.id)}
                                  className="px-2.5 py-1 text-xs font-semibold bg-emerald-100 text-emerald-800 rounded-lg hover:bg-emerald-200 transition-colors"
                                >
                                  Approve
                                </button>
                              )}
                              {u.approval_status !== 'REJECTED' && (
                                <button
                                  onClick={() => handleReject(u.id)}
                                  className="px-2.5 py-1 text-xs font-semibold bg-amber-100 text-amber-800 rounded-lg hover:bg-amber-200 transition-colors"
                                >
                                  Reject
                                </button>
                              )}
                            </>
                          )}
                          {u.role !== 'admin' && (
                            <button
                              onClick={() => setConfirmDelete(u.id)}
                              className="px-2.5 py-1 text-xs font-semibold bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                            >
                              Delete
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        onConfirm={handleDelete}
        title="Delete User Account"
        message="Are you sure you want to permanently delete this user account? This will cascade-delete their profile, availability, and associated interview reports."
        confirmLabel={isDeleting ? "Deleting..." : "Permanently Delete"}
        danger
      />
    </DashboardLayout>
  )
}



/* ================= ADMIN INTERVIEWS PAGE ================= */

export function AdminInterviews() {
  const { data, loading, refetch } = useInterviews({ per_page: 80 })
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [confirmCancel, setConfirmCancel] = useState(null)
  const [cancelReason, setCancelReason] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [activeTab, setActiveTab] = useState('all')

  const cleanStatus = (status) => status?.split(".").pop()
  const interviews = data?.items || []

  const upcoming = interviews.filter(iv => ['pending', 'scheduled'].includes(cleanStatus(iv.status)))
  const completedList = interviews.filter(iv => ['completed', 'report_pending'].includes(cleanStatus(iv.status)))
  const cancelled = interviews.filter(iv => cleanStatus(iv.status) === 'cancelled')

  let displayedInterviews = []
  if (activeTab === 'all') displayedInterviews = interviews
  else if (activeTab === 'upcoming') displayedInterviews = upcoming
  else if (activeTab === 'completed') displayedInterviews = completedList
  else if (activeTab === 'cancelled') displayedInterviews = cancelled

  const tabs = [
    { id: 'all', label: 'All', count: interviews.length },
    { id: 'upcoming', label: 'Upcoming', count: upcoming.length },
    { id: 'completed', label: 'Completed', count: completedList.length },
    { id: 'cancelled', label: 'Cancelled', count: cancelled.length }
  ]

  const handleDelete = async () => {
    if (!confirmDelete) return
    setIsProcessing(true)
    try {
      await interviewService.delete(confirmDelete)
      toast.success("Interview deleted successfully")
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || "Failed to delete interview")
    } finally {
      setIsProcessing(false)
      setConfirmDelete(null)
    }
  }

  const handleCancel = async () => {
    if (!confirmCancel) return
    if (!cancelReason.trim()) {
      toast.error("Please provide a reason for cancellation")
      return
    }
    setIsProcessing(true)
    try {
      await interviewService.cancel(confirmCancel, cancelReason)
      toast.success("Interview cancelled successfully")
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || "Failed to cancel interview")
    } finally {
      setIsProcessing(false)
      setConfirmCancel(null)
      setCancelReason('')
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto animate-fade-in">
        <div className="flex justify-between items-center mb-6">
          <div>
            <p className="section-label">Admin</p>
            <h1 className="font-display text-3xl text-forest-900 mb-1">All Interviews</h1>
            <p className="text-forest-500 text-sm">Monitor, assign, cancel, or delete all platform interviews.</p>
          </div>
        </div>

        {/* Tab Selection */}
        <div className="flex border-b border-cream-200 gap-6 mb-6">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 text-sm font-semibold transition-all relative ${
                activeTab === tab.id
                  ? 'text-forest-900 border-b-2 border-forest-900'
                  : 'text-forest-400 hover:text-forest-600'
              }`}
            >
              {tab.label}
              <span className="ml-1.5 px-2 py-0.5 text-xs bg-cream-100 rounded-full text-forest-600">
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        <div className="card shadow-card">
          {loading ? (
            <PageSpinner />
          ) : displayedInterviews.length === 0 ? (
            <EmptyState
              icon="📋"
              title="No interviews found"
              description="No interviews have been requested yet."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-cream-100 text-xs font-semibold uppercase text-forest-500">
                    <th className="pb-3 pl-2">Interview Details</th>
                    <th className="pb-3">Candidate</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3 text-right pr-2">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cream-100 text-sm">
                  {displayedInterviews.map(iv => {
                    const statusStr = cleanStatus(iv.status)
                    return (
                      <tr key={iv.id} className="hover:bg-cream-50/50 transition-colors">
                        <td className="py-4 pl-2">
                          <div>
                            <p className="font-semibold text-forest-900">{iv.title}</p>
                            <p className="text-xs text-forest-500 mt-0.5">
                              {iv.job_role || "Technical Interview"} · {iv.scheduled_at ? new Date(iv.scheduled_at).toLocaleString() : "Not scheduled"}
                            </p>
                          </div>
                        </td>
                        <td className="py-4 font-medium text-forest-700">
                          {iv.candidate_email || "—"}
                        </td>
                        <td className="py-4">
                          <StatusBadge status={statusStr} />
                        </td>
                        <td className="py-4 text-right pr-2">
                          <div className="flex items-center justify-end gap-2">
                            <Link
                              to={`/interviews/${iv.id}`}
                              className="px-2.5 py-1 text-xs font-semibold bg-forest-50 text-forest-700 rounded-lg hover:bg-forest-100 transition-colors"
                            >
                              View
                            </Link>
                            {statusStr !== 'cancelled' && statusStr !== 'completed' && (
                              <button
                                onClick={() => setConfirmCancel(iv.id)}
                                className="px-2.5 py-1 text-xs font-semibold bg-amber-50 text-amber-700 rounded-lg hover:bg-amber-100 transition-colors"
                              >
                                Cancel
                              </button>
                            )}
                            <button
                              onClick={() => setConfirmDelete(iv.id)}
                              className="px-2.5 py-1 text-xs font-semibold bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        onConfirm={handleDelete}
        title="Delete Interview"
        message="Are you sure you want to permanently delete this interview? If an interviewer was assigned to a slot, that slot will be released and marked as available."
        confirmLabel={isProcessing ? "Deleting..." : "Permanently Delete"}
        danger
      />

      {confirmCancel && (
        <div className="fixed inset-0 bg-forest-950/20 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-cream-100">
            <h3 className="font-display text-lg font-semibold text-forest-900 mb-2">Cancel Interview</h3>
            <p className="text-forest-500 text-sm mb-4">Please provide a reason for cancelling this interview. This action will notify both parties and release any reserved slots.</p>
            <textarea
              value={cancelReason}
              onChange={e => setCancelReason(e.target.value)}
              placeholder="e.g. Schedule conflict, recruiter request..."
              className="input resize-none w-full mb-4"
              rows={3}
              required
            />
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => {
                  setConfirmCancel(null)
                  setCancelReason('')
                }}
                className="btn-secondary"
                disabled={isProcessing}
              >
                Go Back
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="btn-primary bg-amber-600 hover:bg-amber-700"
                disabled={isProcessing}
              >
                {isProcessing ? "Cancelling..." : "Confirm Cancellation"}
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  )
}



export default AdminDashboard