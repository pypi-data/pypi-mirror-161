from math import log10
import unittest
import json
import pandas as pd
import numpy as np
from naclo import Bleach, bleach_default_options, bleach_default_params
import warnings
from rdkit import Chem
import copy


class TestBleach(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.default_params = bleach_default_params
        cls.default_options = bleach_default_options
            
        cls.smiles_df = pd.DataFrame({
            'SMILES': ['Cc1cc(/C=C/C#N)cc(C)c1Nc1nc(Nc2ccc(C#N)cc2)ncc1N',
                       'Cc1cc(/C=C/C#N)cc(C)c1Nc1ncc(N)c(Nc2c(C)cc(/C=C/C#N)cc2C)n1',
                       'CCC',
                       'CCC.Cl',
                       'C.NO.S',
                       'Br',
                       '']
        })
        
        warnings.filterwarnings('error')  # Catch in try except
        
        return super().setUpClass()
    
    def test_param_checker(self):
        params = copy.deepcopy(self.default_params)
        options = copy.deepcopy(self.default_options)
        
        try:
            Bleach(self.smiles_df, params, options)
        except ValueError as e:
            self.assertEqual(
                e.args[0],
                'NO_STRUCTURE_COLUMN'
            )
        
        params['structure_col'] = 'test'
        try:
            Bleach(self.smiles_df, params, options)
        except ValueError as e:
            self.assertEqual(
                e.args[0],
                'STRUCTURE_COLUMN_NOT_FOUND'
            )
        
        params['structure_col'] = 'SMILES'
        try:
            Bleach(self.smiles_df, params, options)
        except ValueError as e:
            self.assertEqual(
                e.args[0],
                'INVALID_STRUCTURE_TYPE'
            )
        
        params['structure_type'] = 'smiles'
        params['target_col'] = 'test'
        try:
            Bleach(self.smiles_df, params, options)
        except ValueError as e:
            self.assertEqual(
                e.args[0],
                'TARGET_COLUMN_NOT_FOUND'
            )
        
        # Should run fine
        params['target_col'] = 'SMILES'
        Bleach(self.smiles_df, params, options)
        
    def test_recognized_options_checker(self):
        params = copy.deepcopy(self.default_params)
        options = copy.deepcopy(self.default_options)
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        options['molecule_settings']['neutralize_charges']['run'] = 42
        
        try:
            Bleach(self.smiles_df, params, options)
        except ValueError as e:
            self.assertEqual(
                list(e.args[0].keys())[0],
                'BAD_OPTION_MOLECULE_SETTINGS_NEUTRALIZE_CHARGES_RUN'
            )

    def test_drop_na(self):
        df = pd.DataFrame({
            'SMILES': [
                pd.NA,
                '',
                'nan',
                'none',
                'CCC',
                np.nan
            ],
            'ROMol': [
                pd.NA,
                '',
                'nan',
                'C',
                'none',
                np.nan
            ],
            'drop_empty': 6*[np.nan]
        })
        
        params = copy.deepcopy(self.default_params)
        
        # SMILES
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        
        bleach = Bleach(df, params, self.default_options)
        bleach.drop_na()
        
        expected = pd.DataFrame({
            'SMILES': ['CCC']
        }, index=[4])
        
        self.assertEqual(
            True,
            bleach.df.equals(expected)
        )
        
        # ROMol
        params['structure_col'] = 'ROMol'
        params['structure_type'] = 'mol'
        
        bleach = Bleach(df, params, self.default_options)
        bleach.drop_na()
        
        expected = pd.DataFrame({
            'ROMol': ['C']
        }, index=[3])
        
        self.assertEqual(
            True,
            bleach.df.equals(expected)
        )
        
        # ALL_NA_STRUCTURES warning
        params['structure_col'] = 'drop_empty'
        
        bleach = Bleach(df, params, self.default_options)
        
        try:
            bleach.drop_na()
        except RuntimeWarning as w:
            self.assertEqual(
                w.args[0],
                'ALL_NA_STRUCTURES: All structures in specified column were NA, all rows dropped'
            )
            
        # ALL_NA_TARGETS warning
        params['structure_col'] = 'ROMol'
        params['target_col'] = 'drop_empty'
        
        # Not set to drop NA targets
        bleach = Bleach(df, params, self.default_options)
        bleach.drop_na()
        
        expected = pd.DataFrame({
            'ROMol': ['C']
        }, index=[3])
        
        self.assertEqual(
            True,
            bleach.df.equals(expected)
        )
        
        # Set to drop NA targets
        options = copy.deepcopy(self.default_options)
        options['file_settings']['remove_na_targets']['run'] = True
        
        bleach = Bleach(df, params, options)
        
        try:
            bleach.drop_na()
        except RuntimeWarning as w:
            self.assertEqual(
                w.args[0],
                'ALL_NA_TARGETS: All targets in specified column were NA, all rows dropped'
            )
            
    def test_init_structure_compute(self):
        # From SMILES
        params = copy.deepcopy(self.default_params)
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        
        bleach = Bleach(self.smiles_df, params, self.default_options)
        bleach.drop_na()
        bleach.init_structure_compute()

        [self.assertIsInstance(m, Chem.rdchem.Mol) for m in bleach.df['ROMol']]
        
        # From SMILES w/ bad Mols
        mol_df = bleach.df.copy()
        
        new_row = pd.DataFrame({
            'SMILES': ['CC', 'C', 'CCC'],
            'ROMol': ['test', 1, 'CCC']
        })
        
        mol_df = pd.concat((mol_df, new_row))
        bleach = Bleach(mol_df, params, self.default_options)
        bleach.drop_na()
        bleach.init_structure_compute()
        
        self.assertEqual(
            bleach.df['SMILES'].tolist(),
            mol_df['SMILES'].tolist()
        )
        [self.assertIsInstance(m, Chem.rdchem.Mol) for m in bleach.df['ROMol']]
        
        # From Mols w/ bad Mols
        params['structure_col'] = 'ROMol'
        params['structure_type'] = 'mol'
        bleach = Bleach(mol_df, params, self.default_options)
        bleach.drop_na()
        bleach.init_structure_compute()
        
        [self.assertIsInstance(m, Chem.rdchem.Mol) for m in bleach.df['ROMol']]
        self.assertEqual(
            len(bleach.df),
            6
        )
        self.assertEqual(
            bleach.df['SMILES'].tolist(),
            self.smiles_df['SMILES'].tolist()[:-1]  # Excluding blank
        )
        
    def test_convert_units(self):
        df = pd.DataFrame({
            'SMILES': ['CCC', 'C', 'CCC', 'CC'],
            'value': [1, 2, np.nan, 3],
            'units': [np.nan, 'nm', 'm', 'pg ml-1']
        })
        
        params = copy.deepcopy(self.default_params)
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        
        options = copy.deepcopy(self.default_options)
        options['molecule_settings']['convert_units'] = {
            'units_col': 'units',
            'output_units': 'molar',
            'drop_na': True
        }
        
        # Warning: no target value column
        bleach = Bleach(df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        
        with self.assertRaises(RuntimeWarning):
            bleach.convert_units()
        
        
        # molar units
        params['target_col'] = 'value'
        bleach = Bleach(df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.convert_units()
        
        self.assertEqual(
            list(bleach.df.columns),
            list(df.columns) + ['ROMol', 'molar_units']
        )
        self.assertTrue(
            bleach.df.drop(columns=['ROMol', 'molar_units']).equals(
                df.dropna(subset=['units', 'value'])
            )
        )
        molar_units = bleach.df['molar_units'].tolist()
        
        # neg_log_molar units
        options['molecule_settings']['convert_units']['output_units'] = 'neg_log_molar'
        bleach = Bleach(df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.convert_units()
        
        self.assertEqual(
            list(bleach.df.columns),
            list(df.columns) + ['ROMol', 'neg_log_molar_units']
        )
        self.assertTrue(
            bleach.df.drop(columns=['ROMol', 'neg_log_molar_units']).equals(
                df.dropna(subset=['units', 'value'])
            )
        )
        neg_log_molar_units = bleach.df['neg_log_molar_units'].tolist()
        
        # Dont drop NA units
        options['molecule_settings']['convert_units']['drop_na'] = False
        bleach = Bleach(df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.convert_units()
        
        self.assertEqual(
            list(bleach.df.columns),
            list(df.columns) + ['ROMol', 'neg_log_molar_units']
        )
        self.assertTrue(
            bleach.df.drop(columns=['ROMol', 'neg_log_molar_units']).equals(
                df
            )
        )
        
        # neg_log_molar is true
        self.assertEqual(
            neg_log_molar_units,
            [-1 * log10(m) for m in molar_units]
        )
        
    def test_mol_cleanup(self):
        params = copy.deepcopy(self.default_params)
        options = copy.deepcopy(self.default_options)
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        
        # Salts only
        options['molecule_settings']['remove_fragments']['salts'] = True
        options['molecule_settings']['remove_fragments']['filter_method'] = 'none'
        options['molecule_settings']['neutralize_charges']['run'] = False
        bleach = Bleach(self.smiles_df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        df = bleach.mol_cleanup()
        expected = pd.DataFrame({
            'SMILES': ['Cc1cc(/C=C/C#N)cc(C)c1Nc1nc(Nc2ccc(C#N)cc2)ncc1N',
                       'Cc1cc(/C=C/C#N)cc(C)c1Nc1ncc(N)c(Nc2c(C)cc(/C=C/C#N)cc2C)n1',
                       'CCC',
                       'CCC',
                       'C.NO.S']
        })
        
        self.assertTrue(
            bleach.df['SMILES'].equals(expected['SMILES'])
        )
        
        # Filter only: carbon count
        options['molecule_settings']['remove_fragments']['salts'] = False
        options['molecule_settings']['remove_fragments']['filter_method'] = 'carbon_count'
        options['molecule_settings']['neutralize_charges']['run'] = False
        bleach = Bleach(self.smiles_df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        
        self.assertEqual(
            bleach.df['SMILES'].iloc[-2],
            'C'
        )
        
        # Filter only: atom count
        options['molecule_settings']['remove_fragments']['salts'] = False
        options['molecule_settings']['remove_fragments']['filter_method'] = 'atom_count'
        options['molecule_settings']['neutralize_charges']['run'] = False
        bleach = Bleach(self.smiles_df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        
        self.assertEqual(
            bleach.df['SMILES'].iloc[-2],
            'NO'
        )
        
        # Filter only: molecular weight
        options['molecule_settings']['remove_fragments']['salts'] = False
        options['molecule_settings']['remove_fragments']['filter_method'] = 'mw'
        options['molecule_settings']['neutralize_charges']['run'] = False
        bleach = Bleach(self.smiles_df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        
        self.assertEqual(
            bleach.df['SMILES'].iloc[-2],
            'S'
        )
        
        # Salts + filter together
        options['molecule_settings']['remove_fragments']['salts'] = True
        options['molecule_settings']['remove_fragments']['filter_method'] = 'carbon_count'
        options['molecule_settings']['neutralize_charges']['run'] = False
        bleach = Bleach(self.smiles_df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        expected = pd.DataFrame({
            'SMILES': ['Cc1cc(/C=C/C#N)cc(C)c1Nc1nc(Nc2ccc(C#N)cc2)ncc1N',
                       'Cc1cc(/C=C/C#N)cc(C)c1Nc1ncc(N)c(Nc2c(C)cc(/C=C/C#N)cc2C)n1',
                       'CCC',
                       'CCC',
                       'C']
        })
        
        self.assertTrue(
            bleach.df['SMILES'].equals(expected['SMILES'])
        )
        
    def test_handle_duplicates(self):
        params = copy.deepcopy(self.default_params)
        options = copy.deepcopy(self.default_options)
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        params['target_col'] = 'target'
        
        df = self.smiles_df.copy()
        df['target'] = [1, 2, 3, 4, 5, 6, 7]
        
        # Average
        bleach = Bleach(df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        bleach.handle_duplicates()
        
        expected = pd.DataFrame({
            'SMILES': ['Cc1cc(/C=C/C#N)cc(C)c1Nc1nc(Nc2ccc(C#N)cc2)ncc1N',
                       'Cc1cc(/C=C/C#N)cc(C)c1Nc1ncc(N)c(Nc2c(C)cc(/C=C/C#N)cc2C)n1',
                       'CCC',
                       'C'],
            
            'InchiKey': [
                'NFQWIYBXPYHNRC-ONEGZZNKSA-N',
                'IKTVSGAURLVDFP-KQQUZDAGSA-N',
                'ATUOYWHBWRKTHZ-UHFFFAOYSA-N',
                'VNWKTOKETHGBQD-UHFFFAOYSA-N'],
            
            'target': [1,
                       2,
                       3.5,
                       5]
        })

        self.assertTrue(
            bleach.df[['SMILES', 'InchiKey', 'target']].reset_index(drop=True).equals(expected)
        )
        
        # Remove
        options['file_settings']['duplicate_compounds']['selected'] = 'remove'
        bleach = Bleach(df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        bleach.handle_duplicates()
        
        expected['target'] = [1, 2, 3, 5]
        
        self.assertTrue(
            bleach.df[['SMILES', 'InchiKey', 'target']].reset_index(drop=True).equals(expected)
        )
        
        # Keep
        options['file_settings']['duplicate_compounds']['selected'] = 'keep'
        bleach = Bleach(df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        
        df1 = bleach.df.copy()
        bleach.handle_duplicates()
        df2 = bleach.df.copy().drop('InchiKey', axis=1)
        
        self.assertTrue(
            df1.equals(df2)
        )
        
        self.assertIn(
            'InchiKey',
            bleach.df.columns
        )
        
    def test_append_column(self):
        params = copy.deepcopy(self.default_params)
        options = copy.deepcopy(self.default_options)
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        
        # All columns
        bleach = Bleach(self.smiles_df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        bleach.handle_duplicates()
        bleach.append_columns()
        
        self.assertEqual(
            ['SMILES', 'ROMol', 'InchiKey', 'MW'],
            list(bleach.df.columns)
        )
        
        # No columns (except SMILES for testing purposes)
        options['file_settings']['append_columns'] = {
            'smiles': True,
            'mol': False,
            'inchi_key': False,
            'mw': False
        }
        
        bleach = Bleach(self.smiles_df, params, options)
        bleach.drop_na()
        bleach.init_structure_compute()
        bleach.mol_cleanup()
        bleach.handle_duplicates()
        bleach.append_columns()
        
        self.assertEqual(
            ['SMILES'],
            list(bleach.df.columns)
        )
        
    def test_remove_header_chars(self):
        params = copy.deepcopy(self.default_params)
        options = copy.deepcopy(self.default_options)
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        
        options['file_settings']['remove_header_chars']['chars'] = 'sr'
        
        bleach = Bleach(self.smiles_df, params, options)
        bleach.main()
        
        self.assertEqual(
            ['MILE', 'OMol', 'InchiKey', 'MW'],
            list(bleach.df.columns)
        )
    
    def test_main(self):
        params = copy.deepcopy(self.default_params)
        params['structure_col'] = 'SMILES'
        params['structure_type'] = 'smiles'
        
        options = copy.deepcopy(self.default_options)
        bleach = Bleach(self.smiles_df, params, options)
        
        bleach.mol_cleanup()


if __name__ == '__main__':
    unittest.main()
