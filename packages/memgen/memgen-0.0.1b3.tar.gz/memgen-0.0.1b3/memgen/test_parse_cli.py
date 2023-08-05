from memgen.parse_cli import deduce_force_field, deduce_topology_headers, parse_cli, BoxShape, resolve_force_field_name


def test_minimal_example():
    """ Minimal example. Single lipid, with default settings. """

    cmd = 'memgen example/dmpc.pdb membrane.pdb'

    assert vars(parse_cli(cmd.split())) == {
      'input_pdbs': ['example/dmpc.pdb'],
      'output_pdb': 'membrane.pdb',
      'ratio': None,
      'area_per_lipid': 65,
      'water_per_lipid': 35,
      'lipids_per_monolayer': 64,
      'added_salt': 0,
      'box_shape': BoxShape.square,
      'png': None,
      'topology': None,
      'server': 'https://memgen.uni-saarland.de',

      'topology_headers': None,
      'force_field': None,
      'list_force_fields': None,
      'list_structures': None,
      'give_json': False,
      'run_locally': False
    }


def test_kitchen_sink_example():
    """ Two lipids and all possible options set. """

    cmd = """ memgen 
              example/dmpc.pdb example/dopc.pdb membrane.pdb --ratio 1 4
              --area-per-lipid 55 --water-per-lipid 30 --lipids-per-monolayer 75 --added-salt 5
              --box-shape hexagonal
              --png membrane.png
              --topology membrane.top
              --server localhost:3000 """

    assert vars(parse_cli(cmd.split())) == {
      'input_pdbs': ['example/dmpc.pdb', 'example/dopc.pdb'],
      'output_pdb': 'membrane.pdb',
      'ratio': [1, 4],
      'area_per_lipid': 55,
      'water_per_lipid': 30,
      'lipids_per_monolayer': 75,
      'added_salt': 5,
      'box_shape': BoxShape.hexagonal,
      'png': 'membrane.png',
      'topology': 'membrane.top',
      'server': 'localhost:3000',

      'topology_headers': None,
      'force_field': None,
      'list_force_fields': None,
      'list_structures': None,
      'give_json': False,
      'run_locally': False
    }

def test_deduce_force_field():
    assert deduce_force_field(["db://slipids/cholesterol.pdb", "db://slipids/cholesterol.itp"]) == "db://slipids"
    assert deduce_force_field(["db://charmm/bddtm.crd"]) == "db://charmm"
    assert deduce_force_field(["./cholesterol.pdb"]) == None
    assert deduce_force_field(["db://slipids/cholesterol.pdb", "db://charmm/bddtm.crd"]) == None
    assert deduce_force_field(["db://charmm/bddtm.crd", "./cholesterol.pdb"]) == None

def test_resolve_force_field_name():
    assert resolve_force_field_name("db://slipids") == "db://Slipids_2020"
    assert resolve_force_field_name("db://Slipids_2020") == "db://Slipids_2020"
    assert resolve_force_field_name("db://charmm") == "db://charmm36-jul2021"
    assert resolve_force_field_name("db://charmm36-jul2021") == "db://charmm36-jul2021"
    assert resolve_force_field_name("db://charmm36-feb2021") == "db://charmm36-feb2021"

def test_deduce_topology_headers():
    assert deduce_topology_headers("db://slipids")[0].endswith("/Slipids_2020.ff/forcefield.itp")
