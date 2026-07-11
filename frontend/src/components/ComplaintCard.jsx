import { useState } from "react";
import StatusHistoryTimeline from "./StatusHistoryTimeline";

export default function ComplaintCard({ complaint }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`complaint-card ${complaint.is_overdue ? "overdue" : ""}`}>
      <div className="complaint-header">
        <span className="category">{complaint.category}</span>
        <span className={`status-badge status-${complaint.current_status.replace(" ", "-")}`}>
          {complaint.current_status}
        </span>
        {complaint.is_overdue && <span className="overdue-badge">Overdue</span>}
      </div>

      <p className="description">{complaint.description}</p>

      {complaint.photo_url && (
        <img src={complaint.photo_url} alt="Complaint" className="complaint-photo" />
      )}

      <div className="complaint-meta">
        <span>Priority: {complaint.priority}</span>
        <span>Raised: {new Date(complaint.created_at).toLocaleDateString()}</span>
      </div>

      <button onClick={() => setExpanded(!expanded)}>
        {expanded ? "Hide History" : "View History"}
      </button>

      {expanded && <StatusHistoryTimeline history={complaint.history} />}
    </div>
  );
}