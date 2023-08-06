

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from galaxy2janis import tags
from galaxy2janis.gx.command.components import InputComponent


class InputValueType(Enum):
    RUNTIME         = auto()
    ENV_VAR         = auto()
    STRING          = auto()
    NUMERIC         = auto()
    BOOLEAN         = auto()
    NONE            = auto()

enum_map = {
    #'runtime': InputValueType.RUNTIME,
    'env_var': InputValueType.ENV_VAR,
    'string': InputValueType.STRING,
    'numeric': InputValueType.NUMERIC,
    'boolean': InputValueType.BOOLEAN,
    'none': InputValueType.NONE
}

@dataclass
class InputValue(ABC):
    component: Optional[InputComponent]

    def __post_init__(self):
        self.scatter: bool = False

    @property
    def comptype(self) -> Optional[str]:
        return type(self.component).__name__.lower() 

    @property
    def input_tag(self) -> str:
        """get the str tag for this tool input"""
        if self.component:
            return self.component.tag
        else:
            return 'UNKNOWN'
    
    @property
    @abstractmethod
    def input_value(self) -> str:
        """get the str value for this tool input"""
        ...


@dataclass
class StaticInputValue(InputValue):
    value: str
    _valtypestr: str
    default: bool

    def __post_init__(self):
        self.scatter: bool = False
        self.valtype = enum_map[self._valtypestr]
    
    @property
    def is_none(self) -> bool:
        if self.valtype == InputValueType.NONE:
            return True
        return False
    
    @property
    def input_value(self) -> str:
        if self._should_wrap_value():
            return f'"{self.value}"'
        else:
            return f'{self.value}'

    def _should_wrap_value(self) -> bool:
        if self.valtype == InputValueType.STRING:
            return True
        if self.valtype == InputValueType.ENV_VAR:
            return True
        return False


@dataclass
class ConnectionInputValue(InputValue):
    step_uuid: str
    out_uuid: str
    
    @property
    def input_value(self) -> str:
        step_tag = tags.get(self.step_uuid)
        out_tag = tags.get(self.out_uuid)
        return f'w.{step_tag}.{out_tag}'
    

@dataclass
class WorkflowInputInputValue(InputValue):
    input_uuid: str
    is_runtime: bool

    @property
    def input_value(self) -> str:
        wflow_inp_tag = tags.get(self.input_uuid)
        return f'w.{wflow_inp_tag}'

