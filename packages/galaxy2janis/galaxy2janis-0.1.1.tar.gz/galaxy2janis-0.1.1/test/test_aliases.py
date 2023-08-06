

import unittest
import xml.etree.ElementTree as et

from gx.gxtool.text.simplification.aliases import resolve_aliases



def get_cmd(path: str) -> str:
    tree = et.parse(path)
    root = tree.getroot()
    assert(root.text)
    return root.text


class TestAliases(unittest.TestCase):

    def test_resolve_fastqc(self):
        raw_path = 'test/data/command/manipulation/aliases/fastqc/fastqc_command.xml'
        ref_path = 'test/data/command/manipulation/aliases/fastqc/fastqc_command_resolved.xml'
        raw_cmd = get_cmd(raw_path)
        ref_cmd = get_cmd(ref_path)
        res_cmd = resolve_aliases(raw_cmd)
        self.assertEquals(ref_cmd, res_cmd)
    
    def test_resolve_unicycler(self):
        raw_path = 'test/data/command/manipulation/aliases/unicycler/unicycler_command.xml'
        ref_path = 'test/data/command/manipulation/aliases/unicycler/unicycler_command_resolved.xml'
        raw_cmd = get_cmd(raw_path)
        ref_cmd = get_cmd(ref_path)
        res_cmd = resolve_aliases(raw_cmd)
        self.assertEquals(ref_cmd, res_cmd)
        
