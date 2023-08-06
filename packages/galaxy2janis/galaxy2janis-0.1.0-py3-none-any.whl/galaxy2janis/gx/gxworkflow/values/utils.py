

from typing import Any, Optional
from galaxy2janis import expressions

from ...command.components.outputs.OutputComponent import OutputComponent
from ...command.components import InputComponent


def get_comptype(component: InputComponent | OutputComponent) -> str:
    return type(component).__name__.lower() 

def select_input_value_type(component: Optional[InputComponent], value: Any) -> str:
    """
    only StaticValueLinkingStrategy and DefaultValueLinkingStrategy 
    call select_input_value_type(). don't need to worry about CONNECTION and RUNTIME_VALUE
    """
    if is_bool(value):
        return 'boolean'
    elif component and is_numeric(component, value):
        return 'numeric'
    elif is_none(value):
        return 'none'
    elif expressions.is_var(value) or expressions.has_var(value):
        return 'env_var'
    else:
        return 'string'

def is_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    return False

def is_none(value: Any) -> bool:
    if value is None:
        return True
    return False

def is_numeric(component: InputComponent | OutputComponent, value: Any) -> bool:
    if _has_numeric_datatype(component):
        if expressions.is_int(str(value)) or expressions.is_float(str(value)):
            return True
    return False

def _has_numeric_datatype(component: InputComponent | OutputComponent) -> bool:
    jtype = component.datatype
    numeric_classes = ['Int', 'Float']
    if jtype.classname in numeric_classes:
        return True
    return False
    


