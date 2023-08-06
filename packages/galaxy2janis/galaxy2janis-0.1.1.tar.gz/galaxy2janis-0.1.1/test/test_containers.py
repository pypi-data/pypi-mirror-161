


import os
import unittest

import containers
from gx.gxtool.requirements import CondaRequirement

QUERY1 = CondaRequirement(_name='abricate', _version='1.0.1')
QUERY1_EXPECTED_RESULT = 'quay.io/biocontainers/abricate:1.0.1--ha8f3691_1'

QUERY2 = CondaRequirement(_name='samtools', _version='1.15')
QUERY2_EXPECTED_RESULT = 'quay.io/biocontainers/samtools:1.15--h1170115_1'

QUERY3 = CondaRequirement(_name='cutadapt', _version='3.5')
QUERY3_EXPECTED_RESULT = 'quay.io/biocontainers/cutadapt:3.5--py36h91eb985_1'


class TestContainerFetching(unittest.TestCase):
    """
    tests biocontainer fetching given a tool id, tool version, and a Requirement()
    """

    def setUp(self) -> None:
        """
        creates a temp container cache for use. the tearDown() method will remove this after tests have run. 
        """
        self.temp_cache_dir = 'test/temp/container_cache.json'
        with open(self.temp_cache_dir, 'w') as fp:
            fp.write('{}')
    
    def test_1(self) -> None:
        result = containers.fetch_container(QUERY1)
        self.assertEquals(result, QUERY1_EXPECTED_RESULT)
    
    def test_2(self) -> None:
        result = containers.fetch_container(QUERY2)
        self.assertEquals(result, QUERY2_EXPECTED_RESULT)
    
    def test_3(self) -> None:
        result = containers.fetch_container(QUERY3)
        self.assertEquals(result, QUERY3_EXPECTED_RESULT)
    
    def tearDown(self) -> None:
        if os.path.exists(self.temp_cache_dir):
            os.remove(self.temp_cache_dir)
        

