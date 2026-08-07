"""Cue and parameter-group definitions for the clean ii runtime."""

from .contracts import ControlGroup, CueDefinition

CONTROL_GROUPS = [
    ControlGroup(key='transport', label='Transport', controls=['mode', 'mode_b', 'blackout', 'flash_active']),
    ControlGroup(key='tempo', label='Tempo', controls=['bpm', 'bpm_sync']),
    ControlGroup(key='layering', label='Layering', controls=['layer_b_enabled', 'layer_b_alpha', 'master_dim']),
    ControlGroup(key='look', label='Look', controls=['palette', 'flash_text']),
]

BUILTIN_CUES = [
    CueDefinition(
        name='signal',
        label='SIGNAL',
        description='Centered identity frame for intros, labels, and quiet moments.',
        patch={'mode': 'text', 'palette': 'steel', 'flash_text': 'ii', 'flash_active': False, 'blackout': False},
    ),
    CueDefinition(
        name='drive',
        label='DRIVE',
        description='Main pulse state for forward motion and tempo-led sections.',
        patch={'mode': 'pulse', 'palette': 'blood', 'bpm': 132, 'blackout': False},
    ),
    CueDefinition(
        name='storm',
        label='STORM',
        description='Layered pulse-plus-rain state for denser energy.',
        patch={
            'mode': 'pulse',
            'mode_b': 'rain',
            'layer_b_enabled': True,
            'layer_b_alpha': 0.55,
            'palette': 'ember',
            'bpm': 140,
            'blackout': False,
        },
    ),
    CueDefinition(
        name='alert',
        label='ALERT',
        description='Flash overlay state for hard accents and callouts.',
        patch={'mode': 'rain', 'palette': 'acid', 'flash_active': True, 'flash_text': 'ALERT', 'bpm': 150},
    ),
    CueDefinition(
        name='blackout',
        label='BLACKOUT',
        description='Immediate blackout safety state.',
        patch={'blackout': True, 'flash_active': False},
    ),
]
