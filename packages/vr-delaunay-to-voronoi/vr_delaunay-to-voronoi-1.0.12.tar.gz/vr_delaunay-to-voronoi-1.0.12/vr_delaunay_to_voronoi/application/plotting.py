from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from vr_delaunay_to_voronoi.shims.matplotlib_axes import add_patches_to_axes


def plot(
    *,
    delaunay_simplices,
    voronoi_polygons,
    x,
    y,
):
    plt.figure(figsize=(4.5, 4.5))
    plt.axis(
        [-0.05, 1.05, -0.05, 1.05]
    )
    axes: Axes = plt.subplot(1, 1, 1)

    # Plot voronoi polygons
    add_patches_to_axes(axes=axes, polygon_patches=voronoi_polygons)

    # Plot delaunay simplices
    axes.triplot(
        x,
        y,
        delaunay_simplices,
    )

    # Plot points
    color = (0, 0, 0, 1)  # Opaque black
    colors = [color] * len(x)
    plt.scatter(
        x=x,
        y=y,
        c=colors,
        marker='.',  # Dot
        zorder=1,    # Foreground
    )
