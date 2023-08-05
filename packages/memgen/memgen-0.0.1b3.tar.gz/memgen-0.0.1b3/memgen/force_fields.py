from typing import List, Optional

class ForceField:
    alias: Optional[str]
    name: str
    path: str

    def __init__(self, name: str, path: str, alias: Optional[str] = None):
        self.alias = alias
        self.name = name
        self.path = path


def get_force_fields() -> List[ForceField]:
    return [
        ForceField(
            alias='charmm',
            path='charmm36-jul2021',
            name='CHARMM36 July 2021'
        ),
        ForceField(
            path='charmm36-feb2021',
            name='CHARMM36 February 2021'
        ),
        ForceField(
            alias='slipids',
            path='Slipids_2020',
            name='Slipids 2020'
        )
    ]

def get_force_field_names() -> List[str]:
    paths = [force_field.path for force_field in get_force_fields()]
    aliases = [force_field.alias for force_field in get_force_fields() if force_field.alias is not None]

    return sorted(list(set(aliases + paths)), key=str.casefold)
