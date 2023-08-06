from rdkit import Chem
from rdkit.Chem.Descriptors import ExactMolWt
from rdkit.Chem.SaltRemover import SaltRemover
import numpy as np

from naclo import mol_stats
from naclo.__asset_loader import recognized_salts


def mw(smile):  # *
    """Removes smaller fragments from a SMILES string by molecular weight.

    Args:
        smile (str): Mol SMILES representation.

    Returns:
        str: SMILES with fragments removed.
    """
    fragments = smile.split('.')

    # Calculate molecular weights of each fragment
    mws = [ExactMolWt(Chem.MolFromSmiles(frag)) for frag in fragments]

    # Locate the max molecular weight
    max_mw = max(mws)
    max_index = mws.index(max_mw)

    return fragments[max_index]

def atom_count(smile):  # *
    """Removes smaller fragments from a SMILES string by atom count.

    Args:
        smile (str): Mol SMILES representation.

    Returns:
        str: SMILES with fragments removed.
    """
    fragments = smile.split('.')

    # Calculate atom counts of each fragment
    atom_counts = [Chem.MolFromSmiles(frag).GetNumAtoms() for frag in fragments]

    # Locate the max atom count
    max_atom_count = max(atom_counts)
    max_index = atom_counts.index(max_atom_count)

    return fragments[max_index]

def carbon_count(smile:str) -> str:  # *
    """Removes smaller fragments from a SMILES string by carbon count.

    Args:
        smile (str): Mol SMILES representation.

    Returns:
        str: SMILES with fragments removed.
    """
    fragments = smile.split('.')
    
    # Calculate carbon counts of each fragment
    carbon_counts = [mol_stats.carbon_num(frag) for frag in fragments]
    
    # Locate the max carbon count
    max_carbon_count = max(carbon_counts)
    max_index = carbon_counts.index(max_carbon_count)
    
    return fragments[max_index]

def remove_recognized_salts(smile:str) -> str:
    """Removes smiles fragments that are found in assets/recognized_salts.json. Salts sourced from:
    https://github.com/chembl/ChEMBL_Structure_Pipeline/blob/master/chembl_structure_pipeline/data/salts.smi

    Args:
        smile (str): Molecule SMILES structure.

    Returns:
        str: SMILES with salts removed. Could be empty string if all fragments are recognized salts.
    """
    fragments = smile.split('.')
    fragments = [f for f in fragments if f not in recognized_salts['smiles']]
    return '.'.join(fragments)

def remove_salts(mols, salts='[Cl,Br]'):  # *
    """Removes salts from iterable.

    Args:
        mols (iterable): Contains RDKit Mol objects.

    Returns:
        list: Contains RDKit Mol objects with salts removed.
    """
    remover = SaltRemover(defnData=salts)
    return [remover.StripMol(mol) for mol in mols]
