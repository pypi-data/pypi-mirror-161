from scipy.spatial import Delaunay


def get_delaunay_tesselation(
    *,
    points,
) -> Delaunay:
    """
    Get a Delaunay tesselation for the given points.
    """

    # Derive values from inputs
    ndim: int = len(points[0])

    # Configure Delaunay tesselation
    furthest_site: bool = False
    incremental: bool = False
    qhull_options: str = "Qbb Qc Qz Qx Q12" if ndim > 4 else "Qbb Qc Qz Q12"

    # Execute Delaunay tesselation
    delaunay_tesselation: Delaunay = Delaunay(
        points=points,
        furthest_site=furthest_site,
        incremental=incremental,
        qhull_options=qhull_options,
    )

    # Handle failure mode of Delaunay tesselation
    if delaunay_tesselation.coplanar.size != 0:
        raise ValueError(
            'The Delaunay triangulation did not contain some input points.'
            f'These were: {delaunay_tesselation.coplanar}'
        )

    return delaunay_tesselation
