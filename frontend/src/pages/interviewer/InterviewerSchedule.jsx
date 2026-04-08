import { useState } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import scheduleService from '../../services/scheduleService'
import { useFetch } from '../../hooks'
import { EmptyState, PageSpinner, ConfirmDialog } from '../../components/ui'
import toast from 'react-hot-toast'
import { format, parseISO } from 'date-fns'

export default function InterviewerSchedule() {
  const { data, loading, refetch } = useFetch(() => scheduleService.listSlots({ available_only: false, per_page: 50 }))
  const slots = data?.items || []

  const [form, setForm] = useState({ start_time: '', end_time: '', timezone: Intl.DateTimeFormat().resolvedOptions().timeZone })
  const [adding,    setAdding]    = useState(false)
  const [deleting,  setDeleting]  = useState(null)
  const [confirmId, setConfirmId] = useState(null)

  const handleAdd = async (e) => {
    e.preventDefault()
    if (!form.start_time || !form.end_time) { toast.error('Both start and end times are required'); return }
    if (new Date(form.end_time) <= new Date(form.start_time)) { toast.error('End time must be after start time'); return }
    setAdding(true)
    try {
      await scheduleService.addSlot({
        start_time: new Date(form.start_time).toISOString(),
        end_time:   new Date(form.end_time).toISOString(),
        timezone:   form.timezone,
      })
      toast.success('Availability slot added!')
      setForm(f => ({ ...f, start_time: '', end_time: '' }))
      refetch()
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Failed to add slot')
    } finally {
      setAdding(false)
    }
  }

  const handleDelete = async () => {
    if (!confirmId) return
    setDeleting(confirmId)
    try {
      await scheduleService.deleteSlot(confirmId)
      toast.success('Slot removed')
      refetch()
    } catch {
      toast.error('Failed to delete slot')
    } finally {
      setDeleting(null)
      setConfirmId(null)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Interviewer</p>
          <h1 className="font-display text-3xl text-forest-900">My Schedule</h1>
          <p className="text-forest-500 text-sm mt-1">Add windows when you're available to conduct interviews</p>
        </div>

        {/* Add slot form */}
        <div className="card shadow-card-hover mb-6">
          <h2 className="font-display text-lg text-forest-900 mb-4">Add Availability Slot</h2>
          <form onSubmit={handleAdd} className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="label">Start time</label>
                <input className="input" type="datetime-local"
                  value={form.start_time} onChange={e => setForm(f => ({ ...f, start_time: e.target.value }))} required />
              </div>
              <div>
                <label className="label">End time</label>
                <input className="input" type="datetime-local"
                  value={form.end_time} onChange={e => setForm(f => ({ ...f, end_time: e.target.value }))} required />
              </div>
            </div>
            <div>
              <label className="label">Timezone</label>
              <input className="input" value={form.timezone}
                onChange={e => setForm(f => ({ ...f, timezone: e.target.value }))} />
            </div>
            <button type="submit" disabled={adding} className="btn-primary">
              {adding ? 'Adding…' : '+ Add Slot'}
            </button>
          </form>
        </div>

        {/* Slots list */}
        <div className="card">
          <h2 className="font-display text-lg text-forest-900 mb-4">
            Your Slots <span className="text-forest-400 text-sm font-sans font-normal">({slots.length})</span>
          </h2>
          {loading ? <PageSpinner /> : slots.length === 0 ? (
            <EmptyState icon="📅" title="No slots yet"
              description="Add your availability windows above so recruiters can book you" />
          ) : (
            <div className="space-y-2">
              {slots.sort((a,b) => new Date(a.start_time) - new Date(b.start_time)).map(slot => (
                <div key={slot.id}
                  className={`flex items-center gap-4 p-3.5 rounded-xl border ${
                    slot.is_booked ? 'border-forest-200 bg-forest-50' : 'border-cream-200 hover:border-forest-300'
                  } transition-colors`}>
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${slot.is_booked ? 'bg-amber-400' : 'bg-green-500'}`} />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-forest-900 text-sm">
                      {format(parseISO(slot.start_time), 'EEE, MMM d · h:mm a')} — {format(parseISO(slot.end_time), 'h:mm a')}
                    </p>
                    <p className="text-forest-400 text-xs mt-0.5">{slot.timezone}</p>
                  </div>
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                    slot.is_booked ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                  }`}>
                    {slot.is_booked ? 'Booked' : 'Available'}
                  </span>
                  {!slot.is_booked && (
                    <button onClick={() => setConfirmId(slot.id)}
                      className="text-red-400 hover:text-red-600 text-xs font-medium transition-colors ml-1">
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={!!confirmId}
        onClose={() => setConfirmId(null)}
        onConfirm={handleDelete}
        title="Remove Slot"
        message="Are you sure you want to remove this availability slot?"
        confirmLabel="Remove"
        danger
      />
    </DashboardLayout>
  )
}
