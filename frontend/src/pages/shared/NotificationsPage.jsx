import { useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useNotifications } from '../../hooks'
import { PageSpinner, EmptyState } from '../../components/ui'
import { formatDistanceToNow } from 'date-fns'

const TYPE_META = {
  interview_scheduled: { icon: '📅', color: 'bg-blue-100 text-blue-700'   },
  interview_assigned:  { icon: '🎙️', color: 'bg-forest-100 text-forest-700' },
  report_ready:        { icon: '📊', color: 'bg-amber-100 text-amber-700'  },
  default:             { icon: '🔔', color: 'bg-cream-200 text-forest-600' },
}

export default function NotificationsPage() {
  const { notifications, unreadCount, loading, markRead, markAllRead } = useNotifications()
  const [filter, setFilter] = useState('all') // all | unread

  const displayed = filter === 'unread'
    ? notifications.filter(n => !n.is_read)
    : notifications

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto animate-fade-in">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="section-label">Notifications</p>
            <h1 className="font-display text-3xl text-forest-900">
              Inbox
              {unreadCount > 0 && (
                <span className="ml-3 text-base font-sans font-bold bg-amber-400 text-forest-900 px-2.5 py-0.5 rounded-full">
                  {unreadCount}
                </span>
              )}
            </h1>
          </div>
          {unreadCount > 0 && (
            <button onClick={markAllRead}
              className="btn-ghost text-sm text-forest-500 hover:text-forest-900">
              Mark all read ✓
            </button>
          )}
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 mb-5">
          {[
            { v: 'all',    label: `All (${notifications.length})` },
            { v: 'unread', label: `Unread (${unreadCount})` },
          ].map(tab => (
            <button key={tab.v} onClick={() => setFilter(tab.v)}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                filter === tab.v
                  ? 'bg-forest-900 text-white border-forest-900'
                  : 'bg-white border-cream-300 text-forest-600 hover:border-forest-600'
              }`}>
              {tab.label}
            </button>
          ))}
        </div>

        {/* List */}
        <div className="card divide-y divide-cream-100">
          {loading ? (
            <PageSpinner />
          ) : displayed.length === 0 ? (
            <EmptyState
              icon="🔔"
              title={filter === 'unread' ? 'All caught up!' : 'No notifications yet'}
              description={filter === 'unread' ? 'You have no unread notifications' : 'Notifications will appear here'}
            />
          ) : (
            displayed.map(notif => {
              const meta = TYPE_META[notif.type] || TYPE_META.default
              return (
                <div
                  key={notif.id}
                  className={`flex items-start gap-4 p-4 transition-colors ${
                    !notif.is_read ? 'bg-amber-50/60' : 'hover:bg-cream-50'
                  }`}
                >
                  {/* Icon */}
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center text-base flex-shrink-0 ${meta.color}`}>
                    {meta.icon}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className={`text-sm leading-snug ${!notif.is_read ? 'font-semibold text-forest-900' : 'font-medium text-forest-800'}`}>
                        {notif.title}
                      </p>
                      {!notif.is_read && (
                        <span className="w-2 h-2 rounded-full bg-amber-400 flex-shrink-0 mt-1.5" />
                      )}
                    </div>
                    <p className="text-forest-500 text-xs mt-0.5 leading-relaxed">{notif.message}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-forest-400 text-xs">
                        {formatDistanceToNow(new Date(notif.created_at), { addSuffix: true })}
                      </span>
                      {notif.action_url && (
                        <Link to={notif.action_url}
                          className="text-forest-700 text-xs font-semibold hover:text-forest-900 hover:underline">
                          View →
                        </Link>
                      )}
                      {!notif.is_read && (
                        <button
                          onClick={() => markRead(notif.id)}
                          className="text-forest-400 text-xs hover:text-forest-700 transition-colors">
                          Mark read
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* Empty unread state with CTA */}
        {!loading && filter === 'unread' && unreadCount === 0 && notifications.length > 0 && (
          <div className="text-center mt-4">
            <button onClick={() => setFilter('all')} className="btn-ghost text-sm">
              View all notifications →
            </button>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
