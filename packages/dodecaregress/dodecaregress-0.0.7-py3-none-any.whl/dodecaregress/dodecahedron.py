from copy import deepcopy

import numpy as np
from scipy.spatial.transform import Rotation as R

from .pentagon import pentagon_axes, pentagon_centerpoint, pentagon_vertices
from .plotting import plot3d
from .transformations import pentagon_radius, batch_batch_transform, to_unified_mat, primitive_r_mat, make_t_mat, \
    make_r_mat, batch_matmul, faces6dof_to_center


def dodecahedron_axes():
    all_primitives = pentagon_axes(10, 12)
    all_primitives = batch_batch_transform(all_primitives)

    return all_primitives

def dodecahedron_face_centerpoints():
    centers = pentagon_centerpoint(12)
    centers = batch_batch_transform(centers)
    return centers

def dodecahedron_vertices():
    vertices = pentagon_vertices(pentagon_radius(), 12)
    vertices = batch_batch_transform(vertices)
    return vertices

class Dodecahedron:
    def __init__(self):
        self.vertices = dodecahedron_vertices()

        self.face_centerpoints = dodecahedron_face_centerpoints()
        self.face_angles = primitive_r_mat()
        self.face_axes = dodecahedron_axes()

        self.center = np.zeros(3)[None,None,:]
        self.center_axes = pentagon_axes(10, 1)
        self.center_angles = R.from_euler('xyz', np.zeros(3)).as_matrix()[None,:,:]

    def __copy__(self):
        return deepcopy(self)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def clone(self):
        return deepcopy(self)

    def _to_6dof(self, xyz, angles_mat):
        rvec = self._to_euler(angles_mat)
        return np.concatenate((xyz, rvec), axis=2)

    def _to_euler(self, angle):
        return R.from_matrix(angle).as_euler('xyz')[:, None, :]

    @property
    def faces_euler_angles(self):
        return self._to_euler(self.face_angles)

    @property
    def center_euler_angles(self):
        return self._to_euler(self.center_angles)

    @property
    def faces_6dof(self):
        return self._to_6dof(self.face_centerpoints, self.face_angles)

    @property
    def center_6dof(self):
        return self._to_6dof(self.center, self.center_angles)

    def transform(self, tvec, rvec):
        t = make_t_mat(tvec)
        r = make_r_mat(rvec)
        unified = to_unified_mat(t, r)

        clone = self.clone()


        clone.vertices = batch_batch_transform(clone.vertices, unified)

        clone.face_centerpoints = batch_batch_transform(clone.face_centerpoints, unified)
        clone.face_angles = batch_matmul(r, clone.face_angles)
        clone.face_axes = batch_batch_transform(clone.face_axes, unified)

        clone.center = batch_batch_transform(clone.center, unified[:1])
        clone.center_axes = batch_batch_transform(clone.center_axes, unified[:1])
        clone.center_angles = batch_matmul(r[:1], clone.center_angles)

        return clone

    @staticmethod
    def face6dof_to_dodecahedron(face_6dofs, ids):
        return Dodecahedron().transform(*faces6dof_to_center(face_6dofs, ids))

    def plot(self):
        plot3d(self.vertices, self.face_centerpoints, self.face_axes, self.center[0,0], self.center_axes[0], solid_polys=False)


