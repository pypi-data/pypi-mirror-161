import argparse
import http.client
import json
from pathlib import Path
from textwrap import indent
from typing import List, Optional

from memgen.box_shape import BoxShape
from memgen.defaults import Defaults
from memgen.file_types import is_structure
from memgen.force_fields import get_force_field_names, get_force_fields
from memgen.structure_sources import get_raw_local_sources, load_source


def get_raw_sources(args):
    if args.run_locally:
        return get_raw_local_sources()
    else:
        server = args.server

        if server.startswith("https://"):
            connection = http.client.HTTPSConnection(server[len("https://"):])
        else:
            connection = http.client.HTTPConnection(server)

        try:
            connection.request('GET', '/api/structures')

            res = connection.getresponse()
        except http.client.RemoteDisconnected as disconnected:
            print()
            print(f"{disconnected}.")
            exit(1)

        try:
            structures = json.loads(res.read().decode())
        except json.decoder.JSONDecodeError as parse_error:
            print()
            print("Server didn't respond with a valid message. Try again in a few minutes.")
            print()
            print("If the issue persists report an issue at https://gitlab.com/cbjh/memgen/py-memgen/-/issues")
            print()
            exit(1)

        return structures["sources"]

def list_structures_action(script_name: str, argv):
    class ListStructures(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            raw_sources = get_raw_sources(args)

            if args.give_json:
                print(json.dumps({"sources": raw_sources}))
                parser.exit()

            sources = [load_source(raw_source) for raw_source in raw_sources]

            for source in sources:
                for group in source.groups:
                    if group.name is None:
                        print(f"{source.name}")
                    else:
                        print(f"{source.name} / {group.name}")

                    print()

                    column_layout = "{:>30}    {}"

                    print(column_layout.format("structure", "path"))
                    print(column_layout.format("---", "---"))

                    for lipid in group.lipids:
                        path = f"db://{source.path}/{lipid.id}{source.suffix}"
                        path_str = f"{path}" if not lipid.invalid else f"{path} (file missing)"

                        print(column_layout.format(lipid.description, path_str))

                    print()

                print()

            print(f"usage example:")
            print(f"  {script_name} db://slipids/cholesterol.{{pdb,itp}} membrane.pdb")
            print()

            print(f"search example:")
            print(f"  {script_name} --list-structures | grep -i POPC")
            print()

            print("sources:")

            for source in sources:
                print(f"  {source.path}: {source.reference}")

            print()

            parser.exit()

    return ListStructures


def list_force_fields_action(argv):
    class ListForceFields(argparse.Action):
        def __call__(self, _parser, args, _values, _option_string=None):
            print("Available Force-fields")
            print()

            column_layout = "{:>20}    {:<10}    {:<22}    {}"

            print(column_layout.format("name", "alias", "description", "ref"))
            print(column_layout.format("---", "---", "---", "---"))

            for force_field in get_force_fields():
                if force_field.alias is not None:
                    print(column_layout.format(force_field.path, force_field.alias, force_field.name, f"db://{force_field.path}"))
                else:
                    print(column_layout.format(force_field.path, "", force_field.name, f"db://{force_field.path}"))

            print()

            print("example:")
            print("  memgen ./DOPC.pdb membrane.pdb --force-field db://charmm")
            print()

            exit(0)

    return ListForceFields

def is_db_path(path: str):
    return path.startswith("db://")

def deduce_force_field(input_files: List[str]) -> Optional[str]:
    for input_file in input_files:
        if not is_db_path(input_file):
            return None

    force_fields = list(set([input_file[5:].split("/")[0] for input_file in input_files if len(input_file) > 5]))

    if len(force_fields) > 1:
        return None

    return f"db://{list(force_fields)[0]}"

def resolve_force_field_name(force_field_spec: str) -> str:
    if not is_db_path(force_field_spec):
        return force_field_spec

    force_field_name = force_field_spec[5:]

    for force_field in get_force_fields():
        if force_field.alias is not None and force_field.alias == force_field_name:
            return f"db://{force_field.path}"
        
        if force_field.path == force_field_name:
            return f"db://{force_field.path}"

    return force_field_spec


def deduce_topology_headers(force_field_spec: str) -> List[str]:
    force_field = resolve_force_field_name(force_field_spec)

    if not is_db_path(force_field):
        return []

    force_field_name = force_field[5:]

    force_field_path = Path(Path(__file__).parent.parent.parent, "data", "force-fields", f"{force_field_name}.ff")

    if force_field in ["db://Slipids_2020", "db://charmm36-jul2021", "db://charmm36-feb2021"]:
        return [str(Path(force_field_path, "forcefield.itp"))]

    return []

def parse_cli(argv):
    script_name = Path(argv[0]).name

    parser = argparse.ArgumentParser(script_name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("input_pdbs", nargs="+", help="PDB or CRD and optionally .itp files.")
    parser.add_argument("output_pdb", help="Generated membrane.")

    parser.add_argument("-c", "--ratio", nargs="*", type=int,
            help=""" Lipid concentration ratio. For example: 1 4 (same as 20 80).
                     It means 20%% of the first lipid and 80%% of the second. """)

    parser.add_argument("-a", "--area-per-lipid", type=int, default=Defaults.area_per_lipid, help="Area per lipid (Å²)")
    parser.add_argument("-w", "--water-per-lipid", type=int, default=Defaults.water_per_lipid, help="Water molecules per lipid")
    parser.add_argument("-n", "--lipids-per-monolayer", type=int, default=Defaults.lipids_per_monolayer, help="Lipids per monolayer")
    parser.add_argument("-s", "--added-salt", type=int, default=Defaults.added_salt, help="Added salt (milli molar)")
    parser.add_argument("-b", "--box-shape", type=BoxShape, choices=list(BoxShape), default=BoxShape.square, help="Box shape")

    parser.add_argument("--png", help="A small thumbnail depicting generated membrane.")
    parser.add_argument("--topology", help="Generated GROMACS topology file.")

    parser.add_argument("--run-locally", action="store_true")
    parser.add_argument("--give-json", action="store_true")

    parser.add_argument("-l", "--list-structures", action=list_structures_action(script_name, argv), nargs=0, help="List lipid structures offered by the server")
    parser.add_argument("--list-force-fields", action=list_force_fields_action(argv), nargs=0, help="List force-fields offered by the server")

    parser.add_argument("-f", "--force-field", type=str, required=False)
    parser.add_argument("--topology-headers", nargs="+")

    maintenance = parser.add_argument_group("Maintenance")
    maintenance.add_argument("--server", default=Defaults.server, help="Hostname of MemGen REST API server.")

    args = parser.parse_args(argv[1:])

    if args.force_field is None and args.topology_headers is None:
        deduced_force_field = deduce_force_field(args.input_pdbs)
        args.force_field = deduced_force_field

        if deduced_force_field is not None:
            deduced_topology_headers = deduce_topology_headers(deduced_force_field)

            if deduced_topology_headers is not None:
                args.topology_headers = deduced_topology_headers

    if args.force_field is not None and is_db_path(args.force_field) and args.topology_headers is None:
        deduced_topology_headers = deduce_topology_headers(args.force_field)

        if deduced_topology_headers is not None:
            args.topology_headers = deduced_topology_headers

    # Setting equal ratio of lipids if ratio not specified. For two lipids 1:1, for three 1:1:1 (33%/33%/33%) and so on.
    if args.ratio is None and len(args.input_pdbs) > 1:
        input_structures = [input_file for input_file in args.input_pdbs if is_structure(input_file)]

        args.ratio = [1] * len(input_structures)

    return args
