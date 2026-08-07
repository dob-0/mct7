"""Runtime registry surface for the clean ii scaffold."""

from .contracts import RuntimeDefinition


def build_runtime_definition() -> RuntimeDefinition:
    return RuntimeDefinition(
        runtime_id='ii',
        family='ii',
        label='ii Live Runtime',
        version='0.1.0',
        execution_kind='worker',
        runtime_class='project-runtime',
        supported_hosts=['linux'],
        capabilities=[
            'terminal-render',
            'mapping',
            'midi',
            'osc',
            'audio-input',
            'camera-input',
            'web-control',
        ],
        node_types=[
            'ii.output',
            'ii.surface',
            'ii.mapper',
            'ii.controller',
            'ii.mode',
            'ii.clock',
        ],
        surfaces=['controller', 'projector', 'output-zone'],
        transports=['local-socket', 'websocket'],
        asset_kinds=['image', 'video', 'audio', 'mapping', 'preset', 'shader', 'font'],
        entrypoint={'kind': 'local-process', 'command': ['python3', '-m', 'ii_runtime']},
    )


II_RUNTIME_DEFINITION = build_runtime_definition()
