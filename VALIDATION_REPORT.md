# Validation Report

Package: ARC-Fusion v0.4.0

Validated paths:

- Binary pack / verify / restore
- CLI smoke
- Deterministic transcode plan creation
- SQLite manifest/receipt index creation
- Codec boundary manifest generation
- Receipt signing path inherited from v0.3

Honest limitation:

- Transcode execution depends on local FFmpeg availability.
- Output byte identity may vary across FFmpeg builds; receipts record backend version for this reason.
- OCR/transcription/captioning remain adapter boundaries, not claimed functionality.
