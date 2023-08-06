"""
An adaptation of https://stackoverflow.com/a/15783581/60982
Using ideas from https://stackoverflow.com/a/9471601/60982
"""

import collections
from typing import List, Dict, Tuple, Any, Union, DefaultDict

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.spatial import Delaunay, KDTree

from vr_delaunay_to_voronoi.delaunay.delaunay_tesselation_getting import \
    get_delaunay_tesselation
from vr_delaunay_to_voronoi.library_seeding import \
    seed_standard_library_and_numpy
from vr_delaunay_to_voronoi.plotting import plot
from vr_delaunay_to_voronoi.points_getting import get_points
from vr_delaunay_to_voronoi.polygon_patch_getting import get_polygons


def voronoi(*, delaunay: Delaunay) -> Tuple:
    """
    Return a list of all edges of the voronoi diagram for given input points.
    """
    triangles = delaunay.points[delaunay.vertices]

    circum_centers = np.array(
        [
            triangle_circumscribed_circle(points=triangle)
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


def get_long_line_endpoints_and_line_indices(
    *,
    circum_centers,
    delaunay,
    triangles,
):
    long_lines_endpoints = []
    line_indices = []
    for triangle_index, triangle in enumerate(triangles):
        circum_center = circum_centers[triangle_index]
        triangle_neighbors = delaunay.neighbors[triangle_index]
        for neighbor_index, neighbor in enumerate(triangle_neighbors):
            if neighbor != -1:
                line_indices.append(
                    (triangle_index, neighbor)
                )
                continue

            ps = \
                triangle[(neighbor_index + 1) % 3] - \
                triangle[(neighbor_index - 1) % 3]
            ps = np.array((ps[1], -ps[0]))

            middle = (
                triangle[(neighbor_index + 1) % 3] +
                triangle[(neighbor_index - 1) % 3]
            ) * 0.5
            di = middle - triangle[neighbor_index]

            ps /= np.linalg.norm(ps)
            di /= np.linalg.norm(di)

            if np.dot(di, ps) < 0.0:
                ps *= -1000.0
            else:
                ps *= 1000.0

            long_lines_endpoints.append(circum_center + ps)
            line_indices.append(
                (
                    triangle_index,
                    len(circum_centers) + len(long_lines_endpoints) - 1
                )
            )

    return long_lines_endpoints, line_indices


def triangle_circumscribed_circle(*, points):
    rows, columns = points.shape

    A_built_matrix = np.bmat(
        [
            [
                2 * np.dot(points, points.T),
                np.ones((rows, 1))
            ],
            [
                np.ones((1, rows)),
                np.zeros((1, 1))
            ]
        ]
    )

    b = np.hstack(
        (np.sum(points * points, axis=1), np.ones(1))
    )
    x = np.linalg.solve(A_built_matrix, b)
    barycentric_coordinates = x[:-1]

    circum_center = np.sum(
        points * np.tile(
            barycentric_coordinates.reshape(
                (points.shape[0], 1)
            ),
            (
                1,
                points.shape[1]
            )
        ),
        axis=0,
    )

    return circum_center


def voronoi_cell_lines(
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


def create_polygons_from_cells(
    *,
    cells: DefaultDict[Any, List[Tuple]],
) -> Dict[int, List[int]]:
    """
    Create polygons by storing vertex indices of a cell in order.

    The order can either be clockwise or counter-clockwise.
    """
    polygons: Dict[int, List[int]] = {}
    for polygon_index, edge_indices in cells.items():
        ordered_edges = \
            get_ordered_edges_by_edge_indices(edge_indices=edge_indices)
        polygons[polygon_index] = [
            edge_start for (edge_start, edge_end) in ordered_edges
        ]

    return polygons


def get_ordered_edges_by_edge_indices(*, edge_indices):
    # Create a directed graph which contains both directions
    edge_indices_reversed = [
        (edge_end, edge_start) for
        (edge_start, edge_end) in
        edge_indices
    ]
    directed_edges = \
        edge_indices + \
        edge_indices_reversed

    # Map each edge start vertices to all its edges' end vertices
    edge_start_to_ends = collections.defaultdict(list)
    for (edge_start, edge_end) in directed_edges:
        edge_start_to_ends[edge_start].append(edge_end)

    # Start at the first edge and follow that direction around the graph
    ordered_edges = []
    current_edge = directed_edges[0]
    while len(ordered_edges) < len(edge_indices):
        edge_start = current_edge[1]
        edge_end = \
            edge_start_to_ends[edge_start][0] \
            if edge_start_to_ends[edge_start][0] != current_edge[0] \
            else edge_start_to_ends[edge_start][1]

        next_edge = (edge_start, edge_end)
        ordered_edges.append(next_edge)
        current_edge = next_edge

    return ordered_edges


def close_outer_cells(
    *,
    cells: DefaultDict[Any, List[Tuple]],
) -> DefaultDict[Any, List[Tuple]]:
    """
    Close the outer cells.
    """
    for polygon_index, line_indices in cells.items():
        dangling_lines = []
        for line_index_0, line_index_1 in line_indices:
            connections = list(
                filter(
                    lambda i12_:
                    (line_index_0, line_index_1) != (i12_[0], i12_[1])
                    and
                    (
                            line_index_0 == i12_[0] or
                            line_index_0 == i12_[1] or
                            line_index_1 == i12_[0] or
                            line_index_1 == i12_[1]
                    ),
                    line_indices
                )
            )
            assert 1 <= len(connections) <= 2
            if len(connections) == 1:
                dangling_lines.append((line_index_0, line_index_1))
        assert len(dangling_lines) in {0, 2}
        if len(dangling_lines) == 2:
            (i11, i12), (i21, i22) = dangling_lines

            # determine which line ends are unconnected
            connected = list(
                filter(
                    lambda i12_:
                        (i12_[0], i12_[1]) != (i11, i12) and
                        (i12_[0] == i11 or i12_[1] == i11),
                    line_indices
                )
            )
            i11_unconnected = not connected

            connected = list(
                filter(
                    lambda i12_:
                        (i12_[0], i12_[1]) != (i21, i22) and
                        (i12_[0] == i21 or i12_[1] == i21),
                    line_indices
                )
            )
            i21_unconnected = not connected

            start_index = i11 if i11_unconnected else i12
            end_index = i21 if i21_unconnected else i22

            cells[polygon_index].append((start_index, end_index))

    return cells


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
    vertices, line_indices = voronoi(delaunay=delaunay)

    voronoi_polygon_list = \
        get_voronoi_polygons_for_points_vertices_and_line_indices(
            points=points,
            line_indices=line_indices,
            vertices=vertices,
        )

    return voronoi_polygon_list


def get_voronoi_polygons_for_points_vertices_and_line_indices(
    *,
    points,
    vertices,
    line_indices: List[Tuple[int, int]],
):
    cells: DefaultDict[Any, List[Tuple]] = voronoi_cell_lines(
        points=points,
        vertices=vertices,
        line_indices=line_indices,
    )
    cells = close_outer_cells(cells=cells)
    voronoi_polygons_dict: Dict[int, List[int]] = \
        create_polygons_from_cells(cells=cells)

    voronoi_polygons_list: List[Any] = [
        vertices[
            np.asarray(
                voronoi_polygons_dict[point_index]
            )
        ]
        for point_index in range(len(points))
    ]

    return voronoi_polygons_list


def main():
    seed_standard_library_and_numpy()

    points: Union = get_points()

    delaunay: Delaunay = get_delaunay_tesselation(points=points)
    voronoi_polygon_list: List[Any] = get_voronoi_polygons(delaunay=delaunay)
    voronoi_polygons: List[Polygon] = \
        get_polygons(voronoi_polygon_list=voronoi_polygon_list)

    x = points[:, 0]
    y = points[:, 1]

    plot(
        delaunay_simplices=delaunay.simplices,
        voronoi_polygons=voronoi_polygons,
        x=x,
        y=y,
    )

    plt.show()


if __name__ == '__main__':
    main()
