

from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4

from galaxy2janis.datatypes import JanisDatatype
from galaxy2janis import tags


@dataclass
class WorkflowInput:
    _name: str
    array: bool
    optional: bool
    is_runtime: bool
    datatype: JanisDatatype
    value: Any = None

    def __post_init__(self):
        self.uuid: str = str(uuid4())

    @property
    def name(self) -> str:
        if self.is_runtime:
            return self._name
        else:
            return f'in_{self._name}'
    
    @property
    def tag(self) -> str:
        return tags.get(self.uuid)
    
    @property
    def docstring(self) -> Optional[str]:
        return 'None yet!'
        

