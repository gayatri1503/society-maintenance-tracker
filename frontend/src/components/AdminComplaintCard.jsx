import { useState } from "react";
import apiClient from "../api/client";
import StatusHistoryTimeline from "./StatusHistoryTimeline";

const STATUSES = ["Open", "In Progress", "Resolved"];
const PRIORITIES = ["Low", "Medium", "High"];

export default function AdminComplaintCard({ complaint, onUpdate }) {
  const [expanded, setExpanded] = useState(false);
  const [newStatus, setNewStatus] = useState(complaint.current_status);
  const [note, setNote] = useState("");
  const [priority, setPriority] = useState(complaint.priority);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const isResolved = complaint.current_status === "Resolved";

  const handleStatusUpdate = async () => {
    setError("");
    setSaving(true);
    try {
      await apiClient.patch(`/complaints/${complaint.id}/status`, {
        status: newStatus,
        note: note || null,
      });
      setNote("");
      onUpdate();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update status");
    } finally {
      setSaving(false);
    }
  };

  const handlePriorityUpdate = async (e) => {
    const value = e.target.value;
    setPriority(value);
    try {
      await apiClient.patch(`/complaints/${complaint.id}/priority`, { priority: value });
      onUpdate();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update priority");
    }
  };

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
        <span>Resident ID: {complaint.resident_id}</span>
        <span>Raised: {new Date(complaint.created_at).toLocaleDateString()}</span>
      </div>

      <div className="admin-controls">
        <label>
          Priority:
          <select value={priority} onChange={handlePriorityUpdate}>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </label>

        {!isResolved && (
          <div className="status-update">
            <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Note (optional)"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
            <button onClick={handleStatusUpdate} disabled={saving}>
              {saving ? "Updating..." : "Update Status"}
            </button>
          </div>
        )}
        {isResolved && <p className="closed-note">Closed — no further updates allowed</p>}
      </div>

      {error && <p className="error">{error}</p>}

      <button onClick={() => setExpanded(!expanded)}>
        {expanded ? "Hide History" : "View History"}
      </button>
      {expanded && <StatusHistoryTimeline history={complaint.history} />}
    </div>
  );
}