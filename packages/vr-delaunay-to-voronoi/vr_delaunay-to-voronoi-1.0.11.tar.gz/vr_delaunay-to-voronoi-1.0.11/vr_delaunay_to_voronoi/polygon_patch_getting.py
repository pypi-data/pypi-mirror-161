import random
from typing import Tuple, List, Any

from matplotlib.patches import Polygon


def get_polygon(
    *,
    polygon_tuple: Tuple,
) -> Polygon:
    face_color: List[float] = [
        0.3 + 0.7 * random.random(),  # red channel
        0.3 + 0.7 * random.random(),  # green channel
        0.3 + 0.7 * random.random(),  # blue channel
        1,  # alpha channel
    ]
    closed: bool = True

    polygon: Polygon = \
        Polygon(
            xy=polygon_tuple,
            facecolor=face_color,
            closed=closed,
        )

    return polygon


def get_polygons(
    *,
    voronoi_polygon_list: List[Any],
) -> List[Polygon]:
    polygon_patches: List[Polygon] = [
        get_polygon(polygon_tuple=polygon_tuple)
        for polygon_tuple in voronoi_polygon_list
    ]

    return polygon_patches
