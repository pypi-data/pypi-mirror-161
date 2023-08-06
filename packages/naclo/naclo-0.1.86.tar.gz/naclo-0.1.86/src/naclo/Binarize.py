from typing import Iterable, List, Optional, Tuple, Union
import warnings
import pandas as pd
from copy import copy
import numpy as np

import naclo
import stse
from stse.dataframes import sync_na_drop
from naclo.__asset_loader import recognized_binarize_options
from naclo.__naclo_util import recognized_options_checker, check_columns_in_df

class Binarize:
    def __init__(self, df:pd.DataFrame, params:dict, options:dict) -> None:
        self.df = df.copy()
        
        self.__options = copy(options)
        recognized_options_checker(options, recognized_binarize_options)
        
        # Params
        self.__structure_col = params['structure_col']
        self.__structure_type = params['structure_type']
        self.__target_col = params['target_col']  # Set to standard_value col if doing unit conversion
        self.__decision_boundary = float(params['decision_boundary'])  # Cast to float for comparison w/ values
        self.binarized_col_name = f'binarized_{self.__target_col}'
        
        # Drop NA structures and targets
        self.df = stse.dataframes.convert_to_nan(self.df)
        self.df.dropna(subset=[self.__structure_col], inplace=True)
        self.df.dropna(subset=[self.__target_col], inplace=True)
        
        # Check all needed columns exist in df
        cols_to_check = [self.__structure_col, self.__target_col]
        if self.__options['convert_units']['units_col']:
            cols_to_check.append(self.__options['convert_units']['units_col'])
        if self.__options['qualifiers']['run']:
            cols_to_check.append(self.__options['qualifiers']['qualifier_col'])
        check_columns_in_df(self.df, cols_to_check)
        
        # Instance methods
        self.handle_duplicates = self.__instance_handle_duplicates
        self.binarize = self.__instance_binarize
        self.convert_units = self.__instance_convert_units
    
    @staticmethod
    def __mol_weights(df:pd.DataFrame, structure_type:str, structure_col_name:str) -> List[float]:
        if structure_type == 'smiles':
            mols = naclo.smiles_2_mols(df[structure_col_name])
        elif structure_type == 'mol':
            mols = df[structure_col_name]
        return naclo.mol_stats.mol_weights(mols)
    
    @staticmethod
    def convert_units(df:pd.DataFrame, structure_col_name:str, target_col_name:str, units_col_name:str, structure_type:str, output_units:str) -> pd.DataFrame:
        # target_col == standard_value col in this case
        mws = Binarize.__mol_weights(df=df, structure_type=structure_type, structure_col_name=structure_col_name)
        unit_converter = naclo.UnitConverter(values=df[target_col_name],
                                             units=df[units_col_name],
                                             mol_weights=mws)
        if output_units == 'neg_log_molar':
            return unit_converter.to_neg_log_molar()
        elif output_units == 'molar':
            return unit_converter.to_molar()
        elif output_units == 'nanomolar':
            return unit_converter.to_molar()*1e9
        else:
            raise ValueError(f'Unrecognized output units: {output_units}')
        
    def __instance_convert_units(self, output_units):
        return Binarize.convert_units(df=self.df, structure_col_name=self.__structure_col,
                                      target_col_name=self.__target_col,
                                      units_col_name=self.__options['convert_units']['units_col'],
                                      structure_type=self.__structure_type, output_units=output_units)

    @staticmethod
    def handle_duplicates(df:pd.DataFrame, structure_type:str, structure_col_name:str, bin_value_col_name:str,
                          agree_ratio:float=.8) -> pd.DataFrame:
        if agree_ratio < 0 or agree_ratio > 1:
            raise ValueError('Agree ratio must be between 0 and 1')
        elif agree_ratio == 0.5:
            warnings.warn(f'Agree ratio of 0.5 will yield a 1 if structures are in 50{0} agreement'.format('%'))
        
        if structure_type == 'smiles':
            df = naclo.dataframes.df_smiles_2_inchi_keys(df, structure_col_name, 'inchi_key')
        elif structure_type == 'mol':
            df = naclo.dataframes.df_mols_2_inchi_keys(df, structure_col_name, 'inchi_key')
        else:
            raise ValueError(f'Unrecognized structure type: {structure_type}')
        
        avg_df = stse.duplicates.average(df, subsets=['inchi_key'], average_by=bin_value_col_name) \
            .reset_index(drop=True)

        new_bins = []
        for i, val in enumerate(avg_df[bin_value_col_name]):
            if val >= agree_ratio:  # NOTE: Will default to 1 if agree ratio is set to 0.5
                new_bins.append(1)
            elif val <= 1 - agree_ratio:
                new_bins.append(0)
            else:
                avg_df.drop(index=i, inplace=True)
        avg_df[bin_value_col_name] = new_bins
        
        return avg_df.reset_index(drop=True).drop(columns=['inchi_key'])
    
    def __instance_handle_duplicates(self) -> pd.DataFrame:
        self.df = Binarize.handle_duplicates(self.df, self.__structure_type, self.__structure_col,
                                             self.binarized_col_name, self.__options['duplicates']['agree_ratio'])
        return self.df
        
    @staticmethod
    def binarize(df:pd.DataFrame, values:Iterable, decision_boundary:Union[int, float, np.number], active_operator:str,
                 qualifier_col_name:Optional[str]=None) -> Tuple[pd.DataFrame, np.array]:
        if qualifier_col_name:
            df, values = sync_na_drop(df, qualifier_col_name, values, all_na=True)  # Drop NA
            # qualifiers = [q.replace('\'', '') for q in df[qualifier_col_name].tolist()]
            qualifiers = [q.replace('\'', '') for q in df[qualifier_col_name].tolist()]
        else:
            qualifiers = None
        
        values = np.array(values, dtype=float)  # Cast any strings to floats
            
        binarizer = stse.Binarizer(values=values, boundary=decision_boundary, active_operator=active_operator,
                                   qualifiers=qualifiers)
        return df, binarizer.binarize()
    
    def __instance_binarize(self, values:Iterable):
        qualifier_col_name = self.__options['qualifiers']['qualifier_col'] if self.__options['qualifiers']['run'] \
            else None
            
        return Binarize.binarize(df=self.df, values=values, decision_boundary=self.__decision_boundary,
                                 active_operator=self.__options['active_operator'],
                                 qualifier_col_name=qualifier_col_name)
    
    def main(self) -> pd.DataFrame:
        if self.__options['convert_units']['units_col']:
            # Convert and append units
            output_units = self.__options['convert_units']['output_units']
            converted_values = self.convert_units(output_units).tolist()
            
            self.df[f'{output_units}_{self.__target_col}'] = converted_values
            self.df, bin_values = self.binarize(converted_values)
            self.df[self.binarized_col_name] = bin_values
        else:
            self.df[self.binarized_col_name] = self.binarize(self.df[self.__target_col].tolist())
            
        if self.__options['duplicates']['run']:
            self.df = self.handle_duplicates()
            
        if self.__options['drop_na']:
            self.df.dropna(subset=[self.binarized_col_name], inplace=True)
        
        return self.df
