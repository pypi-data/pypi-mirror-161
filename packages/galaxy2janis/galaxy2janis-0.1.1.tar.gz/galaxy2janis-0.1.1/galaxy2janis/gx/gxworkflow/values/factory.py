
from typing import Any, Optional

from galaxy2janis.gx.command.components import InputComponent
from . import utils

from galaxy2janis.entities.workflow import (
    ConnectionInputValue, 
    WorkflowInputInputValue,
    StaticInputValue
)


def static(component: Optional[InputComponent], value: Any, default: bool=False) -> StaticInputValue:
    return StaticInputValue(
        component=component,
        value=value,
        _valtypestr=utils.select_input_value_type(component, value),
        default=default
    )

def connection(component: Optional[InputComponent], step_uuid: str, out_uuid: str) -> ConnectionInputValue:
    return ConnectionInputValue(
        component=component,
        step_uuid=step_uuid,
        out_uuid=out_uuid
    )

def workflow_input(component: Optional[InputComponent], input_uuid: str, is_runtime: bool=False) -> WorkflowInputInputValue:
    return WorkflowInputInputValue(
        component=component,
        input_uuid=input_uuid,
        is_runtime=is_runtime
    )


