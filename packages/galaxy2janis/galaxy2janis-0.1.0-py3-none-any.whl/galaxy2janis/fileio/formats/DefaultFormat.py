


from galaxy2janis.entities.tool import Tool
from galaxy2janis.entities.workflow import Workflow
from galaxy2janis.entities.workflow import WorkflowStep

from .Format import Format


class DefaultFormat(Format):
    """renders output pages in same manner as appears in original workflow"""

    def workflow(self, workflow: Workflow) -> str:
        raise NotImplementedError()
    
    def subworkflow(self, workflow: Workflow) -> str:
        raise NotImplementedError()
    
    def step(self, step: WorkflowStep) -> str:
        raise NotImplementedError()

    def tool(self, tool: Tool) -> str:
        raise NotImplementedError()

    def script(self) -> str:
        raise NotImplementedError()
    
    def inputs(self, workflow: Workflow) -> str:
        raise NotImplementedError()
    
    def config(self, workflow: Workflow) -> str:
        raise NotImplementedError()


