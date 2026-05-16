# Language Module and LLMBuilder Hooks

ARC-Fusion does not invent labels. It emits source-backed lineage rows so OCR, captions, transcripts, or human annotations can attach later.

Future rows should bind:

```text
annotation -> language object hash -> source frame hash -> source video hash -> receipt chain
```

This keeps datasets auditable and prevents silent synthetic contamination.
