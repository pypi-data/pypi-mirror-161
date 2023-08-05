from pathlib import Path


def is_structure(path: str):
    return Path(path).suffix in ['.pdb', '.crd']

def is_params(path: str):
    return Path(path).suffix in ['.itp']
