"""Tests classes in modalities module"""

import unittest

from aind_data_schema_models.modalities import Modality, ExpectedFiles, FileRequirement


class TestModality(unittest.TestCase):
    """Tests methods in Modality class"""

    def test_from_abbreviation(self):
        """Tests modality can be constructed from abbreviation"""

        self.assertEqual(Modality.ECEPHYS, Modality.from_abbreviation("ecephys"))


class TestExpectedFiles(unittest.TestCase):
    """Test methods in ExpectedFiles class"""

    def test_expected_file_state(self):
        """Test that expected file states were set correctly"""

        self.assertEqual(ExpectedFiles.ECEPHYS.subject, FileRequirement.REQUIRED)
        self.assertEqual(ExpectedFiles.ECEPHYS.data_description, FileRequirement.REQUIRED)
        self.assertEqual(ExpectedFiles.ECEPHYS.procedures, FileRequirement.REQUIRED)
        self.assertEqual(ExpectedFiles.ECEPHYS.session, FileRequirement.REQUIRED)
        self.assertEqual(ExpectedFiles.ECEPHYS.rig, FileRequirement.REQUIRED)
        self.assertEqual(ExpectedFiles.ECEPHYS.processing, FileRequirement.OPTIONAL)
        self.assertEqual(ExpectedFiles.ECEPHYS.acquisition, FileRequirement.EXCLUDED)
        self.assertEqual(ExpectedFiles.ECEPHYS.instrument, FileRequirement.EXCLUDED)
        self.assertEqual(ExpectedFiles.ECEPHYS.quality_control, FileRequirement.OPTIONAL)


if __name__ == "__main__":
    unittest.main()
