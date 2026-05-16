# Security Policy

ARC-Fusion handles untrusted media paths and may execute FFmpeg. Treat media files as untrusted inputs.

Current security posture:

- no shell=True command execution
- FFmpeg command arguments are passed as lists
- binary objects are hash verified
- receipts are hash addressed
- signing/encryption are roadmap items for the next layer

Do not run ARC-Fusion on hostile media without sandboxing FFmpeg in production.
