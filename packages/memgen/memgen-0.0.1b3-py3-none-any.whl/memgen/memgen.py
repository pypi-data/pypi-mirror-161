import base64
import http.client
import json
from pathlib import Path
import sys
from typing import List, Optional

from memgen.parse_cli import BoxShape
from memgen.defaults import Defaults


def jupyter_display(png):
  if png is None:
    return None

  try:
    from IPython.display import Image

    return Image(filename=png)
  except ImportError as e:
    pass


def display_molecule(input_pdb: str):
  try:
    from openbabel import openbabel

    conversion = openbabel.OBConversion()
    conversion.SetOutFormat("ascii")

    molecule = openbabel.OBMol()
    conversion.ReadFile(molecule, input_pdb)

    asciiArt = conversion.WriteString(molecule)

    lines = asciiArt.splitlines()

    print()
    print("\n".join([line for line in lines if line.strip() != ""]))
    print()
  except Exception:
    pass


def memgen(
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
  if lipids_per_monolayer > 256:
    print(''' error: Maximum of 256 lipids per monolayer are supported. 
        If you want to build a larger membrane, use the GROMACS "genconf" module, 
        e.g. with "gmx genconf -nbox 2 2 1 -f in.pdb -o out.pdb". ''', file=sys.stderr)
    sys.exit(1)

  quoted_paths = '"' + '", "'.join(input_pdbs) + '"'

  for input_pdb in input_pdbs:
    if input_pdb[0:5] != "db://" and Path(input_pdb).suffix == ".pdb":
      display_molecule(input_pdb)

  print(f'Submitting {quoted_paths} to "{server}". Please wait...')

  encoded_input_pdbs_content = []

  for input_pdb in input_pdbs:
    if input_pdb[0:5] != "db://":
      with open(input_pdb, 'rb') as fp:
        encoded_input_pdbs_content.append(str(base64.b64encode(fp.read()), 'ascii'))
    else:
      encoded_input_pdbs_content.append(input_pdb)

  if server.startswith("https://"):
    connection = http.client.HTTPSConnection(server[len("https://"):])
  elif server.startswith("http://"):
    connection = http.client.HTTPConnection(server[len("http://"):])
  else:
    connection = http.client.HTTPConnection(server)

  try:
    body = {
      'pdbs': encoded_input_pdbs_content,
      'areaPerLipid': area_per_lipid,
      'waterPerLipid': water_per_lipid,
      'lipidsPerMonolayer': lipids_per_monolayer,
      'addedSalt': added_salt,
      'boxShape': str(box_shape),
      'forceField': force_field
    }

    if ratio is not None:
      body['ratio'] = ratio

    connection.request('POST', '/api/submit', json.dumps(body), {'Content-type': 'application/json'})

    res = connection.getresponse()
  except http.client.RemoteDisconnected as disconnected:
    print()
    print(f"{disconnected}.")
    exit(1)

  try:
    res_body = json.loads(res.read().decode())
  except json.decoder.JSONDecodeError as parse_error:
    print()
    print("Server didn't respond with a valid message. Try again in a few minutes.")
    print()
    print("If the issue persists report an issue at https://gitlab.com/cbjh/memgen/py-memgen/-/issues")
    print()
    exit(1)

  if res.status == 200:
    with open(output_pdb, 'wb') as pdb_fp:
      pdb_fp.write(base64.b64decode(res_body['pdb']))

    if png:
      with open(png, 'wb') as png_fp:
        png_fp.write(base64.b64decode(res_body['png']))

    if topology:
      with open(topology, 'wb') as topology_fp:
        topology_fp.write(base64.b64decode(res_body['topology']))

    if png:
      print(f'Output saved as "{output_pdb}" and "{png}".')
    else:
      print(f'Output saved as "{output_pdb}".')

    return jupyter_display(png)
  else:
    print(f"Server response: {res_body['error']}")
    print(f'Saving error output as "{output_pdb}.out.log" and "{output_pdb}.out.log".')

    with open(f'{output_pdb}.out.log', 'w') as std_out_fp:
      std_out_fp.write(res_body['stdOut'])

    with open(f'{output_pdb}.err.log', 'w') as std_err_fp:
      std_err_fp.write(res_body['stdErr'])

    sys.exit(1)
