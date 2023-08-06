from typing import Any, DefaultDict, Dict, List, Tuple

from vr_delaunay_to_voronoi.voronoi.ordered_edges_by_edge_indices_getting \
    import get_ordered_edges_by_edge_indices


def get_polygon_index_to_polygon_for_cells(
    *,
    cells: DefaultDict[Any, List[Tuple]],
) -> Dict[int, List[int]]:
    """
    Create polygons by storing vertex indices of a cell in order.

    The order can either be clockwise or counter-clockwise.
    """
    polygons_as_vertex_indices: Dict[int, List[int]] = {}
    for polygon_index, edge_indices in cells.items():
        ordered_edges = \
            get_ordered_edges_by_edge_indices(edge_indices=edge_indices)
        polygons_as_vertex_indices[polygon_index] = [
            edge_start for (edge_start, edge_end) in ordered_edges
        ]

    return polygons_as_vertex_indices
