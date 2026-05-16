"""
ARC-Core integration stub for ARC-Fusion / ARC-Apache binary payload authority.

Drop this into ARC-Core when ready and adapt the database dependency names.
The route does not store media bytes. It stores canonical authority references:
payload_hash, manifest_hash, merkle_root, receipt_hash, source system, policy status.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/arc-apache", tags=["arc-apache"])

class PayloadRegistration(BaseModel):
    source_system: str = Field(..., examples=["arc-fusion", "arc-language-module", "streammemory", "llmbuilder"])
    payload_hash: str
    manifest_hash: str
    merkle_root: str
    receipt_hash: str
    label: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None

@router.post("/payloads/register")
def register_payload(payload: PayloadRegistration):
    # TODO: Replace with ARC-Core receipt DB insert + policy checks.
    # Required DB invariants:
    # 1. payload_hash unique or idempotent.
    # 2. manifest_hash and receipt_hash immutable.
    # 3. source_system must be allowlisted by ARC authority policy.
    # 4. never store raw bytes here.
    return {
        "ok": True,
        "authority_event_type": "arc_apache.payload.registered",
        "registered": payload.model_dump(),
    }
