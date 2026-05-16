from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from . import __version__
from .binary_store import BinaryStore
from .ffmpeg_tools import which_ffmpeg, probe_media, extract_frames, extract_audio_preview, plan_ingest
from .receipts import make_receipt, write_receipt
from .stream_memory import build_timeline
from .sure import make_sure_recipe
from .llmbuilder import export_dataset_rows
from .crypto_utils import keygen, sign_json, verify_signed_json
from .language_bindings import mirror_language_path

def jprint(obj):
    print(json.dumps(obj, indent=2, sort_keys=True))

def cmd_doctor(args):
    jprint({'ok': True, 'version': __version__, 'binaries': which_ffmpeg()})

def cmd_init_store(args):
    BinaryStore(Path(args.store)); jprint({'ok': True, 'store': args.store})

def cmd_keygen(args):
    jprint(keygen(args.private_key, args.public_key))

def cmd_pack(args):
    m = BinaryStore(Path(args.store)).pack_file(args.path, media_type=args.media_type, source=args.source)
    jprint(m)

def cmd_verify(args):
    store = BinaryStore(Path(args.store)); m = store.load_manifest(args.manifest); jprint(store.verify_manifest(m))

def cmd_restore(args):
    store = BinaryStore(Path(args.store)); m = store.load_manifest(args.manifest); jprint({'ok': True, 'output': store.restore_manifest(m, args.output)})

def cmd_probe(args):
    probe = probe_media(args.path)
    if args.store:
        store = BinaryStore(Path(args.store))
        manifest = store.write_json_as_object(probe, f'probe/{Path(args.path).name}.ffprobe.json', source='ffprobe')
        receipt = make_receipt('arc_fusion.media.probe', {'input': args.path, 'probe_manifest_hash': manifest['manifest_hash']}, 'ok' if probe.get('ok') else 'error')
        rpath = write_receipt(args.store, receipt)
        probe['arc_fusion'] = {'probe_manifest': manifest, 'receipt_path': rpath, 'receipt_hash': receipt['receipt_hash']}
    jprint(probe)

def cmd_ingest(args):
    store = BinaryStore(Path(args.store))
    work = Path(args.work); work.mkdir(parents=True, exist_ok=True)
    input_manifest = store.pack_file(args.path, logical_name=f'input/{Path(args.path).name}', source='arc-fusion.ingest')
    probe = probe_media(args.path)
    probe_manifest = store.write_json_as_object(probe, f'probe/{Path(args.path).name}.json', source='ffprobe')
    plan = plan_ingest(args.path, fps=args.fps, extract_audio=not args.no_audio)
    plan_manifest = store.write_json_as_object(plan, f'plans/{Path(args.path).name}.plan.json', source='arc-fusion.plan')
    frame_result = extract_frames(args.path, work / 'frames', fps=args.fps, limit=args.frame_limit)
    frame_manifests = [store.pack_file(f, logical_name=f'frames/{Path(f).name}', media_type='image/jpeg', source='ffmpeg.frame') for f in frame_result.get('frames', [])]
    audio_manifest = None; audio_result = None
    if not args.no_audio:
        audio_result = extract_audio_preview(args.path, work / 'audio_preview.wav')
        if audio_result.get('ok') and audio_result.get('output'):
            audio_manifest = store.pack_file(audio_result['output'], logical_name='audio/audio_preview.wav', media_type='audio/wav', source='ffmpeg.audio')
    timeline = build_timeline(input_manifest, probe_manifest, frame_manifests, audio_manifest)
    timeline_manifest = store.write_json_as_object(timeline, f'timelines/{Path(args.path).name}.timeline.json', source='arc-fusion.streammemory')
    receipt = make_receipt('arc_fusion.media.ingest', {
        'input_manifest_hash': input_manifest['manifest_hash'],
        'probe_manifest_hash': probe_manifest['manifest_hash'],
        'plan_manifest_hash': plan_manifest['manifest_hash'],
        'timeline_manifest_hash': timeline_manifest['manifest_hash'],
        'frame_count': len(frame_manifests),
        'audio_manifest_hash': (audio_manifest or {}).get('manifest_hash'),
        'ffmpeg': which_ffmpeg(),
    }, 'ok')
    rpath = write_receipt(args.store, receipt)
    if args.sign_private_key:
        signed = sign_json(receipt, args.sign_private_key)
        Path(rpath).write_text(json.dumps(signed, indent=2, sort_keys=True), encoding='utf-8')
    jprint({'ok': True, 'input_manifest': input_manifest, 'timeline_manifest': timeline_manifest, 'receipt_path': rpath, 'receipt_hash': receipt['receipt_hash'], 'frames': len(frame_manifests), 'ffmpeg_frame_result': frame_result, 'ffmpeg_audio_result': audio_result})

def cmd_receipt(args):
    payload = json.loads(Path(args.payload_json).read_text(encoding='utf-8')) if args.payload_json else {}
    r = make_receipt(args.event_type, payload, args.status)
    if args.store:
        path = write_receipt(args.store, r); r['receipt_path'] = path
    jprint(r)

def cmd_sign_receipt(args):
    obj = json.loads(Path(args.receipt).read_text(encoding='utf-8'))
    signed = sign_json(obj, args.private_key)
    Path(args.output or args.receipt).write_text(json.dumps(signed, indent=2, sort_keys=True), encoding='utf-8')
    jprint({'ok': True, 'output': args.output or args.receipt})

def cmd_verify_receipt(args):
    obj = json.loads(Path(args.receipt).read_text(encoding='utf-8'))
    jprint(verify_signed_json(obj, args.public_key))

def cmd_sure(args):
    params = json.loads(Path(args.params).read_text(encoding='utf-8')) if args.params else {}
    recipe = make_sure_recipe(args.generator_id, args.seed, params, args.expected_output_hash)
    if args.store:
        m = BinaryStore(Path(args.store)).write_json_as_object(recipe, f'sure/{recipe["recipe_hash"]}.json', source='sure-recipe')
        recipe['manifest_hash'] = m['manifest_hash']
    jprint(recipe)

def cmd_mirror_language(args):
    jprint(mirror_language_path(args.store, args.path))

def cmd_export_llmbuilder(args):
    timeline = json.loads(Path(args.timeline_json).read_text(encoding='utf-8'))
    jprint(export_dataset_rows(timeline, args.output))

def cmd_smoke(args):
    store = BinaryStore(Path(args.store)); sample = Path(args.store) / 'smoke.txt'; sample.write_text('arc-fusion smoke', encoding='utf-8')
    m = store.pack_file(sample, logical_name='smoke.txt', source='smoke')
    v = store.verify_manifest(m)
    r = make_receipt('arc_fusion.smoke', {'manifest_hash': m['manifest_hash']}, 'ok' if v['ok'] else 'error')
    write_receipt(args.store, r)
    jprint({'ok': v['ok'], 'manifest_hash': m['manifest_hash'], 'receipt_hash': r['receipt_hash']})
    return 0 if v['ok'] else 1

def build_parser():
    p = argparse.ArgumentParser(prog='arc-fusion')
    sub = p.add_subparsers(dest='cmd', required=True)
    def add_store(sp): sp.add_argument('--store', default='.arc_fusion_store')
    s=sub.add_parser('doctor'); s.set_defaults(func=cmd_doctor)
    s=sub.add_parser('init-store'); add_store(s); s.set_defaults(func=cmd_init_store)
    s=sub.add_parser('keygen'); s.add_argument('--private-key', default='arc_fusion_ed25519_private.pem'); s.add_argument('--public-key', default='arc_fusion_ed25519_public.pem'); s.set_defaults(func=cmd_keygen)
    s=sub.add_parser('pack'); s.add_argument('path'); add_store(s); s.add_argument('--media-type', default='application/octet-stream'); s.add_argument('--source', default='manual'); s.set_defaults(func=cmd_pack)
    s=sub.add_parser('verify'); s.add_argument('manifest'); add_store(s); s.set_defaults(func=cmd_verify)
    s=sub.add_parser('restore'); s.add_argument('manifest'); add_store(s); s.add_argument('--output'); s.set_defaults(func=cmd_restore)
    s=sub.add_parser('probe'); s.add_argument('path'); s.add_argument('--store'); s.set_defaults(func=cmd_probe)
    s=sub.add_parser('ingest'); s.add_argument('path'); add_store(s); s.add_argument('--work', default='.arc_fusion_work'); s.add_argument('--fps', type=float, default=1.0); s.add_argument('--frame-limit', type=int, default=12); s.add_argument('--no-audio', action='store_true'); s.add_argument('--sign-private-key'); s.set_defaults(func=cmd_ingest)
    s=sub.add_parser('receipt'); s.add_argument('--event-type', default='arc_fusion.manual'); s.add_argument('--payload-json'); s.add_argument('--status', default='ok'); s.add_argument('--store'); s.set_defaults(func=cmd_receipt)
    s=sub.add_parser('sign-receipt'); s.add_argument('receipt'); s.add_argument('--private-key', required=True); s.add_argument('--output'); s.set_defaults(func=cmd_sign_receipt)
    s=sub.add_parser('verify-receipt'); s.add_argument('receipt'); s.add_argument('--public-key', required=True); s.set_defaults(func=cmd_verify_receipt)
    s=sub.add_parser('sure-recipe'); s.add_argument('--generator-id', required=True); s.add_argument('--seed', required=True); s.add_argument('--params'); s.add_argument('--expected-output-hash'); s.add_argument('--store'); s.set_defaults(func=cmd_sure)
    s=sub.add_parser('mirror-language'); s.add_argument('path'); add_store(s); s.set_defaults(func=cmd_mirror_language)
    s=sub.add_parser('export-llmbuilder'); s.add_argument('timeline_json'); s.add_argument('--output', required=True); s.set_defaults(func=cmd_export_llmbuilder)
    s=sub.add_parser('smoke'); add_store(s); s.set_defaults(func=cmd_smoke)
    return p

def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args) or 0

if __name__ == '__main__':
    raise SystemExit(main())
