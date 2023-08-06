


from galaxy2janis.entities.workflow import Workflow
from galaxy2janis.entities.workflow.step.inputs import (
    ConnectionInputValue, 
    InputValue, 
    StaticInputValue, 
    WorkflowInputInputValue
)


def update_components_optionality(value: InputValue, janis: Workflow) -> None:
    if value.component:  # if linked to tool component
        if isinstance(value, WorkflowInputInputValue):
            if not value.is_runtime:
                w_inp = janis.get_input(query_uuid=value.input_uuid)
                if w_inp.optional and not value.component.optional:
                    value.component.forced_optionality = True
        elif isinstance(value, ConnectionInputValue):
            s_out = janis.get_step_output(query_uuid=value.out_uuid) 
            if s_out.tool_output.optional and not value.component.optional:
                value.component.forced_optionality = True
        elif isinstance(value, StaticInputValue):
            if value.is_none:
                value.component.forced_optionality = True

