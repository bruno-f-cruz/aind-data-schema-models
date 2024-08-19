"""Tests classes in organizations module"""

import unittest

from aind_data_schema_models.mouse_anatomy import MouseAnatomicalStructure
from aind_data_schema_models.utils import one_of_instance


class TestMouseAnatomy(unittest.TestCase):
    """Tests methods in MouseAnatomicalStructure class"""

    def test_subset(self):
        """Test that the subset groups are generated correctly
        """
        emg_muscles = one_of_instance([
            MouseAnatomicalStructure.DELTOID,
            MouseAnatomicalStructure.PECTORALIS_MAJOR,
            MouseAnatomicalStructure.TRICEPS_BRACHII,
            MouseAnatomicalStructure.BICEPS_BRACHII,
            MouseAnatomicalStructure.PARS_SCAPULARIS_OF_DELTOID,
            MouseAnatomicalStructure.EXTENSOR_CARPI_RADIALIS_LONGUS,
            MouseAnatomicalStructure.EXTENSOR_DIGITORUM_COMMUNIS,
            MouseAnatomicalStructure.EXTENSOR_DIGITORUM_LATERALIS,
            MouseAnatomicalStructure.EXTENSOR_CARPI_ULNARIS,
            MouseAnatomicalStructure.FLEXOR_CARPI_RADIALIS,
            MouseAnatomicalStructure.FLEXOR_CARPI_ULNARIS,
            MouseAnatomicalStructure.FLEXOR_DIGITORUM_PROFUNDUS,
            ])

        self.assertTrue(hasattr(MouseAnatomicalStructure, "EMG_MUSCLES"))
        self.assertEqual(dir(MouseAnatomicalStructure.EMG_MUSCLES), dir(emg_muscles))


if __name__ == "__main__":
    unittest.main()
