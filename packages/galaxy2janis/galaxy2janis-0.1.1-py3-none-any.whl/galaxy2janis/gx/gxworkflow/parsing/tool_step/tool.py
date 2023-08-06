

from typing import Any

from galaxy2janis.entities.tool import Tool
from galaxy2janis.entities.workflow import StepMetadata
from galaxy2janis.entities.workflow import Workflow

from galaxy2janis.tool_mode import tool_mode
from galaxy2janis.gx.gxworkflow.parsing.tool_state import load_tool_state
from galaxy2janis.gx.interaction import get_builtin_tool_path

from galaxy2janis import mapping
from galaxy2janis import settings

def ingest_workflow_tools(janis: Workflow, galaxy: dict[str, Any]) -> None:
    for g_step in galaxy['steps'].values():
        if g_step['type'] == 'tool':
            j_step = mapping.step(g_step['id'], janis, galaxy)
            tool = parse_step_tool(j_step.metadata)
            j_step.set_tool(tool)
            g_step['tool_state'] = load_tool_state(g_step)

def parse_step_tool(metadata: StepMetadata) -> Tool:
    args = create_tool_settings_for_step(metadata)
    settings.tool.set(args)
    return tool_mode()

def create_tool_settings_for_step(metadata: StepMetadata) -> dict[str, Any]:
    tool_id = metadata.wrapper.tool_id
    if metadata.wrapper.inbuilt:
        xml_path = get_builtin_tool_path(tool_id)
        assert(xml_path)
        return {
            'infile': xml_path,
            'remote': None,
            'outdir': None
            #'outdir': f'{paths.wrapper(tool_id, tool_id)}'
        }
    else:
        revision = metadata.wrapper.revision
        owner = metadata.wrapper.owner
        repo = metadata.wrapper.repo
        return {
            'infile': None,
            'remote': f'{owner},{repo},{tool_id},{revision}',
            'outdir': None
            #'outdir': f'{paths.wrapper(tool_id, revision)}'
        }
