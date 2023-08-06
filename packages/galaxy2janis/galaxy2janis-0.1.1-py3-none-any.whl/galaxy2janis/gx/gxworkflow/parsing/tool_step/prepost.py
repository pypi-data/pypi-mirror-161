


from typing import Any, Optional
from galaxy2janis.gx.command.cmdstr.DynamicCommandStatement import DynamicCommandStatement
from galaxy2janis.gx.command.cmdstr.generate import gen_command_string
from galaxy2janis.entities.workflow.workflow import Workflow
from galaxy2janis.gx.gxtool import load_xmltool
from galaxy2janis.gx.gxtool.text import load_partial_cheetah_command

from galaxy2janis import mapping
from galaxy2janis import settings


def ingest_workflow_steps_prepost(janis: Workflow, galaxy: dict[str, Any]) -> None:
    for g_step in galaxy['steps'].values():
        if g_step['type'] == 'tool':
            ingest_prepost(g_step, janis, galaxy)

def ingest_prepost(g_step: dict[str, Any], janis: Workflow, galaxy: dict[str, Any]):
    # get janis step & update settings
    j_step = mapping.step(g_step['id'], janis, galaxy)
    settings.tool.set(wrapper=j_step.metadata.wrapper)

    xmltool = load_xmltool()
    command = load_partial_cheetah_command(inputs_dict=g_step['tool_state'])
    cmdstr = gen_command_string(source='xml', the_string=command, xmltool=xmltool)
    j_step.preprocessing = extract_cmdline(cmdstr.preprocessing)
    j_step.postprocessing = extract_cmdline(cmdstr.postprocessing)

def extract_cmdline(statements: list[DynamicCommandStatement]) -> Optional[str]:
    if not statements:
        return None
    cmdlines = [x.cmdline for x in statements]
    return ' &&'.join(cmdlines)

