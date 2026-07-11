import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import apiClient from "../api/client";

export default function DashboardStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiClient
      .get("/dashboard")
      .then((res) => setStats(res.data))
      .catch(() => setError("Failed to load dashboard stats"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page">Loading...</div>;
  if (error) return <div className="page error">{error}</div>;

  return (
    <div className="page">
      <header className="page-header">
        <h2>Dashboard</h2>
        <Link to="/admin">← Back to Complaints</Link>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-number">{stats.total_complaints}</span>
          <span className="stat-label">Total Complaints</span>
        </div>
        <div className="stat-card overdue">
          <span className="stat-number">{stats.overdue_count}</span>
          <span className="stat-label">Overdue</span>
        </div>
      </div>

      <h3>By Status</h3>
      <div className="stats-grid">
        {Object.entries(stats.by_status).map(([status, count]) => (
          <div key={status} className="stat-card small">
            <span className="stat-number">{count}</span>
            <span className="stat-label">{status}</span>
          </div>
        ))}
      </div>

      <h3>By Category</h3>
      <div className="stats-grid">
        {Object.entries(stats.by_category).map(([category, count]) => (
          <div key={category} className="stat-card small">
            <span className="stat-number">{count}</span>
            <span className="stat-label">{category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}