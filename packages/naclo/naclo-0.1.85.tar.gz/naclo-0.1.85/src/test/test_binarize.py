import unittest
import pandas as pd
import numpy as np
from copy import deepcopy
from rdkit.Chem import MolFromSmiles
from rdkit.Chem.Descriptors import ExactMolWt
from math import log10

from naclo import binarize_default_params, binarize_default_options
from naclo import Binarize


class TestBinarize(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.default_params = binarize_default_params
        cls.default_options = binarize_default_options
        
        cls.test_df = pd.DataFrame({
            'smiles': [
                'CCC',
                'C',
                'CN=C=O',
                'CN(C)C.Cl',
                None
            ],
            'target': [
                55,
                4,
                7,
                '100',  # For testing string -> float conversion
                2000
            ],
            'units': [
                'ug•ml-1',
                'mg/l',
                'unrecognized',
                np.nan,
                'pm'
            ],
            'qualifiers': [
                '>',
                '<',
                '=',
                '',
                '<'
            ]
        })
        
        cls.default_params['structure_col'] = 'smiles'
        cls.default_params['structure_type'] = 'smiles'
        cls.default_params['target_col'] = 'target'
        cls.default_params['decision_boundary'] =  7  # neg log molar
        
        return super().setUpClass()
    
    def test_convert_units(self):
        options = deepcopy(self.default_options)
        options['convert_units']['units_col'] = 'units'
        
        first_two_rows = self.test_df.iloc[:2]
        
        mws = [ExactMolWt(MolFromSmiles(smi)) for smi in first_two_rows['smiles']]
        targets = first_two_rows['target']
        conversion_factor = 1e-3  # ug/ml and mg/l are the same
        
        first_two_expected = (targets*conversion_factor / mws).tolist()
        
        expected_molar = first_two_expected + 2*[np.nan]
        
        binarize = Binarize(self.test_df, params=self.default_params, options=options)
        
        # Molar
        self.assertTrue(
            np.allclose(
                binarize.convert_units('molar'),
                expected_molar, 
                equal_nan=True
            )
        )
        
        # -log(Molar)
        self.assertTrue(
            np.allclose(
                binarize.convert_units('neg_log_molar'),
                [-1*log10(x) for x in expected_molar],
                equal_nan=True
            )
        )
        
        # Nanomolar
        self.assertTrue(
            np.allclose(
                binarize.convert_units('nanomolar'),
                [1e9*x for x in expected_molar],
                equal_nan=True
            )
        )
        
        # Unknown units
        with self.assertRaises(ValueError):
            binarize.convert_units('unknown')
        
    def test_binarize_no_qualifiers(self):
        options = deepcopy(self.default_options)
        options['qualifiers']['run'] = False
        
        expected_arrs = {
            '>': [1, 0, 0, 1, 1],
            '<': [0, 1, 0, 0, 0],
            '>=': [1, 0, 1, 1, 1],
            '<=': [0, 1, 1, 0, 0]
        }
        
        # Loop through allowed operators
        for options['active_operator'] in ['>', '<', '>=', '<=']:
            binarize = Binarize(self.test_df, params=self.default_params, options=options)
            out_df, out_arr = binarize.binarize(self.test_df['target'])

            self.assertTrue(
                out_df.equals(binarize.df)  # No qualifier drop bc no qualifiers
            )
            
            self.assertTrue(
                np.array_equal(
                    list(expected_arrs[options['active_operator']]),
                    out_arr
                )
            )

        # Unknown operator
        options['active_operator'] = 'unknown'
        with self.assertRaises(ValueError):
            binarize = Binarize(self.test_df, params=self.default_params, options=options)
            binarize.binarize(self.test_df['target'])
        
    def test_binarize_with_qualifiers(self):
        options = deepcopy(self.default_options)
        options['qualifiers']['run'] = True
        options['qualifiers']['qualifier_col'] = 'qualifiers'
        
        expected_arrs = {
            '>': [1, 0, 0],
            '<': [0, 1, 0],
            '>=': [1, 0, 1],
            '<=': [0, 1, 1]
        }
        
        # Loop through allowed operators
        for options['active_operator'] in ['>', '<', '>=', '<=']:
            binarize = Binarize(self.test_df, params=self.default_params, options=options)
            out_df, out_arr = (binarize.binarize(self.test_df['target'][:-1]))
            
            self.assertTrue(
                out_df.equals(binarize.df.dropna(subset=['qualifiers']))
            )
            
            self.assertTrue(
                np.array_equal(
                    list(expected_arrs[options['active_operator']]),
                    out_arr
                )
            )
        
        # Unknown operator
        options['active_operator'] = 'unknown'
        with self.assertRaises(ValueError):
            binarize = Binarize(self.test_df, params=self.default_params, options=options)
            binarize.binarize(self.test_df['target'][:-1])
            
    def test_handle_duplicates(self):
        input_df = pd.DataFrame({
            'smiles': ['CC', 'CC', 'CCC', 'CCC', 'CCC', 'CCC', 'CCC', 'O=S=O', 'O=S=O', 'O=S=O', 'O'],
            'bin': [0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1]
        })
        
        # Agree ratio of 0.8
        expected_df = pd.DataFrame({
            'smiles': ['CC', 'CCC', 'O'],  # SO2 dropped bc bad ratio
            'bin': [0, 1, 1]
        })
        out = Binarize.handle_duplicates(input_df, 'smiles', 'smiles', 'bin', agree_ratio=0.8)
        self.assertTrue(
            out.equals(expected_df)
        )
        
        # Agree ratio of 0.3
        expected_df = pd.DataFrame({
            'smiles': ['CC', 'CCC', 'O=S=O', 'O'],
            'bin': [0, 1, 0, 1]
        })
        out = Binarize.handle_duplicates(input_df, 'smiles', 'smiles', 'bin', agree_ratio=0.6)
        self.assertTrue(
            out.equals(expected_df)
        )
        
    def test_main(self):
        options = {
            'duplicates': {
                'run': False,
                'agree_ratio': 0.8
            },
            'convert_units': {
                'units_col': 'units',
                'output_units': 'molar'
            },
            'qualifiers': {
                'run': True,
                'qualifier_col': 'qualifiers'
            },
            'active_operator': '<=',
            'drop_na': False
        }

        # Drop NA = False
        binarize = Binarize(self.test_df, params=self.default_params, options=options)
        out = binarize.main()
        
        self.assertEqual(
            out['smiles'].tolist(),
            ['CCC', 'C', 'CN=C=O']
        )
        self.assertEqual(
            out['target'].tolist(),
            [55, 4, 7]
        )
        self.assertEqual(
            out['units'].tolist(),
            ['ug•ml-1', 'mg/l', 'unrecognized']
        )
        self.assertEqual(
            out['qualifiers'].tolist(),
            ['>', '<', '=']
        )
        self.assertTrue(
            np.allclose(
                out['molar_target'].tolist(),
                [0.001248224110253472, 0.0002495118903683718, np.nan],
                equal_nan=True
            )
        )
        self.assertTrue(
            np.allclose(
                out['binarized_target'].tolist(),
                [np.nan, 1, np.nan],
                equal_nan=True
            )
        )
        
        # Drop NA = True
        options['drop_na'] = True
        binarize = Binarize(self.test_df, params=self.default_params, options=options)
        out = binarize.main()
        
        expected = pd.DataFrame({
            'smiles': ['C'],
            'target': [4],
            'units': ['mg/l'],
            'qualifiers': ['<'],
            'molar_target': [0.00025],
            'binarized_target': [1.0]
        })
        out['molar_target'] = out['molar_target'].apply(lambda x: np.round(x, 5))  # Round to 5 decimals
        
        self.assertTrue(
            np.array_equal(
                out.to_numpy(),
                expected.to_numpy()
            )
        )


if __name__ == '__main__':
    unittest.main()
