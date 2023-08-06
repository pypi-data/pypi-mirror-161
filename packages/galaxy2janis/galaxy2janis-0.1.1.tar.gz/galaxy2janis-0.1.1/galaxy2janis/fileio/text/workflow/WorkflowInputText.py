


from typing import Tuple

from galaxy2janis.entities.workflow import WorkflowInput

from ..TextRender import TextRender
from .. import ordering
from .. import formatting


class WorkflowInputText(TextRender):
    def __init__(self, entity: WorkflowInput):
        super().__init__()
        self.entity = entity

    @property
    def imports(self) -> list[Tuple[str, str]]:
        jtype = self.entity.datatype
        imports: list[Tuple[str, str]] = []
        imports.append((jtype.import_path, jtype.classname))

        # TODO opportunity for decorator
        if self.entity.array:
            imports.append(('janis_core', 'Array'))

        # TODO opportunity for decorator
        imports = list(set(imports))
        return ordering.order_imports(imports)

    def render(self) -> str:
        datatype_str = formatting.format_typestr(self.entity)
        out_str: str = ''
        out_str += f'w.input("{self.entity.tag}", {datatype_str})'
        #out_str += f'\t"{tag}",\n'
        #out_str += f'\t{datatype}'
        #out_str += f',\n\tdefault={default}' if default else ''  # TODO HERE
        #out_str += f',\n\tvalue={value}' if value else ''
        #out_str += f',\n\tdoc="{doc}"' if doc else ''
        #out_str += '\n)\n'
        return out_str