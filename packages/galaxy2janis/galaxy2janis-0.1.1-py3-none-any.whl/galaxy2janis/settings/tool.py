

from typing import Any, Optional

from galaxy2janis.gx.wrappers import Wrapper
from galaxy2janis.gx.wrappers import fetch_wrapper
from galaxy2janis.utils.galaxy import get_xml_id

tool_path: str
tool_id: str
owner: Optional[str] = None
repo: Optional[str] = None
revision: Optional[str] = None


# properties
def xml_basename() -> str:
    return tool_path.rsplit('/', 1)[-1].split('.')[0]

def xml_dir() -> str:
    if '/' not in tool_path:
        return '.'
    return tool_path.rsplit('/', 1)[0]

def logfile_path() -> str:
    return f'{xml_basename()}.log'

def set(args: Optional[dict[str, Any]]=None, wrapper: Optional[Wrapper]=None) -> None:
    if not args and not wrapper:
        raise RuntimeError('supply either args or wrapper to update')
    if args:
        update_args(args)
    elif wrapper:
        update_wrapper(wrapper)

def update_args(args: dict[str, Any]) -> None:
    global tool_path
    global tool_id
    global owner
    global repo
    global revision

    if args['infile']:
        tool_path = args['infile']
        tool_id = get_xml_id(tool_path)
        owner = None
        repo = None
        revision = None
    
    if args['remote']:
        owner, repo, tool_id, revision_raw = args['remote'].split(',')
        revision = revision_raw.rsplit(':', 1)[-1] # incase numeric:revision
        assert(owner)
        assert(repo)
        assert(revision)
        tool_path = fetch_wrapper(owner, repo, revision, tool_id)

def update_wrapper(wrapper: Wrapper) -> None:
    global tool_path
    global tool_id
    global owner
    global repo
    global revision

    tool_id = wrapper.tool_id
    owner = wrapper.owner
    repo = wrapper.repo
    revision = wrapper.revision
    tool_path = fetch_wrapper(wrapper.owner, wrapper.repo, wrapper.revision, wrapper.tool_id)

