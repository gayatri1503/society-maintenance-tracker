import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import apiClient from "../api/client";
import ComplaintCard from "../components/ComplaintCard";
import { useAuth } from "../context/AuthContext";

export default function ResidentDashboard() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { user, logout } = useAuth();

  useEffect(() => {
    apiClient
      .get("/complaints/me")
      .then((res) => setComplaints(res.data))
      .catch(() => setError("Failed to load complaints"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <h2>Welcome, {user?.name}</h2>
        <div>
          <Link to="/notices">Notice Board</Link>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <Link to="/raise-complaint" className="primary-button">
        + Raise New Complaint
      </Link>

      <h3>My Complaints</h3>
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && complaints.length === 0 && <p>No complaints raised yet.</p>}

      <div className="complaint-list">
        {complaints.map((c) => (
          <ComplaintCard key={c.id} complaint={c} />
        ))}
      </div>
    </div>
  );
}