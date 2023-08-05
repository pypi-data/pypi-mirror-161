import sys

from memgen.parse_cli import parse_cli
from memgen.memgen import memgen
from memgen.local_memgen import local_memgen

def main():
  args = parse_cli(sys.argv)

  if args.run_locally:
    local_memgen(args.input_pdbs, args.output_pdb, png=args.png,
        topology=args.topology,
        ratio=args.ratio,
        area_per_lipid=args.area_per_lipid,
        water_per_lipid=args.water_per_lipid,
        lipids_per_monolayer=args.lipids_per_monolayer,
        added_salt=args.added_salt,
        box_shape=args.box_shape,
        server=args.server,
        topology_headers=args.topology_headers,
        force_field=args.force_field
    )
  else:
    memgen(args.input_pdbs, args.output_pdb, png=args.png,
        topology=args.topology,
        ratio=args.ratio,
        area_per_lipid=args.area_per_lipid,
        water_per_lipid=args.water_per_lipid,
        lipids_per_monolayer=args.lipids_per_monolayer,
        added_salt=args.added_salt,
        box_shape=args.box_shape,
        server=args.server,
        topology_headers=args.topology_headers,
        force_field=args.force_field
    )

from memgen.box_shape import BoxShape
