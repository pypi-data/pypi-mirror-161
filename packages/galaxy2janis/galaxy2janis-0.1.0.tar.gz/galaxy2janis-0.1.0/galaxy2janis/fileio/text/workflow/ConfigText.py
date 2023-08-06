
from typing import Tuple

from galaxy2janis.entities.workflow import Workflow
from ..TextRender import TextRender


class ConfigText(TextRender):
    def __init__(self, entity: Workflow):
        super().__init__()
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        raise NotImplementedError()

    def render(self) -> str:
        raise NotImplementedError()
    
