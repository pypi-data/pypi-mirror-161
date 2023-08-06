import pandas as pd
import warnings
from typing import Callable, Dict, Union, Optional

# sourced from github.com/jwgerlach00
import naclo
import stse
from naclo.__asset_loader import recognized_bleach_options as recognized_options
from naclo.__asset_loader import bleach_default_params as default_params
from naclo.__asset_loader import bleach_default_options as default_options
from naclo.__naclo_util import recognized_options_checker


class Bleach:
    filter_fragments_methods = ['carbon_count', 'mw', 'atom_count', 'none']
    
    def __init__(self, df:pd.DataFrame, params:dict=default_params, options:dict=default_options) -> None:  # *
        # Load user options
        self.mol_settings = options['molecule_settings']
        self.file_settings = options['file_settings']
        recognized_options_checker(options, recognized_options)

        self.__recognized_structures = ['smiles', 'mol']
        self.__default_cols = {
            'smiles': 'SMILES',
            'mol': 'ROMol',
            'inchi_key': 'InchiKey',
            'mw': 'MW'
        }

        # Save user input data
        self.original_df = df.copy()
        self.df = df.copy()

        # Load file parameters
        self.structure_col = params['structure_col']
        self.structure_type = params['structure_type']
        self.target_col = params['target_col']
        self.__param_checker()

        self.mol_col = None
        self.smiles_col = None
        self.inchi_key_col = None
        self.__set_structure_cols()  # Assign mol and SMILES cols using input + defaults
        
        # Set staticmethods to instance methods
        self.convert_units = self.__instance_convert_units
        self.mol_cleanup = self.__instance_mol_cleanup
        self.handle_duplicates = self.__instance_handle_duplicates
        self.append_columns = self.__instance_append_columns
        self.remove_header_chars = self.__instance_remove_header_chars


# -------------------------------------------------- ERROR CHECKING -------------------------------------------------- #
    def __param_checker(self) -> None:  # *
        """Checks for errors related to declared parameters.

        Raises:
            ValueError: NO_STRUCTURE_COLUMN
            ValueError: STRUCTURE_COLUMN_NOT_FOUND
            ValueError: INVALID_STRUCTURE_TYPE
            ValueError: TARGET_COLUMN_NOT_FOUND
        """
        if not self.structure_col:
            raise ValueError('NO_STRUCTURE_COLUMN', 'Must specify the name of the structure column in params')

        if self.structure_col not in self.df.columns:
            raise ValueError('STRUCTURE_COLUMN_NOT_FOUND', f'The structure column: "{self.structure_col}"" is not \
                present in the data: "{list(self.df.columns)}"')

        if self.structure_type not in self.__recognized_structures:
            raise ValueError('INVALID_STRUCTURE_TYPE', f'Structure type: "{self.structure_type}"" is not one of: \
                {self.__recognized_structures}')

        if self.target_col and self.target_col not in self.df.columns:
            raise ValueError('TARGET_COLUMN_NOT_FOUND', f'The target column: "{self.target_col}"" is not present in \
                the data: "{list(self.df.columns)}"')


# -------------------------------------------------- PRIVATE METHODS ------------------------------------------------- #
    def __set_structure_cols(self) -> None:
        """Sets Mol and SMILES columns using declared structure type."""
        self.mol_col = self.structure_col if self.structure_type == 'mol' else self.__default_cols['mol']
        self.smiles_col = self.structure_col if self.structure_type == 'smiles' else self.__default_cols['smiles']
        self.inchi_key_col = self.__default_cols['inchi_key']

    def __drop_na_structures(self) -> None:
        """Drops NA along declared structure column."""
        self.df.dropna(subset=[self.structure_col], inplace=True)
        if not len(self.df):
            warnings.warn('ALL_NA_STRUCTURES: All structures in specified column were NA, all rows dropped',
                          RuntimeWarning)

    def __drop_na_targets(self) -> None:
        """Drops NA along declared target column"""
        run_na_targets = self.file_settings['remove_na_targets']['run']

        if self.target_col and run_na_targets and len(self.df):  # If run and TARGET COLUMN DECLARED
            self.df.dropna(subset=[self.target_col], inplace=True)
            if not len(self.df):
                warnings.warn('ALL_NA_TARGETS: All targets in specified column were NA, all rows dropped',
                              RuntimeWarning)

        elif run_na_targets:  # If run but not declared target
            warnings.warn('NA_TARGETS: options.file_settings.remove_na_targets was set to run but no activity column \
                was specified', RuntimeWarning)

    def __build_smiles(self) -> None:
        """Creates a SMILES column in the dataset using dataset MolFile column. DROPS NA."""
        self.df = naclo.dataframes.df_mols_2_smiles(self.df, self.mol_col, self.smiles_col)

    def __build_mols(self) -> None:
        """Creates MolFile column in the dataset using dataset SMILES column. DROPS NA."""
        self.df = naclo.dataframes.df_smiles_2_mols(self.df, self.smiles_col, self.mol_col)
        
    @staticmethod
    def __filter_fragments_factory(filter:str) -> Callable:
        """Returns a callable SMILES fragment filter function using a key.

        Args:
            filter (str): Function key.

        Raises:
            ValueError

        Returns:
            Callable: Filter function.
        """
        if filter == 'carbon_count':
            return naclo.fragments.carbon_count
        elif filter == 'mw':
            return naclo.fragments.mw
        elif filter == 'atom_count':
            return naclo.fragments.atom_count
        else:
            raise ValueError('Filter method is not allowed')

    @staticmethod
    def __remove_fragments(df:pd.DataFrame, smiles_col_name:str, mol_col_name:str, salts:bool,
                           filter_method:Optional[str]) -> pd.DataFrame:
        """Removes salts if specified. Drops NA as a result of salt removal. Filters out other fragments by specified
        method."""
        df = df.copy()
        rebuild_mols = lambda x: naclo.dataframes.df_smiles_2_mols(x, smiles_col_name, mol_col_name)
            
        if salts:
            df[smiles_col_name] = df[smiles_col_name].apply(naclo.fragments.remove_recognized_salts)
            df = rebuild_mols(df)

            # Drop NA (blank string after salts)
            df = stse.dataframes.convert_to_nan(df, na=[''])  # Convert bc NA is just empty string
            df.dropna(subset=[smiles_col_name], inplace=True)  # Drop NA bc may include molecule that is ONLY salts

        # Filter
        if filter_method and filter_method != 'none':
            df[smiles_col_name] = df[smiles_col_name].apply(Bleach.__filter_fragments_factory(filter_method))
            df = rebuild_mols(df)
            
        return df

    @staticmethod
    def __append_inchi_keys(df:pd.DataFrame, mol_col_name:str, inchi_key_col_name:str) -> pd.DataFrame:
        """Declares inchi key column name using default. Appends inchi keys to dataset."""
        return naclo.dataframes.df_mols_2_inchi_keys(df, mol_col_name, inchi_key_col_name)

    @staticmethod
    def __drop_columns(df:pd.DataFrame, column_mapper:Dict[str, bool], mol_col_name:str, smiles_col_name:str,
                       inchi_key_col_name:str) -> pd.DataFrame:
        """Removes columns that the user does not want in the final output."""
        
        # Drop added columns from built if not requested
        if not column_mapper['mol']:
            df = df.drop(mol_col_name, axis=1)
        if not column_mapper['inchi_key']:
            df = df.drop(inchi_key_col_name, axis=1)
        if not column_mapper['smiles']:
            df = df.drop(smiles_col_name, axis=1)
        
        return df

    @staticmethod
    def __add_columns(df:pd.DataFrame, column_mapper:Dict[str, bool], mol_col_name:str) -> pd.DataFrame:
        """Add columns that the user wants in the final output."""
        # Add MW column
        if column_mapper['mw']:
            df = df.assign(MW = naclo.mol_weights(df[mol_col_name]))
        return df


# ---------------------------------------------------- MAIN STEPS ---------------------------------------------------- #
    # Step 1
    def drop_na(self) -> None:  # *
        """Converts blanks to NA. Drops NA Mols or SMILES. Handles NA targets. Removes entire NA columns"""

        # Convert all df blanks and 'none' to NA
        self.df = stse.dataframes.convert_to_nan(self.df)

        # Drop rows
        self.__drop_na_structures()
        self.__drop_na_targets()

        # Drop cols
        self.df = stse.dataframes.remove_nan_cols(self.df)  # After dropping rows because columns may BECOME empty

    # Step 2 
    def init_structure_compute(self) -> None:  # *
        """Builds (or rebuilds from Mols) SMILES. Builds Mols if not present in dataset."""
        if self.structure_type == 'mol':
            self.__build_smiles()
            # Rebuilding Mols not necessary

        elif self.structure_type == 'smiles':
            self.__build_mols()
            self.__build_smiles()  # Canonicalize SMILES
    
    # Step 3
    @staticmethod
    def convert_units(df:pd.DataFrame, mol_col_name:str, value_col_name:str, units_col_name:str,
                      output_units:str, drop_na_units:bool) -> pd.DataFrame:
        df = df.copy()
        
        uc = naclo.UnitConverter(df[value_col_name], df[units_col_name], naclo.mol_weights(df[mol_col_name]))
        
        if output_units == 'molar':
            col_name = f'molar_{units_col_name}'
            df[col_name] = uc.to_molar()
        elif output_units == 'neg_log_molar':
            col_name = f'neg_log_molar_{units_col_name}'
            df[col_name] = uc.to_neg_log_molar()
        else:
            raise ValueError(f'Output units: "{output_units}" are not recognized')
        
        return df.dropna(subset=[col_name]) if drop_na_units else df
    
    def __instance_convert_units(self):
        convert_units = self.mol_settings['convert_units']
        if convert_units['units_col']:
            if not self.target_col:
                warnings.warn('CONVERT_UNITS: options.molecule_settings.convert_units was set to run but no activity \
                    column was specified', RuntimeWarning)
                return
            self.df = Bleach.convert_units(df=self.df, mol_col_name=self.mol_col, value_col_name=self.target_col,
                                           units_col_name=convert_units['units_col'],
                                           output_units=convert_units['output_units'],
                                           drop_na_units=convert_units['drop_na'])

    # Step 4
    @staticmethod
    def mol_cleanup(df:pd.DataFrame, smiles_col_name:str, mol_col_name:str, run_salts:bool, filter_method:Optional[str],
                    run_neutralize:bool) -> pd.DataFrame:  # * (except neutralize)
        """Cleans Mols and SMILES."""
        df = df.copy()

        # Step 1: Deal with fragments (includes salt step -- may include a molecule that is ONLY salts (NA dropped))
        df = Bleach.__remove_fragments(df, smiles_col_name, mol_col_name, run_salts,
                                       filter_method=(None if filter_method == 'none' else filter_method))

        # Step 2: Neutralize mols
        if run_neutralize:
            df[mol_col_name] = naclo.neutralize.neutralize_charges(df[mol_col_name])
            df = naclo.dataframes.df_mols_2_smiles(df, mol_col_name, smiles_col_name)  # Rebuild SMILES
        
        return df
    
    def __instance_mol_cleanup(self) -> None:
        self.df = Bleach.mol_cleanup(self.df, self.smiles_col, self.mol_col,
                                     run_salts=self.mol_settings['remove_fragments']['salts'],
                                     filter_method=self.mol_settings['remove_fragments']['filter_method'],
                                     run_neutralize=self.mol_settings['neutralize_charges']['run'])

    # Step 5
    @staticmethod
    def handle_duplicates(df:pd.DataFrame, mol_col_name:str, inchi_key_col_name:str, target_col:Union[str, None]=None,
                          method='average') -> pd.DataFrame:  # *
        """Computes inchi keys. Averages, removes, or keeps duplicates. ONLY BY INCHI KEY FOR NOW."""
        df = Bleach.__append_inchi_keys(df, mol_col_name, inchi_key_col_name)

        if method == 'average' and target_col:
            df = stse.duplicates.average(df, subsets=[inchi_key_col_name], average_by=target_col)
        elif method == 'remove' or (method == 'average' and not target_col):
            df = stse.duplicates.remove(df, subsets=[inchi_key_col_name])
        return df
    
    def __instance_handle_duplicates(self) -> None:
        self.df = Bleach.handle_duplicates(self.df, self.mol_col, self.inchi_key_col, self.target_col,
                                           method=self.file_settings['duplicate_compounds']['selected'])

    # Step 6
    @staticmethod
    def append_columns(df:pd.DataFrame, column_mapper:Dict[str, bool], mol_col_name:str, smiles_col_name:str,
                       inchi_key_col_name:str) -> pd.DataFrame:  # *
        """Drops and adds columns depending on what the user wants returned.

        Args:
            df (pandas DataFrame): Data to transform
        """
        df = df.copy()
        
        df = Bleach.__drop_columns(df, column_mapper, mol_col_name, smiles_col_name, inchi_key_col_name)
        df = Bleach.__add_columns(df, column_mapper, mol_col_name)
        return df
    
    def __instance_append_columns(self) -> None:
        self.df = Bleach.append_columns(self.df, self.file_settings['append_columns'], self.mol_col, self.smiles_col,
                                        self.inchi_key_col)

    # Step 7
    @staticmethod
    def remove_header_chars(df, chars) -> pd.DataFrame:  # *
        """Removes any chars listed in a string of chars from the df column headers.
        """
        return stse.dataframes.remove_header_chars(df, chars)
    
    def __instance_remove_header_chars(self) -> None:
        self.df = Bleach.remove_header_chars(self.df, self.file_settings['remove_header_chars']['chars'])


# ----------------------------------------------------- MAIN LOOP ---------------------------------------------------- #
    def main(self) -> pd.DataFrame:
        """Main bleach loop.

        Returns:
            pandas DataFrame: Cleaned df
        """
        self.drop_na()  # Before init_structure bc need NA
        self.init_structure_compute()
        self.convert_units()
        self.mol_cleanup()
        self.handle_duplicates()
        self.append_columns()
        self.remove_header_chars()
        return self.df
