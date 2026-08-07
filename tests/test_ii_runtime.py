import json
import subprocess
import sys
import unittest

from ii_runtime import II_RUNTIME_DEFINITION, IiRuntime
from ii_runtime.contracts import ControlState, RuntimeCommand
from ii_runtime.registry import build_runtime_definition


class IiRuntimeTests(unittest.TestCase):
    def test_runtime_definition_matches_expected_runtime_id(self):
        definition = build_runtime_definition()
        self.assertEqual(definition.runtime_id, 'ii')
        self.assertIn('terminal-render', definition.capabilities)
        self.assertEqual(II_RUNTIME_DEFINITION.runtime_id, definition.runtime_id)

    def test_runtime_snapshot_reports_active_mode(self):
        runtime = IiRuntime(ControlState(mode='pulse', palette='blood', bpm=128))
        runtime.render_frame(width=20, height=4)
        snapshot = runtime.snapshot()
        self.assertEqual(snapshot.runtime_id, 'ii')
        self.assertEqual(snapshot.active_mode, 'pulse')
        self.assertEqual(snapshot.palette, 'blood')
        self.assertEqual(snapshot.bpm, 128)
        self.assertGreaterEqual(snapshot.metrics['frames'], 1)
        self.assertEqual(snapshot.controls['mode'], 'pulse')
        self.assertTrue(any(field['key'] == 'layer_b_enabled' for field in snapshot.control_schema))
        self.assertTrue(any(group['key'] == 'tempo' for group in snapshot.control_groups))
        self.assertTrue(any(mode['name'] == 'rain' for mode in snapshot.mode_catalog))
        self.assertTrue(any(cue['name'] == 'drive' for cue in snapshot.cue_catalog))

    def test_runtime_frame_has_expected_dimensions(self):
        runtime = IiRuntime(ControlState(mode='text', flash_text='HELLO'))
        frame = runtime.render_frame(width=12, height=5)
        lines = frame.splitlines()
        self.assertEqual(len(lines), 5)
        self.assertTrue(all(len(line) == 12 for line in lines))
        self.assertIn('HELLO', frame)

    def test_runtime_patch_and_command_update_control_state(self):
        runtime = IiRuntime()
        runtime.apply_patch({'palette': 'blood', 'bpm': 999, 'layer_b_enabled': True, 'mode_b': 'rain'})
        runtime.apply_command(RuntimeCommand(kind='mode.set', payload={'mode': 'pulse'}))
        self.assertEqual(runtime.control.palette, 'blood')
        self.assertEqual(runtime.control.bpm, 240)
        self.assertTrue(runtime.control.layer_b_enabled)
        self.assertEqual(runtime.control.mode_b, 'rain')
        self.assertEqual(runtime.control.mode, 'pulse')

    def test_cue_selection_updates_runtime_and_tracks_active_cue(self):
        runtime = IiRuntime()
        cue_name = runtime.select_cue(name='storm')
        self.assertEqual(cue_name, 'storm')
        self.assertEqual(runtime.active_cue_name(), 'storm')
        self.assertEqual(runtime.control.mode, 'pulse')
        self.assertEqual(runtime.control.mode_b, 'rain')
        self.assertTrue(runtime.control.layer_b_enabled)
        runtime.apply_command(RuntimeCommand(kind='cue.advance'))
        self.assertEqual(runtime.active_cue_name(), 'alert')
        self.assertTrue(runtime.control.flash_active)

    def test_layer_b_and_flash_change_the_rendered_frame(self):
        base_runtime = IiRuntime(ControlState(mode='pulse', flash_text='ii'))
        layered_runtime = IiRuntime(
            ControlState(
                mode='pulse',
                mode_b='rain',
                layer_b_enabled=True,
                layer_b_alpha=1.0,
                flash_active=True,
                flash_text='ALERT',
            )
        )
        base_frame = base_runtime.render_frame(width=18, height=6)
        layered_frame = layered_runtime.render_frame(width=18, height=6)
        self.assertNotEqual(base_frame, layered_frame)
        self.assertIn('ALERT', layered_frame)

    def test_cli_snapshot_emits_json(self):
        result = subprocess.run(
            [sys.executable, '-m', 'ii_runtime', 'snapshot', '--mode', 'pulse', '--layer-b', '--mode-b', 'rain'],
            check=True,
            capture_output=True,
            text=True,
            cwd='/home/nooo/_ii',
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload['runtime_id'], 'ii')
        self.assertEqual(payload['active_mode'], 'pulse')
        self.assertTrue(payload['controls']['layer_b_enabled'])

    def test_cli_cue_emits_snapshot_with_active_cue(self):
        result = subprocess.run(
            [sys.executable, '-m', 'ii_runtime', 'cue', '--name', 'storm'],
            check=True,
            capture_output=True,
            text=True,
            cwd='/home/nooo/_ii',
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload['active_cue'], 'storm')
        self.assertEqual(payload['controls']['palette'], 'ember')

    def test_cli_modes_emits_mode_catalog(self):
        result = subprocess.run(
            [sys.executable, '-m', 'ii_runtime', 'modes'],
            check=True,
            capture_output=True,
            text=True,
            cwd='/home/nooo/_ii',
        )
        payload = json.loads(result.stdout)
        self.assertTrue(any(item['name'] == 'rain' for item in payload))

    def test_cli_groups_emits_control_groups(self):
        result = subprocess.run(
            [sys.executable, '-m', 'ii_runtime', 'groups'],
            check=True,
            capture_output=True,
            text=True,
            cwd='/home/nooo/_ii',
        )
        payload = json.loads(result.stdout)
        self.assertTrue(any(item['key'] == 'layering' for item in payload))


if __name__ == '__main__':
    unittest.main()
