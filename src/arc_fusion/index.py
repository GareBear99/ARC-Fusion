from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Iterable
import json, sqlite3, time

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS manifests (
  manifest_hash TEXT PRIMARY KEY,
  payload_hash TEXT,
  label TEXT,
  mime_type TEXT,
  size_bytes INTEGER,
  merkle_root TEXT,
  manifest_path TEXT,
  created_at_unix INTEGER
);
CREATE TABLE IF NOT EXISTS receipts (
  receipt_hash TEXT PRIMARY KEY,
  event_type TEXT,
  receipt_path TEXT,
  created_at_unix INTEGER
);
CREATE TABLE IF NOT EXISTS media_jobs (
  job_hash TEXT PRIMARY KEY,
  operation TEXT,
  input_manifest_hash TEXT,
  output_manifest_hash TEXT,
  plan_hash TEXT,
  receipt_hash TEXT,
  status TEXT,
  created_at_unix INTEGER
);
"""

def db_path(store: Path) -> Path:
    p = store / "indexes" / "arc_fusion_index.sqlite"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def init_index(store: Path) -> Dict[str, Any]:
    db = db_path(store)
    with sqlite3.connect(db) as con:
        con.executescript(SCHEMA_SQL)
    return {"ok": True, "db": str(db)}

def index_manifest(store: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
    init_index(store)
    with sqlite3.connect(db_path(store)) as con:
        con.execute("""INSERT OR REPLACE INTO manifests(manifest_hash,payload_hash,label,mime_type,size_bytes,merkle_root,manifest_path,created_at_unix) VALUES(?,?,?,?,?,?,?,?)""", (
            manifest.get("manifest_hash"), manifest.get("payload_hash"), manifest.get("label"), manifest.get("mime_type"), manifest.get("size_bytes"), manifest.get("merkle_root"), manifest.get("manifest_path"), manifest.get("created_at_unix")
        ))
    return {"ok": True, "manifest_hash": manifest.get("manifest_hash")}

def index_receipt(store: Path, receipt: Dict[str, Any]) -> Dict[str, Any]:
    init_index(store)
    with sqlite3.connect(db_path(store)) as con:
        con.execute("""INSERT OR REPLACE INTO receipts(receipt_hash,event_type,receipt_path,created_at_unix) VALUES(?,?,?,?)""", (
            receipt.get("receipt_hash"), receipt.get("event_type"), receipt.get("receipt_path"), receipt.get("created_at_unix")
        ))
    return {"ok": True, "receipt_hash": receipt.get("receipt_hash")}

def index_job(store: Path, job: Dict[str, Any]) -> Dict[str, Any]:
    init_index(store)
    with sqlite3.connect(db_path(store)) as con:
        con.execute("""INSERT OR REPLACE INTO media_jobs(job_hash,operation,input_manifest_hash,output_manifest_hash,plan_hash,receipt_hash,status,created_at_unix) VALUES(?,?,?,?,?,?,?,?)""", (
            job.get("job_hash"), job.get("operation"), job.get("input_manifest_hash"), job.get("output_manifest_hash"), job.get("plan_hash"), job.get("receipt_hash"), job.get("status"), job.get("created_at_unix", int(time.time()))
        ))
    return {"ok": True, "job_hash": job.get("job_hash")}

def summarize_index(store: Path) -> Dict[str, Any]:
    init_index(store)
    with sqlite3.connect(db_path(store)) as con:
        cur = con.cursor()
        counts = {}
        for t in ["manifests", "receipts", "media_jobs"]:
            counts[t] = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    return {"ok": True, "db": str(db_path(store)), "counts": counts}
