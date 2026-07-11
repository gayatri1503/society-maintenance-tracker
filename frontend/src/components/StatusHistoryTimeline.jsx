export default function StatusHistoryTimeline({ history }) {
  const sorted = [...history].sort(
    (a, b) => new Date(a.changed_at) - new Date(b.changed_at)
  );

  return (
    <ul className="timeline">
      {sorted.map((entry) => (
        <li key={entry.id} className={`timeline-item status-${entry.status.replace(" ", "-")}`}>
          <div className="timeline-status">{entry.status}</div>
          <div className="timeline-date">
            {new Date(entry.changed_at).toLocaleString()}
          </div>
          {entry.note && <div className="timeline-note">{entry.note}</div>}
        </li>
      ))}
    </ul>
  );
}