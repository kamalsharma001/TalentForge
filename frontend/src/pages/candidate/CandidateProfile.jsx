import { useState } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import { userService } from '../../services/userService'
import { Avatar } from '../../components/ui'
import toast from 'react-hot-toast'

export default function CandidateProfile() {
  const { user, refreshUser } = useAuth()
  const [form,    setForm]    = useState({ first_name: user?.first_name || '', last_name: user?.last_name || '', phone: user?.phone || '' })
  const [loading, setLoading] = useState(false)

  const handleSave = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await userService.updateMe(form)
      await refreshUser()
      toast.success('Profile updated!')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-xl mx-auto animate-fade-in">
        <div className="mb-6">
          <p className="section-label">Candidate</p>
          <h1 className="font-display text-3xl text-forest-900">My Profile</h1>
        </div>
        <div className="card">
          <div className="flex items-center gap-4 mb-6 pb-5 border-b border-cream-200">
            <Avatar name={`${user?.first_name} ${user?.last_name}`} url={user?.avatar_url} size="xl" />
            <div>
              <p className="font-display text-xl text-forest-900">{user?.first_name} {user?.last_name}</p>
              <p className="text-forest-500 text-sm">{user?.email}</p>
              <span className="badge-green mt-1 inline-flex capitalize">{user?.role}</span>
            </div>
          </div>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">First name</label>
                <input className="input" value={form.first_name} onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))} />
              </div>
              <div>
                <label className="label">Last name</label>
                <input className="input" value={form.last_name} onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))} />
              </div>
            </div>
            <div>
              <label className="label">Phone</label>
              <input className="input" type="tel" placeholder="+1 (555) 000-0000" value={form.phone}
                onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} />
            </div>
            <div>
              <label className="label">Email (read-only)</label>
              <input className="input bg-cream-100 cursor-not-allowed" value={user?.email} readOnly />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-3">
              {loading ? 'Saving…' : 'Save changes'}
            </button>
          </form>
        </div>
      </div>
    </DashboardLayout>
  )
}
