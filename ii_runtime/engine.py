"""Clean ii runtime engine with self-describing controls."""

from dataclasses import replace
from time import monotonic
from uuid import uuid4

from .contracts import ControlField, ControlState, CueDefinition, RuntimeCommand, RuntimeSnapshot
from .modes import BUILTIN_MODES, list_mode_definitions
from .presets import BUILTIN_CUES, CONTROL_GROUPS
from .registry import II_RUNTIME_DEFINITION

PALETTE_OPTIONS = ['steel', 'acid', 'void', 'neon', 'ultra', 'deep', 'blood', 'ember']
CONTROL_FIELDS = [
    ControlField(key='mode', label='MODE', value_type='mode', default='text', options=sorted(BUILTIN_MODES)),
    ControlField(key='mode_b', label='MODE B', value_type='mode', default='rain', options=sorted(BUILTIN_MODES)),
    ControlField(key='layer_b_enabled', label='LAYER B', value_type='bool', default=False),
    ControlField(key='layer_b_alpha', label='LAYER MIX', value_type='float', default=0.35, minimum=0.0, maximum=1.0),
    ControlField(key='palette', label='PALETTE', value_type='palette', default='steel', options=PALETTE_OPTIONS),
    ControlField(key='bpm', label='BPM', value_type='int', default=140, minimum=40, maximum=240),
    ControlField(key='bpm_sync', label='BPM SYNC', value_type='bool', default=True),
    ControlField(key='blackout', label='BLACKOUT', value_type='bool', default=False),
    ControlField(key='flash_active', label='FLASH', value_type='bool', default=False),
    ControlField(key='flash_text', label='FLASH TEXT', value_type='text', default='ii'),
    ControlField(key='master_dim', label='MASTER DIM', value_type='float', default=1.0, minimum=0.0, maximum=1.0),
]
CONTROL_FIELD_MAP = {field.key: field for field in CONTROL_FIELDS}


class IiRuntime:
    def __init__(self, control: ControlState | None = None):
        self.definition = II_RUNTIME_DEFINITION
        self.control = control or ControlState()
        self.session_id = f'ii-session-{uuid4()}'
        self.started_at = monotonic()
        self._frame_count = 0
        self._cue_index: int | None = None

    def set_mode(self, mode: str) -> None:
        self.apply_patch({'mode': mode})

    def available_modes(self) -> list[dict[str, object]]:
        return [definition.to_dict() for definition in list_mode_definitions()]

    def control_schema(self) -> list[dict[str, object]]:
        return [field.to_dict() for field in CONTROL_FIELDS]

    def control_groups(self) -> list[dict[str, object]]:
        return [group.to_dict() for group in CONTROL_GROUPS]

    def available_cues(self) -> list[dict[str, object]]:
        return [cue.to_dict() for cue in BUILTIN_CUES]

    def active_cue_name(self) -> str | None:
        if self._cue_index is None:
            return None
        return BUILTIN_CUES[self._cue_index].name

    def apply_command(self, command: RuntimeCommand) -> None:
        if command.kind == 'control.patch':
            self.apply_patch(command.payload)
            return
        if command.kind == 'mode.set':
            self.apply_patch({'mode': command.payload.get('mode', self.control.mode)})
            return
        if command.kind == 'cue.select':
            self.select_cue(name=command.payload.get('name'), index=command.payload.get('index'))
            return
        if command.kind == 'cue.advance':
            self.advance_cue()
            return
        if command.kind == 'cue.previous':
            self.previous_cue()
            return
        raise ValueError(f'unsupported command kind: {command.kind}')

    def apply_patch(self, patch: dict[str, object]) -> None:
        updates: dict[str, object] = {}
        for key, value in patch.items():
            field = CONTROL_FIELD_MAP.get(key)
            if field is None:
                raise ValueError(f'unsupported control key: {key}')
            updates[key] = self._coerce_value(field, value)
        self.control = replace(self.control, **updates)

    def select_cue(self, name: object | None = None, index: object | None = None) -> str:
        cue_index = self._resolve_cue_index(name=name, index=index)
        cue = BUILTIN_CUES[cue_index]
        self.apply_patch(cue.patch)
        self._cue_index = cue_index
        return cue.name

    def advance_cue(self) -> str:
        next_index = 0 if self._cue_index is None else (self._cue_index + 1) % len(BUILTIN_CUES)
        return self.select_cue(index=next_index)

    def previous_cue(self) -> str:
        next_index = len(BUILTIN_CUES) - 1 if self._cue_index is None else (self._cue_index - 1) % len(BUILTIN_CUES)
        return self.select_cue(index=next_index)

    def snapshot(self) -> RuntimeSnapshot:
        elapsed = max(0.001, monotonic() - self.started_at)
        fps = round(self._frame_count / elapsed, 2)
        return RuntimeSnapshot(
            runtime_id=self.definition.runtime_id,
            session_id=self.session_id,
            transport_state='ready',
            active_mode=self.control.mode,
            palette=self.control.palette,
            bpm=self.control.bpm,
            blackout=self.control.blackout,
            metrics={'frames': self._frame_count, 'fps': fps, 'uptime_s': round(elapsed, 3)},
            inputs={},
            outputs={'surfaces': ['controller', 'projector']},
            controls=self.control.to_dict(),
            control_schema=self.control_schema(),
            control_groups=self.control_groups(),
            mode_catalog=self.available_modes(),
            cue_catalog=self.available_cues(),
            active_cue=self.active_cue_name(),
        )

    def render_frame(self, width: int = 40, height: int = 10) -> str:
        width = max(1, width)
        height = max(1, height)
        self._frame_count += 1
        if self.control.blackout:
            return '\n'.join([' ' * width for _ in range(max(1, height))])
        frame = self._render_mode(self.control.mode, width, height)
        if self.control.layer_b_enabled:
            layer_b = self._render_mode(self.control.mode_b, width, height)
            frame = self._composite_layers(frame, layer_b, self.control.layer_b_alpha)
        if self.control.flash_active:
            frame = self._overlay_text(frame, self.control.flash_text, width, height)
        frame = self._apply_master_dim(frame, self.control.master_dim)
        return '\n'.join(frame)

    def _render_mode(self, mode_name: str, width: int, height: int) -> list[str]:
        mode = BUILTIN_MODES.get(mode_name, BUILTIN_MODES['text'])
        frame = mode.render(self.control, width, height, self._frame_count)
        return [line[:width].ljust(width) for line in frame.lines[:height]]

    def _composite_layers(self, primary: list[str], secondary: list[str], alpha: float) -> list[str]:
        if alpha <= 0:
            return primary
        density = int(max(0.0, min(1.0, alpha)) * 100)
        blended: list[str] = []
        for y, (base_line, layer_line) in enumerate(zip(primary, secondary)):
            chars = list(base_line)
            for x, secondary_char in enumerate(layer_line):
                if secondary_char == ' ':
                    continue
                if density >= 100 or ((x * 17 + y * 31) % 100) < density:
                    chars[x] = secondary_char
            blended.append(''.join(chars))
        return blended

    def _overlay_text(self, frame: list[str], text: str, width: int, height: int) -> list[str]:
        lines = list(frame)
        row = min(len(lines) - 1, height // 2)
        label = str(text or 'ii')[:width].center(width)
        lines[row] = label
        return lines

    @staticmethod
    def _resolve_cue_index(name: object | None = None, index: object | None = None) -> int:
        if index is not None:
            return int(index) % len(BUILTIN_CUES)
        if name is not None:
            cue_name = str(name).strip().lower()
            for cue_index, cue in enumerate(BUILTIN_CUES):
                if cue.name == cue_name:
                    return cue_index
            raise ValueError(f'unknown cue: {name}')
        raise ValueError('cue selection requires name or index')

    def _apply_master_dim(self, frame: list[str], master_dim: float) -> list[str]:
        if master_dim <= 0:
            return [' ' * len(line) for line in frame]
        if master_dim >= 0.999:
            return frame
        return [''.join(self._dim_char(char, master_dim) for char in line) for line in frame]

    @staticmethod
    def _dim_char(char: str, master_dim: float) -> str:
        if char == ' ':
            return char
        if master_dim >= 0.75:
            return char
        if master_dim >= 0.45:
            return '+' if char in '#|' else ':'
        if master_dim >= 0.2:
            return '.'
        return ' '

    @staticmethod
    def _coerce_value(field: ControlField, value: object) -> object:
        if field.value_type == 'mode':
            mode_name = str(value).strip().lower()
            if mode_name not in BUILTIN_MODES:
                raise ValueError(f'unsupported mode: {value}')
            return mode_name
        if field.value_type == 'palette':
            palette_name = str(value).strip().lower()
            if palette_name not in field.options:
                raise ValueError(f'unsupported palette: {value}')
            return palette_name
        if field.value_type == 'bool':
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            text = str(value).strip().lower()
            if text in {'1', 'true', 'on', 'yes'}:
                return True
            if text in {'0', 'false', 'off', 'no'}:
                return False
            raise ValueError(f'invalid boolean for {field.key}: {value}')
        if field.value_type == 'int':
            number = int(value)
            if field.minimum is not None:
                number = max(int(field.minimum), number)
            if field.maximum is not None:
                number = min(int(field.maximum), number)
            return number
        if field.value_type == 'float':
            number = float(value)
            if field.minimum is not None:
                number = max(float(field.minimum), number)
            if field.maximum is not None:
                number = min(float(field.maximum), number)
            return number
        if field.value_type == 'text':
            return str(value)
        raise ValueError(f'unsupported field type: {field.value_type}')
