import numpy as np

from .transformations import symmetry


def face2color(i):
    colors = [(0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0)]
    colors2 = ["yellow", "cyan", "magenta", "purple", "pink", "lime", "red", "green", "orange", "black", "gray", "brown"]

    print(i, colors2[i])

    return colors2[i]

    min_mapping = symmetry(i)
    min_mapping = min(i, min_mapping)

    return colors[min_mapping]

def plot_p2p(ax, point1, point2, color):
    ax.plot([point1[0], point2[0]], [point1[1], point2[1]], [point1[2], point2[2]], color=color)

def plot_axes(ax, centerpoint, axes):
    for i, _axe in enumerate(axes):
        axis_colors = ["c", "m", "y"]
        plot_p2p(ax, centerpoint, _axe, axis_colors[i])

def plot3d(polys, centerpoints, axes, center, center_axis, solid_polys=True):
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import matplotlib.pyplot as plt
    import matplotlib
    fig = plt.figure()
    ax = Axes3D(fig, auto_add_to_figure=False)
    ax.set_xlim3d(-30, 30)
    ax.set_ylim3d(-30, 30)
    ax.set_zlim3d(-30, 30)
    fig.add_axes(ax)

    assert len(polys) == len(centerpoints) == len(axes)

    ax.view_init(elev=35, azim=45)
    for i in range(len(polys)):
        poly = polys[i]
        color = face2color(i)
        centerpoint = centerpoints[i].squeeze()
        axe = axes[i]

        if solid_polys:
            mpl_poly = Poly3DCollection([poly])
            mpl_poly.set_facecolor(color)
            ax.add_collection3d(mpl_poly)
        else:
            for j in range(len(poly)):
                point1 = poly[j]
                next_j = (j + 1) % len(poly)
                point2 = poly[next_j]
                plot_p2p(ax, point1, point2, color)

        #plot_p2p(ax, centerpoint, center, color)
        plot_axes(ax, centerpoint, axe)
    plot_axes(ax, center, center_axis)
    #verts = get_centerpoints()
    #_draw_pose_axes(ax)
    plt.show()
