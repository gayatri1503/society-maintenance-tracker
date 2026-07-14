# System Design Write-Up

## Complaint History Model

The core design decision in this system is separating "current state" from "history." Each `Complaint` row holds a `current_status` field — a denormalized cache of the latest status — while a separate `ComplaintStatusHistory` table holds an append-only log of every status change, each row recording the status, timestamp, the acting user (`changed_by`), and an optional note.

This split exists because a single mutable `status` column cannot answer "how did this complaint progress over time," which the spec explicitly requires. If we only stored `current_status`, every update would overwrite the only record of the previous state — the resident would see where a complaint ended up, but never how it got there. By treating history as an insert-only log rather than an update-in-place field, the audit trail is structurally guaranteed to be complete: there is no code path that can silently erase a past entry, because history rows are never updated or deleted, only appended.

Complaint creation itself writes the first history row ("Complaint raised," actor = resident), so a complaint's timeline always starts from its origin, not from the first admin action. `current_status` remains useful as a fast-filterable field for admin queries (`WHERE current_status = 'Open'`) without needing a subquery against the history table on every read — the history table is the source of truth, but the denormalized field keeps common queries cheap. Once a complaint reaches `Resolved`, the status-update endpoint rejects further transitions (HTTP 400), enforced server-side rather than left as a UI convention, so the "closed" state is a real invariant, not just a display choice.

## Overdue Detection

Overdue status is computed at read time rather than stored as a column. A complaint is overdue if it is not yet `Resolved` and its age (`now() - created_at`) exceeds a configurable threshold (`OVERDUE_THRESHOLD_DAYS`, read from environment configuration).

This was a deliberate choice over an alternative design where a background job periodically flips a stored `is_overdue` flag. The computed approach has no risk of staleness — there is no window where the flag is technically wrong because a scheduled job hasn't run yet — and it requires no additional infrastructure (no cron, no task queue) for a project of this scale. The threshold itself lives in configuration rather than code, so it can be tuned per deployment without a schema migration or code change. The tradeoff is that this computation happens in the application layer (Python) rather than the database layer for aggregate counts like the dashboard's `overdue_count`, since "age relative to now" isn't naturally expressible as a simple `GROUP BY`. For the complaint volume a single society realistically generates, this is a negligible cost; a larger-scale version of this system might revisit this as a stored, periodically-refreshed value.

Overdue complaints are surfaced first in the admin's complaint list via a stable secondary sort (overdue first, then by recency within each group), so priority attention items are never buried under a strict recency-only ordering.

## Photo Handling

Complaint photos are optional and, when provided, are uploaded directly to Cloudinary rather than the application server's disk. The backend receives the multipart upload, streams the bytes to Cloudinary, and stores only the resulting HTTPS URL on the `Complaint` row (`photo_url`) — the image itself never touches the server's filesystem or the database.

This matters specifically because the backend is deployed on a free-tier host with an ephemeral filesystem: any file written to local disk would be lost on the next redeploy or restart. Offloading storage to a dedicated service makes the backend stateless with respect to file data, so it can be redeployed, restarted, or scaled without any risk to previously uploaded photos.

## Notification Flow

Two triggers fire transactional emails to residents, both handled synchronously after the relevant database write commits: a complaint's status change emails the owning resident with the new status and any admin note, and posting a notice marked "important" emails every resident in the system.

Email sending is deliberately best-effort, not transactional with the core action it's attached to: if the email provider is briefly unavailable or a send fails for any reason, that failure is caught and logged server-side, but it never rolls back or blocks the underlying status update or notice creation. The core state change in the database is the source of truth; the email is a side effect that should not be able to break the primary action. A synchronous call (rather than a queued background job) was chosen for simplicity at this scale — for a higher-volume deployment, this would move to an async task queue to avoid adding email-provider latency to the request/response cycle.