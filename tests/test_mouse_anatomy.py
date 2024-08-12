"""Tests classes in organizations module"""

import unittest

from aind_data_schema_models.mouse_anatomy import MouseAnatomicalStructure


class TestMouseAnatomy(unittest.TestCase):
    """Tests methods in MouseAnatomicalStructure class"""

    def test_subset(self):
        """Test that the subset groups are generated correctly
        """
        self.assertIn("EMG_MUSCLES", MouseAnatomicalStructure)


if __name__ == "__main__":
    unittest.main()
