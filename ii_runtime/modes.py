"""Built-in modes for the clean ii runtime."""

from dataclasses import dataclass
from math import sin

from .contracts import ControlState, ModeDefinition


@dataclass(frozen=True)
class ModeFrame:
    lines: list[str]


class BaseMode:
    name = 'base'
    definition = ModeDefinition(name='base', label='Base', description='Abstract base mode.')

    def render(self, state: ControlState, width: int, height: int, tick: int) -> ModeFrame:
        raise NotImplementedError


class TextMode(BaseMode):
    name = 'text'
    definition = ModeDefinition(
        name='text',
        label='Text',
        description='Centered signal text for cues, labels, and flash overlays.',
        controls=['flash_text', 'master_dim', 'palette'],
    )

    def render(self, state: ControlState, width: int, height: int, tick: int) -> ModeFrame:
        label = state.flash_text[: max(1, width)].center(width)
        lines = [' ' * width for _ in range(max(1, height))]
        center = min(len(lines) - 1, height // 2)
        lines[center] = label
        return ModeFrame(lines)


class PulseMode(BaseMode):
    name = 'pulse'
    definition = ModeDefinition(
        name='pulse',
        label='Pulse',
        description='Beat-reactive band that expands and contracts with tempo.',
        controls=['bpm', 'master_dim', 'palette'],
    )

    def render(self, state: ControlState, width: int, height: int, tick: int) -> ModeFrame:
        lines = []
        speed = max(0.5, state.bpm / 90.0)
        strength = (sin((tick / 3.0) * speed) + 1.0) / 2.0
        fill = max(1, int(strength * max(1, width - 2)))
        for row in range(max(1, height)):
            if row == height // 2:
                body = ('#' * fill).center(width)
            else:
                body = ('-' * max(1, fill // 3)).center(width)
            lines.append(body[:width].ljust(width))
        return ModeFrame(lines)


class RainMode(BaseMode):
    name = 'rain'
    definition = ModeDefinition(
        name='rain',
        label='Rain',
        description='Terminal rain columns derived from beat speed.',
        controls=['bpm', 'master_dim', 'palette'],
    )

    def render(self, state: ControlState, width: int, height: int, tick: int) -> ModeFrame:
        width = max(1, width)
        height = max(1, height)
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        speed = max(1, state.bpm // 30)
        for col in range(0, width, 3):
            head = (tick * speed + col * 2) % height
            grid[head][col] = '|'
            if head - 1 >= 0:
                grid[head - 1][col] = ':'
            elif height > 1:
                grid[-1][col] = ':'
        return ModeFrame([''.join(row) for row in grid])


BUILTIN_MODES = {
    TextMode.name: TextMode(),
    PulseMode.name: PulseMode(),
    RainMode.name: RainMode(),
}


def list_mode_definitions() -> list[ModeDefinition]:
    return [mode.definition for mode in BUILTIN_MODES.values()]
