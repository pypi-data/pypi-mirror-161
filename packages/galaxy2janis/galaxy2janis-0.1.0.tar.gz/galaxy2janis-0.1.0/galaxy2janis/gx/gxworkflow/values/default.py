


from __future__ import annotations
from typing import TYPE_CHECKING

from galaxy2janis.gx.command.components.inputs.InputComponent import InputComponent

if TYPE_CHECKING:
    from galaxy2janis.entities.workflow import WorkflowStep
    from galaxy2janis.entities.workflow import Workflow

from . import factory
from galaxy2janis import settings


def handle_tool_default_inputs(janis: Workflow) -> None:
    # sets tool input values as default
    for j_step in janis.steps:
        settings.tool.set(wrapper=j_step.metadata.wrapper)
        ingest_values_defaults(j_step)

def ingest_values_defaults(j_step: WorkflowStep) -> None:
    # tool components which don't yet appear in register
    for component in get_linkable_components(j_step):
        input_value = factory.static(component, component.default_value, default=True)
        j_step.inputs.add(input_value)

def get_linkable_components(j_step: WorkflowStep) -> list[InputComponent]:
    out: list[InputComponent] = []
    for component in j_step.tool.inputs:
        if not j_step.inputs.get(component.uuid):
            out.append(component)
    return out

        