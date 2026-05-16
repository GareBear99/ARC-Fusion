# Validation Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python -m arc_fusion.cli --store /tmp/arc_fusion_v04_smoke smoke
PYTHONPATH=src python -m arc_fusion.cli --store /tmp/arc_fusion_v04_smoke plan-transcode input.mov output.mp4
PYTHONPATH=src python -m arc_fusion.cli --store /tmp/arc_fusion_v04_smoke index-summary
PYTHONPATH=src python -m arc_fusion.cli --store /tmp/arc_fusion_v04_smoke codec-boundaries
```

Expected result for the packaged validation run:

```text
pytest: 7 passed
smoke: ok true
plan-transcode: command plan manifest + receipt emitted
index-summary: manifests and receipts indexed
codec-boundaries: FFmpeg-backed now, native module boundary documented
```
