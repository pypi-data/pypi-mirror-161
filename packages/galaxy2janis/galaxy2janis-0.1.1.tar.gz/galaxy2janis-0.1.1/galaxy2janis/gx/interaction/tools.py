

import os
import tempfile
from typing import Optional

from galaxy.tools import Tool as GxTool
from galaxy.tool_util.parser import get_tool_source
from galaxy.tools import create_tool_from_source
from galaxy.model import History

from galaxy2janis.gx.interaction.mock import MockApp, MockObjectStore
from galaxy2janis.utils import galaxy as utils


def get_tool(xml_path: str) -> GxTool:
    app = _get_app()
    tool_source = get_tool_source(xml_path)
    tool = create_tool_from_source(app, tool_source)
    tool.assert_finalized()
    return tool

def get_builtin_tool_path(tool_id: str) -> Optional[str]:
    """returns path to xml file with id='tool_id'"""
    tool_directories = _get_builtin_tool_directories()
    for directory in tool_directories:
        xmlfile = utils.get_xml_by_id(directory, tool_id)
        if xmlfile:
            return f'{directory}/{xmlfile}'
    return None

def _get_builtin_tool_directories() -> list[str]:
    out: list[str] = []
    out += _get_builtin_tools_directories()
    out += _get_datatype_converter_directories()
    return out

def _get_builtin_tools_directories() -> list[str]:
    import galaxy.tools
    tools_folder = str(galaxy.tools.__file__).rsplit('/', 1)[0]
    bundled_folders = os.listdir(f'{tools_folder}/bundled')
    bundled_folders = [f for f in bundled_folders if not f.startswith('__')]
    bundled_folders = [f'{tools_folder}/bundled/{f}' for f in bundled_folders]
    bundled_folders = [f for f in bundled_folders if os.path.isdir(f)]
    return [tools_folder] + bundled_folders

def _get_datatype_converter_directories() -> list[str]:
    import galaxy.datatypes
    datatypes_folder = str(galaxy.datatypes.__file__).rsplit('/', 1)[0]
    converters_folder = f'{datatypes_folder}/converters'
    return [converters_folder]

def _get_app() -> MockApp:
    # basic details
    app = MockApp()
    app.job_search = None
    app.object_store = MockObjectStore()
    # config
    app.config.new_file_path = os.path.join(tempfile.mkdtemp(), "new_files")
    app.config.admin_users = "grace@thebest.com"
    app.config.len_file_path = "moocow"
    # database
    
    app.model.context.add(History())
    app.model.context.flush()
    return app
