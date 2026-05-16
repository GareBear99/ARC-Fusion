# Validation Report

Generated locally.

## pytest

Return code: `0`

```text
[32m.[0m[32m.[0m[32m.[0m[32m                                                                      [100%][0m
[32m[32m[1m3 passed[0m[32m in 0.28s[0m[0m

Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/generated/interface/models.py", line 48821, in hydrate_crdt_from_proto
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/rpc/remote.py", line 747, in __call__
  File "/tmp/tmp.9eeVjt35CN/artifact_tool_v2-2.7.5/artifact_tool/rpc/client.py", line 150, in call
artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.

```

## arc-fusion smoke

Return code: `0`

```json
{
  "ok": true,
  "receipt_hash": "sha256:ce563f8788e0b925e1bce0078438c0d36b43795a5c1504509c4b7c4de35ffb6c",
  "verify": {
    "merkle_ok": true,
    "missing": [],
    "ok": true,
    "payload_ok": true
  }
}

```

## doctor

Return code: `0`

```json
{
  "arc_fusion": "0.3.0",
  "ffmpeg": true,
  "ffprobe": true,
  "store": "/mnt/data/ARC_Fusion_repo_complete_v0_3_0/_smoke_store"
}

```
