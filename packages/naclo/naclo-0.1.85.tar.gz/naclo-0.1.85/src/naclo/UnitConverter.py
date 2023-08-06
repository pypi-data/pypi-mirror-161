from logging import warning
from math import log10
import pandas as pd
import numpy as np
from copy import copy
from typing import Union, Iterable

from naclo.__asset_loader import recognized_units


class UnitConverter:
    __recognized_units = copy(recognized_units)
    __standard_unit_col = 'standard_unit'
    __multiplier_col = 'multiplier'
    
    def __init__(self, values:Iterable, units:Iterable, mol_weights:Iterable) -> None:
        # Column names
        self.__unit_col = 'unit'
        self.__value_col = 'value'
        self.__mw_col = 'mol_weight'
        
        self.df = pd.DataFrame({
            self.__unit_col: copy(units),
            self.__value_col: copy(values),
            self.__mw_col: copy(mol_weights)
        })
        
        # Unit groups
        self.molar = [
            'pm',
            'nm',
            'um',
            'mm',
            'm'
        ]
        self.g_ovr_l = [
            'pg/l',
            'ng/l',
            'ug/l',
            'mg/l',
            'm/l',
            'pg/ml',
            'ng/ml',
            'ug/ml',
            'mg/ml',
            'm/ml'
        ]
        
        self.df = UnitConverter.standardize_units(self.df, self.__unit_col)
    
    @staticmethod
    def __neg_log(val:Union[int, float, np.number]) -> float:
        """Simple negative log10 computation.

        Args:
            val (Union[int, float, np.number]): Value to use for computation.

        Returns:
            float: Computed value.
        """
        if val < 0:
            warning(f'Negative value {val} passed to UnitConverter.__neg_log().')
            return np.nan
        elif val == 0:
            return 0
        else:
            return -1*log10(val)
    
    @staticmethod
    def standardize_units(df, unit_col_name) -> pd.DataFrame:
        """Appends standard units and multipliers found in naclo/assets/recognized_units.json to self.df. Appends
        np.nan if unit is not recognized."""
        standard_units = []
        multipliers = []
        
        for unit in df[unit_col_name]:
            try:
                standard_unit, multiplier = UnitConverter.__recognized_units[f'{unit}'.lower()]
                standard_units.append(standard_unit)
                multipliers.append(multiplier)
            except KeyError:
                standard_units.append(np.nan)
                multipliers.append(np.nan)
                continue
            
        df[UnitConverter.__standard_unit_col] = standard_units
        df[UnitConverter.__multiplier_col] = multipliers
        return df
            
    def __to_molar_broadcaster(self, row:pd.Series) -> float:
        """Broadcasting function to use with pd.DataFrame.apply(). Computes molar values from self.df.

        Args:
            row (pd.Series): pd.DataFrame row passed in apply().

        Returns:
            Union[float]: Molar value. np.nan if the standard unit is not found in self.molar or self.g_ovr_l.
        """
        if row[self.__standard_unit_col] in self.molar:
            molar_val = float(row[self.__value_col])*row[self.__multiplier_col]
        elif row[self.__standard_unit_col] in self.g_ovr_l:  # Divide by mw (g/mol) -> g/L * mol/g = M
            molar_val = float(row[self.__value_col])*row[self.__multiplier_col]/row[self.__mw_col]  # Divide by mw
        else:
            molar_val = np.nan
        return molar_val
    
    def to_molar(self) -> pd.Series:
        """Applies self.__to_molar_broadcaster to self.df.

        Returns:
            pd.Series: Molar values.
        """
        return self.df.apply(self.__to_molar_broadcaster, axis=1)
            
    def to_neg_log_molar(self) -> pd.Series:
        """Applies self.__to_molar_broadcaster and self.__neg_log to self.df.

        Returns:
            pd.Series: Negative log molar values.
        """
        return self.to_molar().apply(self.__neg_log)
