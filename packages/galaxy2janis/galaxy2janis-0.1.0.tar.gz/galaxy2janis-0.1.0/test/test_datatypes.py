

import unittest
import datatypes
from datatypes.core import file_t, float_t, bool_t

# mock objects
from mock.mock_components import MOCK_POSIT1
from mock.mock_components import MOCK_FLAG1
from mock.mock_components import MOCK_OPTION1
from mock.mock_components import MOCK_REDIRECT1
from mock.mock_entities import MOCK_WORKFLOW_INPUT1


class TestDatatypeInference(unittest.TestCase):
    """
    tests the datatype which is assigned to an entity
    """

    def test_positional(self) -> None:
        self.assertEquals(datatypes.get(MOCK_POSIT1), file_t)
    
    def test_flag(self) -> None:
        self.assertEquals(datatypes.get(MOCK_FLAG1), bool_t)
    
    def test_option(self) -> None:
        self.assertEquals(datatypes.get(MOCK_OPTION1), float_t)
    
    def test_outputs(self) -> None:
        self.assertEquals(datatypes.get(MOCK_REDIRECT1), file_t)
    
    def test_workflow_input(self) -> None:
        self.assertEquals(datatypes.get(MOCK_WORKFLOW_INPUT1), file_t)
    
    # def test_option_typestring(self) -> None:
    #     raise NotImplementedError()



