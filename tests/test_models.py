"""Tests classes with fixed Literal values match defaults"""

import unittest

from aind_data_schema_models.harp_types import HarpDeviceType
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.platforms import Platform
from aind_data_schema_models.registries import Registry
from aind_data_schema_models.species import Species
from aind_data_schema_models.mouse_anatomy import MouseAnatomicalStructure
from aind_data_schema_models.brain_atlas import CCFStructure


class LiteralAndDefaultTests(unittest.TestCase):
    """Tests Literals match defaults in several classes"""

    def test_organizations(self):
        """Test Literals match defaults"""

        for organization in Organization.ALL:
            model = organization()
            round_trip = model.model_validate_json(model.model_dump_json())
            self.assertIsNotNone(round_trip)

    def test_harp(self):
        """Test Literals match defaults"""

        for harp in HarpDeviceType.ALL:
            model = harp()
            round_trip = model.model_validate_json(model.model_dump_json())
            self.assertIsNotNone(round_trip)

    def test_registry(self):
        """Test Literals match defaults"""

        for registry in Registry.ALL:
            model = registry()
            round_trip = model.model_validate_json(model.model_dump_json())
            self.assertIsNotNone(round_trip)

    def test_platforms(self):
        """Test Literals match defaults"""

        for platform in Platform.ALL:
            model = platform()
            round_trip = model.model_validate_json(model.model_dump_json())
            self.assertIsNotNone(round_trip)

    def test_species(self):
        """Test Literals match defaults"""

        for species in Species.ALL:
            model = species()
            round_trip = model.model_validate_json(model.model_dump_json())
            self.assertIsNotNone(round_trip)

    def test_ccf(self):
        """Test Literals match defaults"""
        for structure in CCFStructure.ALL:
            model = structure()
            round_trip = model.model_validate_json(model.model_dump_json())
            self.assertIsNotNone(round_trip)

    def test_mouse_anatomy(self):
        """Test Literals match defaults"""

        for structure in MouseAnatomicalStructure.ALL:
            model = structure()
            round_trip = model.model_validate_json(model.model_dump_json())
            self.assertIsNotNone(round_trip)


if __name__ == "__main__":
    unittest.main()
