from scipy.spatial import Delaunay

from vr_delaunay_to_voronoi.application.points_getting import get_points
from vr_delaunay_to_voronoi.voronoi.delaunay_tesselation_getting import \
    get_delaunay_tesselation


def test_get_delaunay_tesselation():
    # Arrange
    points = get_points()

    # Act
    delaunay_tesselation: Delaunay = get_delaunay_tesselation(points=points)

    # Assert
    assert delaunay_tesselation is not None
    assert isinstance(delaunay_tesselation, Delaunay)
