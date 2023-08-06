from naclo.rdpickle import serialize_mol
from stse.database import df_2_db


def rdkit_2_db(df, collection, mol_col='ROMol'):
    # Convert to BSON for back-end storage
    df2 = df.copy()
    df2[mol_col] = df2[mol_col].apply(serialize_mol)
    df_2_db(df2, collection)
