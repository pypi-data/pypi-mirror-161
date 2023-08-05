import subprocess
from typing import List, Optional
from pathlib import Path

from memgen.defaults import Defaults
from memgen.file_types import is_structure, is_params
from memgen.parse_cli import BoxShape


def pair_input_files(input_files: List[str]):
    structure, params = None, None

    for input_file in input_files:
        if is_structure(input_file):
            if (structure, params) != (None, None):
                yield structure, params

            # Start new pair
            structure = input_file
            params = None 
        elif is_params(input_file):
            if structure is None:
                print(f"error: {input_file} is a parameters file, specify a structure file before it")
                exit(1)
            else:
                params = input_file
        else:
            print(f"error: {input_file} is not recognized as structure or params")
            exit(1)

    yield structure, params


def is_db_path(path: str):
    return path.startswith("db://")

def resolve_structure_db_path(db_path: str):
    return Path(Path(__file__).parent.parent.parent, "data", "lipids", db_path[5:])

def local_memgen(
    input_pdbs: List[str],
    output_pdb: str,
    ratio: Optional[List[int]] = None,
    area_per_lipid: int = Defaults.area_per_lipid,
    water_per_lipid: int = Defaults.water_per_lipid,
    lipids_per_monolayer: int = Defaults.lipids_per_monolayer,
    added_salt: int = Defaults.added_salt,
    box_shape: BoxShape = Defaults.box_shape,
    png: Optional[str] = None,
    topology: Optional[str] = None,
    server: str = Defaults.server,
    topology_headers: List[str] = [],
    force_field: Optional[str] = None
):
    structures: str = []
    params: str = []

    for pdb, itp in pair_input_files(input_pdbs):
        resolved_pdb = resolve_structure_db_path(pdb) if is_db_path(pdb) else pdb
        resolved_itp = resolve_structure_db_path(itp) if itp is not None and is_db_path(itp) else itp

        if not Path(resolved_pdb).exists:
            if is_db_path(pdb):
                print(f"{pdb} doesn't exist in the database")
            else:
                print(f"{pdb} doesn't exist")

            exit(1)

        structures.append(str(resolved_pdb))

        if itp is not None:
            if not Path(resolved_itp).exists:
                if is_db_path(itp):
                    print(f"{itp} doesn't exist in the database")
                else:
                    print(f"{itp} doesn't exist")

                exit(1)

            params.append(str(resolved_itp))

    # TODO: This is unnecessary limitation

    if len(params) > 0 and len(params) != len(structures):
        print("error: You need to provide all .itp files or none")

    memgen_location = Path(Path(__file__).parent.parent.parent, "memgen.sh")

    command = \
        f"{memgen_location}" \
        f" -pdb '{' '.join(structures)}'" \
        f" -apl {round(area_per_lipid / 100, 2)} -wpl {water_per_lipid} -n {lipids_per_monolayer}" \

    if len(params) > 0:
        command += f" -itp '{' '.join(params)}'"

    if ratio is not None:
        command += f" -frac '{' '.join(map(str, ratio))}'"

    if topology_headers is not None:
        command += f" -top_headers '{' '.join(topology_headers)}'" \

    print(f"Running {command}")

    subprocess.run(command, shell=True)
