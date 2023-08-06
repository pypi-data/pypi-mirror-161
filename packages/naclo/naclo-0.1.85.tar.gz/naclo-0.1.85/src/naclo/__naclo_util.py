import warnings

import stse


def drop_na_structures(self) -> None:
        """Drops NA along declared structure column."""
        self.df.dropna(subset=[self.structure_col], inplace=True)
        if not len(self.df):
            warnings.warn('ALL_NA_STRUCTURES: All structures in specified column were NA, all rows dropped',
                          RuntimeWarning)

def drop_na_targets(self) -> None:
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
        
def recognized_options_checker(input_options, recognized_options) -> None:  # *
    input = stse.dictionaries.branches(input_options)
    recognized = stse.dictionaries.branches(recognized_options)

    errors = {}
    for key, value in recognized.items():
        if isinstance(value, list):
            if not input[key] in recognized[key]:
                errors[f'BAD_OPTION{key.upper()}'] = f'"{input[key]}" is not an accepted value for "{key}", set \
                    to one of: "{recognized[key]}"'
        else:
            if not type(input[key]) == type(recognized[key]):
                errors[f'BAD_OPTION{key.upper()}'] = f'{type(input[key])} is not an accepted type for {key}, \
                    input a {type(recognized[key])}'
    if errors:
        raise ValueError(errors)
    
def check_columns_in_df(df, columns) -> None:
    """Checks that all columns in columns are in df"""
    for column in columns:
        if column not in df.columns:
            raise ValueError(f'Column: "{column}" is not found in data.')
