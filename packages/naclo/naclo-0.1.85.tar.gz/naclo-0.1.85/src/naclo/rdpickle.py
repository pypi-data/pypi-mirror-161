import pickle


def deserialize_mol(pickled_mol):
    return pickle.loads(pickled_mol)

def serialize_mol(mol):
    return pickle.dumps(mol)
