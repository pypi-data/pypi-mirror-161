import numpy as np

from .transformations import make_t_mat, make_r_mat, to_unified_mat, batch_batch_transform


def repeat(pentagon_data, n):
    return np.tile(pentagon_data, (n, 1, 1))


def pentagon_vertices(radius, n=1):
    radius = radius * 0.9   # you can uncomment. Vertices are just for debugging anyway
    # https://math.stackexchange.com/questions/1990504/how-to-find-the-coordinates-of-the-vertices-of-a-pentagon-centered-at-the-origin
    # radius is distance from center to a vertex

    # i think original matrices were using x axis as 0 axis but we are using y (?) idk who cares pi/10 works lol
    ROT = np.pi / 10
    mode = ROT + np.arange(5) * 2 * np.pi / 5

    x = np.cos(mode)
    y = np.sin(mode)

    poly = radius * np.array([x, y, np.zeros(5)]).T

    polys = repeat(poly, n)

    return polys

def pentagon_axes(d, n=1):
    axis = np.identity(3) * d

    axis = repeat(axis, n)

    return axis

def angle2axes(center, angles, d):
    raise Exception()   # this function CAN be used. But shouldnt be. Just for debugging!


    axes = pentagon_axes(d, len(center))


    t = make_t_mat(center)
    r = make_r_mat(angles)
    unified = to_unified_mat(t, r)[:len(center)]

    axes_transf = batch_batch_transform(axes, unified)
    return axes_transf


def pentagon_centerpoint(n=1):
    centerpoint = np.zeros(3)[None,:]
    return repeat(centerpoint, n)
