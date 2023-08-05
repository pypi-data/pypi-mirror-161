from memgen.parse_cli import BoxShape


class Defaults:
  area_per_lipid: int = 65
  water_per_lipid: int = 35
  lipids_per_monolayer: int = 64
  added_salt: int = 0
  box_shape: BoxShape = BoxShape.square

  server = "https://memgen.uni-saarland.de"
