"""Core runtime contracts for the clean ii scaffold."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeDefinition:
    runtime_id: str
    family: str
    label: str
    version: str
    execution_kind: str
    runtime_class: str
    supported_hosts: list[str]
    capabilities: list[str]
    node_types: list[str]
    surfaces: list[str]
    transports: list[str]
    asset_kinds: list[str]
    entrypoint: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ControlField:
    key: str
    label: str
    value_type: str
    default: Any
    minimum: float | int | None = None
    maximum: float | int | None = None
    options: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ControlGroup:
    key: str
    label: str
    controls: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ModeDefinition:
    name: str
    label: str
    description: str
    controls: list[str] = field(default_factory=list)
    layerable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CueDefinition:
    name: str
    label: str
    description: str
    patch: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeCommand:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ControlState:
    mode: str = 'text'
    mode_b: str = 'rain'
    layer_b_enabled: bool = False
    layer_b_alpha: float = 0.35
    palette: str = 'steel'
    bpm: int = 140
    bpm_sync: bool = True
    blackout: bool = False
    flash_active: bool = False
    flash_text: str = 'ii'
    master_dim: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeSnapshot:
    runtime_id: str
    session_id: str
    transport_state: str
    active_mode: str
    palette: str
    bpm: int
    blackout: bool
    metrics: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    controls: dict[str, Any] = field(default_factory=dict)
    control_schema: list[dict[str, Any]] = field(default_factory=list)
    control_groups: list[dict[str, Any]] = field(default_factory=list)
    mode_catalog: list[dict[str, Any]] = field(default_factory=list)
    cue_catalog: list[dict[str, Any]] = field(default_factory=list)
    active_cue: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
