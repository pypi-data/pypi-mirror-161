import unittest
import numpy as np
import pandas as pd

from naclo import UnitConverter


class TestUnitConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_values = [
            55,
            4,
            7,
            100,
            2000
        ]
        cls.test_units = [
            'ug•ml-1',
            'mg/l',
            'unrecognized',
            np.nan,
            'pm'
        ]
        cls.test_mws = [
            220,
            400,
            300,
            110,
            150
        ]
        
        cls.unit_converter = UnitConverter(cls.test_values, cls.test_units, cls.test_mws)
        return super().setUpClass()
    
    def test_to_molar(self):
        molars = self.unit_converter.to_molar()
        
        self.assertIsInstance(
            molars,
            pd.Series
        )
        
        expected = np.array([
            250e-6,
            10e-6,
            np.nan,
            np.nan,
            2000e-12
        ])
        
        self.assertTrue(
            np.allclose(
                molars.to_numpy(),
                expected,
                equal_nan=True  # np.nan does not evaluate equal
            )
        )
        
    def test_to_neg_log_molar(self):
        neg_log_molars = self.unit_converter.to_neg_log_molar()
        
        self.assertIsInstance(
            neg_log_molars,
            pd.Series
        )
        
        expected = np.array([
            3.60206,
            5,
            np.nan,
            np.nan,
            8.69897
        ])
        
        self.assertTrue(
            np.allclose(
                neg_log_molars.to_numpy(),
                expected,
                equal_nan=True
            )
        )
        
if __name__ == '__main__':
    unittest.main()
