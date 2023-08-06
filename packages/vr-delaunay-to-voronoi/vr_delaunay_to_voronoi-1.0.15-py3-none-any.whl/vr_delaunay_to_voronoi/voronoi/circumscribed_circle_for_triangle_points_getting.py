import numpy as np


def get_circumscribed_circle_for_triangle_points(*, points):
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
