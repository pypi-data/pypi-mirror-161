


from typing import Any
import json
import unittest
import xml.etree.ElementTree as et

from gx.gxworkflow.parsing.tool_state import load_tool_state
from gx.gxtool.text.cheetah.evaluation import sectional_evaluate


UNICYCLER_VANILLA_PATH = 'test/data/command/manipulation/template/unicycler/unicycler_command.xml'
UNICYCLER_TEMPLATED_PATH = 'test/data/command/manipulation/template/unicycler/unicycler_command_templated.xml'
UNICYCLER_INPUTS_PATH = 'test/data/command/manipulation/template/unicycler/unicycler_step.json'


def read_cmd(path: str) -> str:
    tree = et.parse(path)
    root = tree.getroot()
    assert(root.text)
    return root.text

def read_step_inputs(path: str) -> dict[str, Any]:
    with open(path, 'r') as fp:
        step = json.load(fp)
    step['tool_state'] = load_tool_state(step)
    return step['tool_state']


class TestSectionalCheetah(unittest.TestCase):

    def test_unicycler(self):
        vanilla = read_cmd(UNICYCLER_VANILLA_PATH)
        reference = read_cmd(UNICYCLER_TEMPLATED_PATH)
        inputs = read_step_inputs(UNICYCLER_INPUTS_PATH)
        templated = sectional_evaluate(vanilla, inputs)
        self.assertEquals(reference, templated)


        