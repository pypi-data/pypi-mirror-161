from argparse import ArgumentError
import pandas as pd
from stse import error_checking
from io import BytesIO, StringIO
from typing import Any, Union, Tuple
from rdkit.Chem import PandasTools
from collections.abc import Iterable


class Writer:
    def __init__(self, df:pd.DataFrame, mol_col_name:str='ROMol') -> None:
        """Initializes object for writing dataframes to various out formats.

        Args:
            df (pd.DataFrame): Data to write.
            mol_col_name (str, optional): Name of molecule column in dataframe. Defaults to 'ROMol'.
        """
        
        # Check input types
        error_checking.type_check('df', df, [pd.DataFrame])
        error_checking.type_check('mol_col_name', mol_col_name, [str])
        
        # Set properties
        self.df = df.copy()
        self.mol_col_name = mol_col_name
        
    def write(self, out:Union[str, BytesIO], ext:str) -> None:
        """Writes file to buffer object or path.

        Args:
            out (Union[str, BytesIO]): Buffer or path.
            ext (str): Save file extension.
        """
        self.__check_out(out, [str, BytesIO])
        self.__check_ext(ext)
        
        out = self.__get_writer(out, ext)
        
        if out:
            out.seek(0)
            return out
        
    def rdkit_2_excel(self, out:str, size:Tuple[int, int]=(200, 200)) -> None:
        """Writes file to Excel with MolFile images.

        Args:
            out (str): Save path.
            size (Tuple[int, int], optional): Size of image in pixels. Defaults to (200, 200).
        """
        error_checking.type_check('out', out, [str])
        error_checking.val_check('out', out.split('.')[-1], ['xlsx', 'xls'])  # Check extension is Excel
        
        PandasTools.SaveXlsxFromFrame(self.df, out, molCol=self.mol_col_name, size=size)
    
    @staticmethod
    def __check_out(out:Any, types:Iterable) -> None:
        """Wrapper for "out" type checking.

        Args:
            out (Any): Value to check type of.
            types (Iterable): Acceptable types.
        """
        error_checking.type_check('out', out, types)
    
    @staticmethod
    def __check_ext(ext:Any) -> None:
        """Wrapper for "ext" value checking.

        Args:
            ext (Any): Input to check value of.
        """
        error_checking.val_check('ext', ext, ['csv', 'tsv', 'xlsx', 'xls', 'sdf'])
    
    def __get_writer(self, out:Union[int, BytesIO], ext:str) -> Union[None, BytesIO]:
        """Writer factory.

        Args:
            out (Union[int, BytesIO]): Buffer or path.
            ext (str): Extension to determine factory piping.

        Raises:
            ArgumentError: Extension not recognized.
        """
        if ext == 'csv':
            out = self.__write_csv(out)
        elif ext == 'tsv':
            out = self.__write_tsv(out)
        elif ext == 'xlsx' or ext == 'xls':
            out = self.__write_excel(out)
        elif ext == 'sdf':
            out = self.__write_sdf(out)
        else:
            raise ArgumentError(f'ext = {self.ext} is not recognized')
        
        if out:
            return out
    
    def __write_csv(self, out:Union[int, BytesIO]) -> Union[None, BytesIO]:
        """Writes to CSV.

        Args:
            out (Union[int, BytesIO]): Buffer or path.

        Returns:
            Union[None, BytesIO]: Buffer if buffer.
        """
        self.df.to_csv(out, index=False)
        if isinstance(out, BytesIO):
            return out
        
    def __write_tsv(self, out:Union[int, BytesIO]) -> Union[None, BytesIO]:
        """Writes to TSV.

        Args:
            out (Union[int, BytesIO]): Buffer or path.

        Returns:
            Union[None, BytesIO]: Buffer if buffer.
        """
        self.df.to_csv(out, sep='\t', index=False)
        if isinstance(out, BytesIO):
            return out
        
    def __write_excel(self, out:Union[int, BytesIO]) -> Union[None, BytesIO]:
        """Writes to XLSX or XLS.

        Args:
            out (Union[int, BytesIO]): Buffer or path.

        Returns:
            Union[None, BytesIO]: Buffer if buffer.
        """
        with pd.ExcelWriter(out) as writer:
            self.df.to_excel(writer, index=False)
        if isinstance(out, BytesIO):
            return out
            
    def __write_sdf(self, out:Union[int, BytesIO]) -> Union[None, BytesIO]:
        """Writes to SDF.

        Args:
            out (Union[int, BytesIO]): Buffer or path.

        Returns:
            Union[None, BytesIO]: Buffer if buffer.
        """
        from naclo.dataframes import write_sdf  # Import within method to avoid circular import
        
        if isinstance(out, str):
            write_sdf(self.df, out, self.mol_col_name)
        else:
            out = StringIO()  # StringIO required by RDKit
            write_sdf(self.df, out, self.mol_col_name)
            out.seek(0)
            out = BytesIO(out.read().encode('utf8'))
            return out
