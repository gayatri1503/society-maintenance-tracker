import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import apiClient from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function NoticeBoard() {
  const [notices, setNotices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [isImportant, setIsImportant] = useState(false);
  const [error, setError] = useState("");
  const [posting, setPosting] = useState(false);
  const { user } = useAuth();

  const fetchNotices = () => {
    setLoading(true);
    apiClient
      .get("/notices")
      .then((res) => setNotices(res.data))
      .catch(() => setError("Failed to load notices"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchNotices();
  }, []);

  const handlePost = async (e) => {
    e.preventDefault();
    setError("");
    setPosting(true);
    try {
      await apiClient.post("/notices", { title, body, is_important: isImportant });
      setTitle("");
      setBody("");
      setIsImportant(false);
      fetchNotices();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to post notice");
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h2>Notice Board</h2>
        <Link to={user?.role === "admin" ? "/admin" : "/"}>← Back to Dashboard</Link>
      </header>

      {user?.role === "admin" && (
        <form className="notice-form" onSubmit={handlePost}>
          <h3>Post a Notice</h3>
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <textarea
            placeholder="Body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            required
            rows={3}
          />
          <label>
            <input
              type="checkbox"
              checked={isImportant}
              onChange={(e) => setIsImportant(e.target.checked)}
            />
            Mark as important (pins to top, emails all residents)
          </label>
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={posting}>
            {posting ? "Posting..." : "Post Notice"}
          </button>
        </form>
      )}

      {loading && <p>Loading...</p>}
      <div className="notice-list">
        {notices.map((n) => (
          <div key={n.id} className={`notice-card ${n.is_important ? "important" : ""}`}>
            {n.is_important && <span className="pin-badge">📌 Important</span>}
            <h4>{n.title}</h4>
            <p>{n.body}</p>
            <span className="notice-date">{new Date(n.created_at).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}