import os.path
from tempfile import TemporaryDirectory
from pathlib import Path
import pytest

from memgen import memgen
from memgen.box_shape import BoxShape
from memgen.defaults import Defaults

if Path('/workspaces').exists():
  servers = [ "http://localhost:3000", "http://memgen-dev.uni-saarland.de" ]
else:
  servers = [ Defaults.server ]

@pytest.mark.parametrize("server", servers)
def test_two_lipids(server):
  __dir__ = Path(__file__).parent
  examples_dir = str(__dir__.parent)

  with TemporaryDirectory() as temporary_dir:
    output_pdb = f"{temporary_dir}/membrane.pdb"
    output_png = f"{temporary_dir}/membrane.png"
    output_topology = f"{temporary_dir}/membrane.top"

    memgen([f"{examples_dir}/example/dmpc.pdb", f"{examples_dir}/example/dopc.pdb"], output_pdb, png=output_png, topology=output_topology,
        ratio=[1, 4], area_per_lipid=65, water_per_lipid=40, lipids_per_monolayer=128,
        server=server)

    assert(os.path.exists(output_pdb))
    assert(os.path.exists(output_png))

@pytest.mark.parametrize("server", servers)
def test_hexagon_with_salt(server):
  __dir__ = Path(__file__).parent
  examples_dir = str(__dir__.parent)
  
  with TemporaryDirectory() as temporary_dir:
    output_pdb = f"{temporary_dir}/membrane.pdb"
    output_png = f"{temporary_dir}/membrane.png"

    memgen([f"{examples_dir}/example/popc.pdb"], output_pdb, png=output_png,
        area_per_lipid=85, lipids_per_monolayer=32,
        added_salt=1000, box_shape=BoxShape.hexagonal,
        server=server)

    assert(os.path.exists(output_pdb))
    assert(os.path.exists(output_png))
