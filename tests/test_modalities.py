"""Tests classes in modalities module"""

import unittest

from pydantic import BaseModel

from aind_data_schema_models.modalities import Modality


class MockModel(BaseModel):
    mod1: Modality.ONE_OF
    mod2: Modality.ONE_OF
    mod3: Modality.ONE_OF


class TestModality(unittest.TestCase):
    """Tests methods in Modality class"""

    def test_from_abbreviation(self):
        """Tests modality can be constructed from abbreviation"""

        self.assertEqual(Modality.ECEPHYS, Modality.from_abbreviation("ecephys"))

    def test_ophys_to_pophys_coercion(self):
        """Tests that ophys is coerced to pophys"""

        _test_literal = """
        {
        "mod1":{"name":"Extracellular electrophysiology","abbreviation":"ecephys"},
        "mod2":{"name":"Planar optical physiology","abbreviation":"pophys"},
        "mod3":{"name":"foo bar","abbreviation":"ophys"}
        }"""
        t = MockModel(mod1=Modality.ECEPHYS, mod2=Modality.POPHYS, mod3=Modality.POPHYS)

        self.assertEqual(t, MockModel.model_validate_json(_test_literal))

    def test_ophys_to_pophys_from_abbreviation(self):
        """Tests that ophys is coerced to pophys from abbreviation"""

        self.assertEqual(Modality.POPHYS, Modality.from_abbreviation("ophys"))

    def test_ophys_attribute(self):
        """Tests that ophys attribute is available"""

        self.assertEqual(Modality.OPHYS, Modality.POPHYS)


if __name__ == "__main__":
    unittest.main()
