from curses import raw
import json
from typing import List, Optional, Tuple
from pathlib import Path


class Structure:
    id: str
    description: str
    invalid: bool

    def __init__(self, id: str, description: str, invalid: bool):
        self.id = id
        self.description = description
        self.invalid = invalid


class StructuresGroup:
    name: Optional[str]
    lipids: List[Tuple[str, str]]

    def __init__(self, lipids: List[Tuple[str, str]], name: str = None):
        self.name = name
        self.lipids = lipids


class StructureSource:
    alias: Optional[str]
    name: str
    path: str
    suffix: str
    groups: List[StructuresGroup]
    reference: str

    def __init__(self, name: str, groups: List[StructuresGroup], path: str, suffix: str, reference: str, alias: Optional[str] = None):
        self.alias = alias
        self.name = name
        self.path = path
        self.suffix = suffix
        self.groups = groups
        self.reference = reference


def load_source(source: dict) -> StructureSource:
    groups = []

    for raw_group in source["groups"]:
        lipids = []

        for lipid in raw_group["structures"]:
            lipids.append(Structure(
                id=lipid["id"],
                description=lipid["description"],
                invalid=lipid["invalid"] if "invalid" in lipid else False
            ))

        group = StructuresGroup(
            name=raw_group["name"] if "name" in raw_group else None,
            lipids=lipids
        )

        groups.append(group)

    return StructureSource(
        alias=source["alias"],
        name=source["name"],
        path=source["path"],
        suffix=source["suffix"],
        reference=source["reference"],
        groups=groups
    )


def get_raw_local_sources() -> List[dict]:
    charmm_path = Path(Path(__file__).parent.parent.parent, "data", "lipids", "charmm.json")
    slipids_path = Path(Path(__file__).parent.parent.parent, "data", "lipids", "slipids.json")

    paths = [charmm_path, slipids_path]

    raw_sources = []

    for path in paths:
        with open(path, "r") as fp:
            raw_source = json.load(fp)
            raw_sources.append(raw_source)

    return raw_sources
