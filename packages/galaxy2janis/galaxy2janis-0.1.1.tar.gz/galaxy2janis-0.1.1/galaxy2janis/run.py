

from galaxy2janis import aliases
from galaxy2janis.logs import logging

from galaxy2janis import paths
from galaxy2janis import settings

from galaxy2janis.fileio import write_tool
from galaxy2janis.startup import general_setup
from galaxy2janis.cli import CLIparser
from galaxy2janis.tool_mode import tool_mode
from galaxy2janis.workflow_mode import workflow_mode

import sys
from typing import Optional


"""
gxtool2janis program entry point
parses cli settings then hands execution to other files based on command
"""

def main():
    logging.configure_warnings()
    args = load_args()
    general_setup(args)
    run_sub_program(args)
    

def load_args() -> dict[str, Optional[str]]:
    cli = CLIparser(sys.argv)
    return cli.args

def run_sub_program(args: dict[str, Optional[str]]) -> None:
    match args['command']:
        case 'tool':
            run_tool_mode(args)
            #try_run_tool_mode(args)
        case 'workflow':
            run_workflow_mode(args)
            #try_run_workflow_mode(args)
        case _:
            pass

def run_tool_mode(args: dict[str, Optional[str]]):
    settings.tool.set(args)
    tool = tool_mode()
    path = paths.tool(tool.metadata.id)
    write_tool(tool, path=path)  # I dont like this design, but it may be necessary

def run_workflow_mode(args: dict[str, Optional[str]]):
    workflow_mode(args)


# for bulk parsing stat runs

def try_run_tool_mode(args: dict[str, Optional[str]]):
    try: 
        run_tool_mode(args)
    except Exception as e:
        # print('\n####################')
        # print(settings.tool.tool_id.upper())
        # print('####################\n')
        # print()
        print(e)
        logging.tool_exception()

def try_run_workflow_mode(args: dict[str, Optional[str]]):
    try: 
        run_workflow_mode(args)
    except Exception as e:
        print(e)
        logging.workflow_exception()
    

if __name__ == '__main__':
    main()
