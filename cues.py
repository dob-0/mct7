#!/usr/bin/env python3
"""_ii | cues.py — Named cue list with load/save/advance."""

import json
import os

from architecture import BASE

CUES_PATH = os.path.join(BASE, 'cues.json')

BUILTIN = [
    # ── Branding / scene-setters ─────────────────────────────────────────────
    {'name': 'MUTATION',   'mode': 18, 'palette': 6},
    {'name': 'EYE',        'mode': 22, 'palette': 6, 'frame_delay': 0.04},
    {'name': 'OPENER',     'mode': 0,  'palette': 2, 'rain_density': 0.4,  'frame_delay': 0.06},
    {'name': 'PEAK',       'mode': 3,  'palette': 6, 'strobe_speed': 3,    'bpm_sync': True},
    {'name': 'BLACKOUT',   'mode': 0,  'palette': 6, 'blackout': True},

    # ── LINE UP stage ────────────────────────────────────────────────────────
    {'name': 'BAK',        'mode': 13, 'palette': 6, 'glitch_intensity': 0.6,  'wave_amplitude': 0.45},
    {'name': 'LYUPEN',     'mode': 7,  'palette': 6, 'frame_delay': 0.03},
    {'name': 'PINKSTAR',   'mode': 8,  'palette': 7, 'wave_amplitude': 0.50},
    {'name': 'KATE J',     'mode': 9,  'palette': 5, 'frame_delay': 0.035},
    {'name': 'SUBVOID',    'mode': 2,  'palette': 6, 'glitch_intensity': 0.9,  'layer_b_enabled': True, 'mode_b': 13, 'layer_b_alpha': 0.5},

    # ── STUDIO stage ─────────────────────────────────────────────────────────
    {'name': 'ICECHAIN',   'mode': 17, 'palette': 2, 'layer_b_enabled': True,  'mode_b': 16, 'layer_b_alpha': 0.55},
    {'name': 'OOrt',       'mode': 16, 'palette': 5, 'frame_delay': 0.055},
    {'name': 'SZG',        'mode': 15, 'palette': 6, 'frame_delay': 0.03},
    {'name': 'SCHESSEE',   'mode': 8,  'palette': 6, 'wave_amplitude': 0.40},
    {'name': 'RED VELVET', 'mode': 9,  'palette': 7, 'frame_delay': 0.03},
    {'name': 'VULKANSKI',  'mode': 7,  'palette': 5, 'frame_delay': 0.028},

    # ── BAR room ─────────────────────────────────────────────────────────────
    {'name': 'BAR',        'mode': 0,  'palette': 6, 'rain_density': 0.6,  'frame_delay': 0.05},
    {'name': 'BUZZAND',    'mode': 5,  'palette': 7, 'frame_delay': 0.04},
    {'name': 'PILLZ',      'mode': 11, 'palette': 6, 'frame_delay': 0.04},
]


class CueList:
    """Named preset list. Each cue is a dict of control overrides plus a 'name' key."""

    def __init__(self):
        self.cues = []
        self.idx = 0
        self.load()

    def load(self):
        try:
            with open(CUES_PATH) as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                self.cues = data
                return
        except Exception:
            pass
        self.cues = list(BUILTIN)

    def save(self):
        try:
            with open(CUES_PATH, 'w') as f:
                json.dump(self.cues, f, indent=2)
        except Exception:
            pass

    def current_params(self):
        """Return cue overrides (name key stripped)."""
        if not self.cues:
            return {}
        c = dict(self.cues[self.idx % len(self.cues)])
        c.pop('name', None)
        return c

    def name(self):
        if not self.cues:
            return ''
        return self.cues[self.idx % len(self.cues)].get('name', f'CUE{self.idx + 1}')

    def advance(self):
        if self.cues:
            self.idx = (self.idx + 1) % len(self.cues)

    def prev(self):
        if self.cues:
            self.idx = (self.idx - 1) % len(self.cues)

    def go(self, n):
        if self.cues:
            self.idx = int(n) % len(self.cues)

    def store(self, name, overrides):
        """Store overrides as a named cue. Replaces existing cue with same name."""
        cue = {'name': name}
        cue.update({k: v for k, v in overrides.items() if not k.startswith('_')})
        for i, c in enumerate(self.cues):
            if c.get('name') == name:
                self.cues[i] = cue
                self.save()
                return
        self.cues.append(cue)
        self.idx = len(self.cues) - 1
        self.save()
