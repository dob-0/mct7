"""CLI entrypoint for the clean ii scaffold."""

import argparse
import json

from .contracts import ControlState
from .engine import IiRuntime


def emit_json(payload: object) -> int:
    print(json.dumps(payload, indent=2))
    return 0


def add_control_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--mode')
    parser.add_argument('--mode-b')
    parser.add_argument('--layer-b', action='store_true')
    parser.add_argument('--layer-b-alpha', type=float)
    parser.add_argument('--palette')
    parser.add_argument('--bpm', type=int)
    parser.add_argument('--blackout', action='store_true')
    parser.add_argument('--flash-active', action='store_true')
    parser.add_argument('--flash-text')
    parser.add_argument('--master-dim', type=float)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='python -m ii_runtime')
    sub = parser.add_subparsers(dest='command', required=True)

    snapshot = sub.add_parser('snapshot')
    add_control_arguments(snapshot)

    frame = sub.add_parser('frame')
    add_control_arguments(frame)
    frame.add_argument('--width', type=int, default=40)
    frame.add_argument('--height', type=int, default=10)

    sub.add_parser('modes')
    sub.add_parser('controls')
    sub.add_parser('groups')
    sub.add_parser('cues')

    cue = sub.add_parser('cue')
    cue_group = cue.add_mutually_exclusive_group(required=True)
    cue_group.add_argument('--name')
    cue_group.add_argument('--index', type=int)
    cue_group.add_argument('--next', action='store_true')
    cue_group.add_argument('--previous', action='store_true')

    return parser


def build_patch(args: argparse.Namespace) -> dict[str, object]:
    patch: dict[str, object] = {}
    if getattr(args, 'mode', None):
        patch['mode'] = args.mode
    if getattr(args, 'mode_b', None):
        patch['mode_b'] = args.mode_b
    if getattr(args, 'layer_b', False):
        patch['layer_b_enabled'] = True
    if getattr(args, 'layer_b_alpha', None) is not None:
        patch['layer_b_alpha'] = args.layer_b_alpha
    if getattr(args, 'palette', None):
        patch['palette'] = args.palette
    if getattr(args, 'bpm', None) is not None:
        patch['bpm'] = args.bpm
    if getattr(args, 'blackout', False):
        patch['blackout'] = True
    if getattr(args, 'flash_active', False):
        patch['flash_active'] = True
    if getattr(args, 'flash_text', None):
        patch['flash_text'] = args.flash_text
    if getattr(args, 'master_dim', None) is not None:
        patch['master_dim'] = args.master_dim
    return patch


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    runtime = IiRuntime(control=ControlState())
    patch = build_patch(args)
    if patch:
        runtime.apply_patch(patch)

    if args.command == 'snapshot':
        return emit_json(runtime.snapshot().to_dict())

    if args.command == 'frame':
        print(runtime.render_frame(width=max(1, args.width), height=max(1, args.height)))
        return 0

    if args.command == 'modes':
        return emit_json(runtime.available_modes())

    if args.command == 'controls':
        return emit_json(runtime.control_schema())

    if args.command == 'groups':
        return emit_json(runtime.control_groups())

    if args.command == 'cues':
        return emit_json(runtime.available_cues())

    if args.command == 'cue':
        if args.next:
            runtime.advance_cue()
        elif args.previous:
            runtime.previous_cue()
        else:
            runtime.select_cue(name=args.name, index=args.index)
        return emit_json(runtime.snapshot().to_dict())

    parser.error(f'unknown command: {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
