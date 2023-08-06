import numpy as np


def get_points():
    points = np.random.normal(
        loc=(0.5, 0.5),
        scale=(0.2, 0.2),
        size=(10, 2),
    )

    return points
