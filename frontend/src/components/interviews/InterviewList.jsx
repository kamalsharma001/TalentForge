import { Link } from "react-router-dom"
import { StatusBadge } from "../ui"
import { format } from "date-fns"

export default function InterviewList({ interviews, role }) {

  return (
    <div className="space-y-3">
      {interviews.map(iv => (
        <Link
          key={iv.id}
          to={`/interviews/${iv.id}`}
          className="flex items-center gap-4 p-4 rounded-xl border border-cream-200 hover:border-forest-300 hover:bg-cream-50 transition-colors"
        >

          <div className="w-10 h-10 bg-forest-100 rounded-xl flex items-center justify-center text-forest-700 font-bold text-xs">
            {(iv.tech_stack?.[0] || "GEN").slice(0,3).toUpperCase()}
          </div>

          <div className="flex-1 min-w-0">
            <p className="font-semibold text-forest-900 text-sm truncate">
              {iv.title}
            </p>

            <p className="text-forest-500 text-xs mt-0.5">
              {iv.scheduled_at
                ? format(new Date(iv.scheduled_at), "MMM d, yyyy · h:mma")
                : "Not yet scheduled"}
            </p>
          </div>

          <StatusBadge status={iv.status} />

          {/* Role specific actions */}

          {role === "interviewer" && iv.status === "scheduled" && iv.meeting_link && (
            <a
              href={iv.meeting_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs bg-amber-400 text-forest-900 font-bold px-3 py-1.5 rounded-full hover:bg-amber-300"
              onClick={e => e.stopPropagation()}
            >
              Join
            </a>
          )}

          {role === "interviewer" && iv.status === "report_pending" && (
            <Link
              to={`/interviewer/reports?interview=${iv.id}`}
              className="text-xs bg-forest-900 text-white font-semibold px-3 py-1.5 rounded-full hover:bg-forest-800"
              onClick={e => e.stopPropagation()}
            >
              Submit Report
            </Link>
          )}

        </Link>
      ))}
    </div>
  )
}