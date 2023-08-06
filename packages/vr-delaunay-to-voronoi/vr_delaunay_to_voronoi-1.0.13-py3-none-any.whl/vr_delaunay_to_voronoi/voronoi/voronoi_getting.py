"""
An adaptation of https://stackoverflow.com/a/15783581/60982
Using ideas from https://stackoverflow.com/a/9471601/60982
"""

from typing import Any, DefaultDict, Dict, List, Tuple

import numpy as np
from scipy.spatial import Delaunay

from vr_delaunay_to_voronoi.voronoi.cell_to_edges_for_voronoi_cell_getting \
    import get_cell_to_edges_for_voronoi_cell
from vr_delaunay_to_voronoi.voronoi.\
    circumscribed_circle_for_triangle_points_getting import \
    get_circumscribed_circle_for_triangle_points
from vr_delaunay_to_voronoi.voronoi.\
    long_line_endpoints_and_line_indices_getting import \
    get_long_line_endpoints_and_line_indices
from vr_delaunay_to_voronoi.voronoi.outer_cell_closing import close_outer_cells
from vr_delaunay_to_voronoi.voronoi.\
    polygon_index_to_polygon_for_cells_getting import \
    get_polygon_index_to_polygon_for_cells


def get_voronoi_polygons(
    *,
    delaunay,
) -> List[Any]:
    """
    Get a voronoi polygon for each point in the input delaunay triangulation.

    :rtype: list of n polygons where each polygon is an array of vertices
    """
    points: List[int] = delaunay.points
    line_indices: List[Tuple[int, int]]
    vertices, line_indices = _get_voronoi(delaunay=delaunay)

    voronoi_polygon_list = \
        _get_voronoi_polygons_for_points_vertices_and_line_indices(
            points=points,
            line_indices=line_indices,
            vertices=vertices,
        )

    return voronoi_polygon_list


def _get_voronoi(*, delaunay: Delaunay) -> Tuple:
    """
    Return a list of all edges of the voronoi diagram for given input points.
    """
    triangles = delaunay.points[delaunay.vertices]

    circum_centers = np.array(
        [
            get_circumscribed_circle_for_triangle_points(points=triangle)
            for triangle in triangles
        ]
    )

    long_lines_endpoints, line_indices = \
        get_long_line_endpoints_and_line_indices(
            circum_centers=circum_centers,
            delaunay=delaunay,
            triangles=triangles,
        )

    vertices = np.vstack(
        (circum_centers, long_lines_endpoints)
    )

    # Make lines (1,2) and (2,1) both (1,2)
    line_indices_sorted = np.sort(line_indices)
    # Filter out any duplicate lines
    line_indices_tuples = [tuple(row) for row in line_indices_sorted]
    line_indices_unique = set(line_indices_tuples)
    line_indices_unique_sorted = sorted(line_indices_unique)

    return vertices, line_indices_unique_sorted


def _get_voronoi_polygons_for_points_vertices_and_line_indices(
    *,
    points,
    vertices,
    line_indices: List[Tuple[int, int]],
):
    cells: DefaultDict[Any, List[Tuple]] = get_cell_to_edges_for_voronoi_cell(
        points=points,
        vertices=vertices,
        line_indices=line_indices,
    )
    cells = close_outer_cells(cells=cells)
    polygon_index_to_polygon_as_vertex_indices: Dict[int, List[int]] = \
        get_polygon_index_to_polygon_for_cells(cells=cells)

    voronoi_polygons_list: List[Any] = [
        vertices[
            polygon_index_to_polygon_as_vertex_indices[point_index]
        ]
        for point_index in range(len(points))
    ]

    return voronoi_polygons_list
