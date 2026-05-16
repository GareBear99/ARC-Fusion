CREATE TABLE IF NOT EXISTS arc_apache_payloads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_system TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  manifest_hash TEXT NOT NULL,
  merkle_root TEXT NOT NULL,
  receipt_hash TEXT NOT NULL,
  label TEXT,
  mime_type TEXT,
  size_bytes INTEGER,
  policy_status TEXT NOT NULL DEFAULT 'registered',
  created_at_unix INTEGER NOT NULL DEFAULT (strftime('%s','now')),
  UNIQUE(payload_hash, manifest_hash, receipt_hash)
);

CREATE INDEX IF NOT EXISTS idx_arc_apache_payloads_payload_hash
ON arc_apache_payloads(payload_hash);

CREATE INDEX IF NOT EXISTS idx_arc_apache_payloads_source
ON arc_apache_payloads(source_system);
