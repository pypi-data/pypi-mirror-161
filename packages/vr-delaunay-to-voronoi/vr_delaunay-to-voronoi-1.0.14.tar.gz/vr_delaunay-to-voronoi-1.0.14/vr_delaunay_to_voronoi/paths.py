from pathlib import Path

from vr_delaunay_to_voronoi.shims.path_ensuring import ensure_path

ROOT_PATH: Path = Path(__file__).parent.parent

ROOT_DATA_TEST_PLOTTING_PATH: Path = ROOT_PATH / 'data' / 'test' / 'plotting'

ensure_path(path=ROOT_DATA_TEST_PLOTTING_PATH)
