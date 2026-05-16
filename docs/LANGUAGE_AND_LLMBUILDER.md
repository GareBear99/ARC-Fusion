# Language Module and LLMBuilder

## Language Module

Use:

```bash
arc-fusion mirror-language ../arc-language-module --store .arc_fusion_store
```

This mirrors language files as binary objects. The language module becomes part of the same verifiable memory plane as media and model artifacts.

## LLMBuilder

`export-llmbuilder` emits lineage rows only. It does not invent captions or labels.

Future adapters may add:

- OCR
- transcription
- captioning
- frame descriptions
- scene summaries

Each generated label must trace back to source payload hashes and model/adapter receipts.
