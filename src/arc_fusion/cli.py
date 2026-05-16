from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from .binary_store import BinaryStore
from .ffmpeg_tools import ffmpeg_versions, probe, extract_frames, extract_audio_preview
from .receipts import make_receipt, write_receipt
from .stream_memory import build_timeline
from .sure import make_sure_recipe
from .llmbuilder import export_llmbuilder_dataset


def _print(obj):
    print(json.dumps(obj, indent=2, sort_keys=True))


def cmd_doctor(args):
    _print({'ok': True, 'ffmpeg': ffmpeg_versions()})


def cmd_probe(args):
    store = BinaryStore(Path(args.store)); store.init()
    result = probe(Path(args.input))
    packed = store.write_bytes_object(json.dumps(result, sort_keys=True).encode('utf-8'), logical_name=f'{Path(args.input).name}.ffprobe.json', content_type='application/json')
    receipt = make_receipt('arc_fusion.media.probe', 'ok' if result.get('ok') else 'error', {'probe_manifest_hash': packed.manifest_hash, 'input': args.input})
    rp = write_receipt(receipt, store.receipts)
    _print({'probe_ok': result.get('ok'), 'probe_manifest': str(packed.manifest_path), 'receipt': str(rp)})


def cmd_ingest(args):
    store = BinaryStore(Path(args.store)); store.init()
    inp = Path(args.input)
    job_dir = store.jobs / f'ingest_{inp.stem}'
    job_dir.mkdir(parents=True, exist_ok=True)

    input_obj = store.pack_file(inp)
    probe_result = probe(inp)
    probe_obj = store.write_bytes_object(json.dumps(probe_result, sort_keys=True).encode('utf-8'), logical_name=f'{inp.name}.ffprobe.json', content_type='application/json')

    frame_objects = []
    frame_result = {'ok': False, 'skipped': True}
    if args.fps is not None:
        frame_dir = job_dir / 'frames'
        frame_result = extract_frames(inp, frame_dir, float(args.fps))
        for idx, fp in enumerate(sorted(frame_dir.glob('frame_*.png'))):
            obj = store.pack_file(fp, logical_name=f'{inp.name}.frame.{idx:06d}.png')
            frame_objects.append({'index': idx, 'payload_hash': obj.payload_hash, 'manifest_hash': obj.manifest_hash, 'merkle_root': obj.merkle_root})

    audio_object = None
    audio_result = {'ok': False, 'skipped': True}
    if args.audio:
        wav = job_dir / 'audio_preview.wav'
        audio_result = extract_audio_preview(inp, wav)
        if wav.exists():
            obj = store.pack_file(wav, logical_name=f'{inp.name}.audio_preview.wav')
            audio_object = {'payload_hash': obj.payload_hash, 'manifest_hash': obj.manifest_hash, 'merkle_root': obj.merkle_root}

    input_manifest = {'payload_hash': input_obj.payload_hash, 'manifest_hash': input_obj.manifest_hash}
    probe_manifest = {'payload_hash': probe_obj.payload_hash, 'manifest_hash': probe_obj.manifest_hash}
    timeline = build_timeline(input_manifest, probe_manifest, frame_objects, audio_object)
    timeline_obj = store.write_bytes_object(json.dumps(timeline, sort_keys=True).encode('utf-8'), logical_name=f'{inp.name}.stream_timeline.json', content_type='application/json')

    data = {
        'input_payload_hash': input_obj.payload_hash,
        'input_manifest_hash': input_obj.manifest_hash,
        'probe_manifest_hash': probe_obj.manifest_hash,
        'timeline_manifest_hash': timeline_obj.manifest_hash,
        'frame_count': len(frame_objects),
        'audio': audio_object,
        'ffmpeg': ffmpeg_versions(),
        'frame_result_ok': frame_result.get('ok'),
        'audio_result_ok': audio_result.get('ok'),
    }
    receipt = make_receipt('arc_fusion.media.ingest', 'ok', data)
    rp = write_receipt(receipt, store.receipts)
    _print({'ok': True, 'input_manifest': str(input_obj.manifest_path), 'timeline_manifest': str(timeline_obj.manifest_path), 'receipt': str(rp), 'frame_count': len(frame_objects)})


def cmd_receipt(args):
    store = BinaryStore(Path(args.store)); store.init()
    job = json.loads(Path(args.job).read_text(encoding='utf-8'))
    receipt = make_receipt(args.event_type, args.status, job)
    rp = write_receipt(receipt, store.receipts)
    _print({'ok': True, 'receipt': str(rp), 'receipt_hash': receipt['receipt_hash']})


def cmd_sure_recipe(args):
    params = json.loads(Path(args.params).read_text(encoding='utf-8')) if args.params else {}
    recipe = make_sure_recipe(args.generator, args.seed, params, args.expected_output_hash)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(recipe, indent=2, sort_keys=True), encoding='utf-8')
    _print(recipe)


def cmd_export_llmbuilder(args):
    timeline = json.loads(Path(args.timeline).read_text(encoding='utf-8'))
    _print(export_llmbuilder_dataset(timeline, Path(args.out)))


def cmd_smoke(args):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        sample = td / 'sample.txt'
        sample.write_text('arc fusion smoke\n', encoding='utf-8')
        store = BinaryStore(td / 'store'); store.init()
        obj = store.pack_file(sample)
        ver = store.verify_manifest(obj.manifest_path)
        restored = store.restore(obj.manifest_path, td / 'restored.txt')
        if not (ver.get('ok') and restored.get('ok')):
            _print({'ok': False, 'verify': ver, 'restore': restored})
            return 1
    _print({'ok': True, 'message': 'ARC-Fusion smoke test passed'})
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog='arc-fusion')
    sub = p.add_subparsers(dest='cmd', required=True)

    sp = sub.add_parser('doctor'); sp.set_defaults(func=cmd_doctor)

    sp = sub.add_parser('probe'); sp.add_argument('input'); sp.add_argument('--store', default='.arc_fusion_store'); sp.set_defaults(func=cmd_probe)

    sp = sub.add_parser('ingest'); sp.add_argument('input'); sp.add_argument('--store', default='.arc_fusion_store'); sp.add_argument('--fps', default='1'); sp.add_argument('--audio', action='store_true'); sp.add_argument('--receipt', action='store_true'); sp.set_defaults(func=cmd_ingest)

    sp = sub.add_parser('receipt'); sp.add_argument('--job', required=True); sp.add_argument('--store', default='.arc_fusion_store'); sp.add_argument('--event-type', default='arc_fusion.custom'); sp.add_argument('--status', default='ok'); sp.set_defaults(func=cmd_receipt)

    sp = sub.add_parser('sure-recipe'); sp.add_argument('--generator', required=True); sp.add_argument('--seed', required=True); sp.add_argument('--params'); sp.add_argument('--expected-output-hash'); sp.add_argument('--out'); sp.set_defaults(func=cmd_sure_recipe)

    sp = sub.add_parser('export-llmbuilder'); sp.add_argument('--timeline', required=True); sp.add_argument('--out', required=True); sp.set_defaults(func=cmd_export_llmbuilder)

    sp = sub.add_parser('smoke'); sp.set_defaults(func=cmd_smoke)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    res = args.func(args)
    if isinstance(res, int):
        return res
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
