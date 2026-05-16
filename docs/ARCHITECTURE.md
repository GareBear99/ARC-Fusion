# ARC-Fusion Architecture

ARC-Fusion is designed as the media execution lane for ARC-Apache. In phase one, FFmpeg/FFprobe remain the execution backend. ARC-Fusion adds deterministic plans, binary storage, cryptographic receipts, and integration contracts.

## Pipeline

```text
input media
  -> ffprobe metadata
  -> command plan
  -> ffmpeg extraction/transcode
  -> binary object packing
  -> stream timeline
  -> media receipt
  -> ARC-Core registration
```

## Why this exists

FFmpeg transforms media. ARC-Fusion transforms media and makes the operation provable, replayable, referenceable, and usable as AI memory.

## Canonical truth

The canonical truth is not the JSON view. The canonical truth is the binary object and its proof chain:

```text
payload bytes -> chunk hashes -> Merkle root -> manifest hash -> receipt hash
```

## Future native replacement path

1. wrapper and proof layer
2. deterministic binary media store
3. StreamMemory extraction
4. language/transcript/OCR hooks
5. LLMBuilder dataset generation
6. Proto-Synth visualization
7. custom filters
8. custom lightweight codecs
9. ARC-native media runtime
