import collections
from typing import Any, DefaultDict, List, Tuple

from scipy.spatial import KDTree


def get_cell_to_edges_for_voronoi_cell(
    *,
    points,
    vertices,
    line_indices,
) -> DefaultDict[Any, List[Tuple]]:
    """
    Return a mapping from a voronoi cell to its edges.

    :param points: shape (m,2)
    :param vertices: shape (n,2)
    :param line_indices: shape (o,2)
    :rtype: dict point index -> list of shape (n,2) with vertex indices
    """
    kd_tree: KDTree = KDTree(points)

    cells: DefaultDict[Any, List[Tuple]] = collections.defaultdict(list)
    for line_index_0, line_index_1 in line_indices:
        vertex_0, vertex_1 = vertices[line_index_0], vertices[line_index_1]
        middle = (vertex_0 + vertex_1) / 2
        _, (point_0_index, point_1_index) = kd_tree.query(middle, 2)
        cells[point_0_index].append((line_index_0, line_index_1))
        cells[point_1_index].append((line_index_0, line_index_1))

    return cells
