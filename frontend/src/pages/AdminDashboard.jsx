import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import apiClient from "../api/client";
import { useAuth } from "../context/AuthContext";
import AdminComplaintCard from "../components/AdminComplaintCard";

const CATEGORIES = ["Plumbing", "Electrical", "Cleaning", "Security", "Parking", "Other"];
const STATUSES = ["Open", "In Progress", "Resolved"];

export default function AdminDashboard() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({ category: "", status: "", date_from: "", date_to: "" });
  const { user, logout } = useAuth();

  const fetchComplaints = () => {
    setLoading(true);
    const params = {};
    if (filters.category) params.category = filters.category;
    if (filters.status) params.status = filters.status;
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;

    apiClient
      .get("/complaints", { params })
      .then((res) => setComplaints(res.data))
      .catch(() => setError("Failed to load complaints"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchComplaints();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  return (
    <div className="page">
      <header className="page-header">
        <h2>Admin — {user?.name}</h2>
        <div>
          <Link to="/dashboard-stats">Stats</Link>
          <Link to="/notices">Notice Board</Link>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <div className="filters">
        <select
          value={filters.category}
          onChange={(e) => setFilters({ ...filters, category: e.target.value })}
        >
          <option value="">All Categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
        >
          <option value="">All Statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <label>
          From: <input
            type="date"
            value={filters.date_from}
            onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
          />
        </label>
        <label>
          To: <input
            type="date"
            value={filters.date_to}
            onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
          />
        </label>
      </div>

      <h3>All Complaints ({complaints.length})</h3>
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}

      <div className="complaint-list">
        {complaints.map((c) => (
          <AdminComplaintCard key={c.id} complaint={c} onUpdate={fetchComplaints} />
        ))}
      </div>
    </div>
  );
}