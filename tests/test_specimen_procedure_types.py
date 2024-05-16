"""Testing script for the SpecimenProcedureTypes enum"""

from aind_data_schema_models.specimen_procedure_types import SpecimenProcedureType
import unittest


class TestSpecimenProcedureTypes(unittest.TestCase):
    """Tests methods in SpecimenProcedureType class"""

    def test_class_construction(self):
        """Tests enum can be instantiated via string"""

        self.assertEqual(SpecimenProcedureType.DELIPIDATION, SpecimenProcedureType("Delipidation"))
