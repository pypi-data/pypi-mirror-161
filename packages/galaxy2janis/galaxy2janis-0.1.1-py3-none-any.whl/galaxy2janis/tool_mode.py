
from galaxy2janis.logs import logging

from galaxy2janis.startup import tool_setup
from galaxy2janis.gx.gxtool import load_xmltool

from galaxy2janis.gx.command import gen_command
from galaxy2janis.containers import fetch_container
from galaxy2janis.entities.tool.generate import gen_tool
from galaxy2janis.entities.tool import Tool

# TODO future 
# from galaxy2janis.gx.xmltool.tests import write_tests

"""
this file parses a single tool to janis
the steps involved are laid out in order
each step involves a single module
"""

def tool_mode() -> Tool:
    tool_setup()
    logging.msg_parsing_tool()
    xmltool = load_xmltool()
    command = gen_command(xmltool)
    container = fetch_container(xmltool.metadata.get_main_requirement())
    tool = gen_tool(xmltool, command, container)
    return tool

