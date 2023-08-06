import numpy as np

from scipy.spatial.transform import Rotation as R

import pathlib
path = pathlib.Path(__file__).parent.resolve()

_R_cent_face = np.load(str(path / 'Center_face_rotations.npy'))
_T_cent_face = np.load(str(path / 'Center_face_translations.npy'))

def batch_matmul(angles_mat, transform_mat):
    assert transform_mat.shape == angles_mat.shape

    rs = np.einsum('ijk,ikl->ijl', angles_mat, transform_mat)
    return rs

def set_scale(scale=1.0):
    global _R_cent_face
    global _T_cent_face
    scale_mat = np.identity(3) * scale
    _12scale = np.tile(scale_mat, (len(_T_cent_face), 1, 1))

    _T_cent_face = np.load(str(path / 'Center_face_translations.npy'))
    #_R_cent_face = batch_matmul(_R_cent_face, _12scale)
    _T_cent_face *= scale


def primitive_r_mat():
    mat = _R_cent_face
    return mat

def make_t_mat(t_array):
    if len(t_array.shape) == 1:
        t_array = t_array[None, :]
    if len(t_array) == 1:
        t_array = np.repeat(t_array, 12, axis=0)
    return t_array

def make_r_mat(r):
    if len(r.shape) == 1:
        r = r[None, :]
    if len(r) == 1:
        r = np.repeat(r, 12, axis=0)

    rmats = R.from_euler('xyz', r).as_matrix()
    return rmats


def to_unified_mat(t_mat=_T_cent_face, r_mat=_R_cent_face, scale=0.5, inverse=False):  # todo include scale
    scale_mat = np.identity(4) * scale
    scale_mat[-1,-1] = 1
    _12scale = np.tile(scale_mat, (len(t_mat), 1, 1))

    diag = np.identity(4)
    _12diag = np.tile(diag, (len(t_mat), 1, 1))

    tmat = t_mat.squeeze()
    _12diag[:, :3, -1] = tmat

    rmat = r_mat
    _12diag[:, :3, :3] = rmat

    if inverse:
        _12diag = np.linalg.inv(_12diag)

    #_12diag = batch_matmul(_12diag, _12scale)

    return _12diag


def pentagon_radius():
    # radius is the distance from a vertex to the center of a given pentagon

    center_face_distance = np.linalg.norm(_T_cent_face[0].squeeze())

    rm_constant = (1 / 4 * (3 + np.sqrt(5)))
    ri_constant = (1 / 2 * np.sqrt(5 / 2 + 11 / 10 * np.sqrt(5)))
    ru_constant = ((np.sqrt(3) / 4) * (1 + np.sqrt(5)))
    a = center_face_distance / ri_constant
    radius = a * np.sqrt(5 + 2 * np.sqrt(5)) / 4
    radius = radius * 1.11  # why does 1.11 work even?!
    return radius


def symmetry(id):
    # [2, 1, 0, 3, 4, 5, 0, 1, 2, 3, 4, 5]
    mapping = np.array([8, 7, 6, 9, 10, 11, 2, 1, 0, 3, 4, 5])
    return mapping[id]


def batch_batch_transform(array_of_points, transform_mat=None):
    if len(array_of_points) == 12 and transform_mat is None:
        transform_mat = to_unified_mat()
    else:
        assert transform_mat is not None

    array_of_points = add_dummy(array_of_points)

    old_shape = array_of_points.shape
    flat_first2 = old_shape[0] * old_shape[1]

    array_of_points = array_of_points.reshape((flat_first2, old_shape[2]))

    transform_mat2 = np.repeat(transform_mat, old_shape[1], axis=0)

    #all_points = []
    #for pt, tr in zip(array_of_points, transform_mat2):
    #    all_points.append(tr @ pt)
    #all_points = np.array(all_points)
    all_points = np.einsum('ijk,ik->ij', transform_mat2, array_of_points)  # todo am i doing this wrong lol

    all_points = all_points.reshape(old_shape)

    return all_points[:, :, :-1]


def add_dummy(vects):
    vects = vects

    must_squeeze = False
    if len(vects.shape) == 1:
        vects = vects[None, None, :]
        must_squeeze = True

    shape = vects.shape[:-1]
    dummy = np.ones(shape=(*shape, 1))

    x = np.dstack((vects, dummy))

    if must_squeeze:
        x = x.squeeze(0).squeeze(0)

    return x



def _faces6dof_to_transformation_filter(tvec, rvec):
    # TODO some sort of better filter here
    tvec_mean = tvec.mean(axis=0)
    rvec_mean = rvec.mean(axis=0)
    return tvec_mean, rvec_mean


def faces6dof_to_center(face_6dofs, ids):
    assert isinstance(ids, np.ndarray) and face_6dofs.shape[1] == 1
    # retrieves center's pose from face's pose
    tvec = face_6dofs[:, 0, :3]
    rvec = face_6dofs[:, 0, 3:]

    transformation_t = make_t_mat(tvec)[:len(ids)]
    transformation_r = make_r_mat(rvec)[:len(ids)]

    origin_2_faceprime = to_unified_mat(transformation_t, transformation_r)

    face_2_origin = to_unified_mat(inverse=True)[ids]

    origin_2_originprime = batch_matmul(origin_2_faceprime, face_2_origin)

    centroid = origin_2_originprime[:,:-1,-1]
    centroid_angles = R.from_matrix(origin_2_originprime[:,:3,:3]).as_euler('xyz')

    centroid_angles = np.abs(centroid_angles)   # fixme: not a real issue but there's some weird stuff with angles, since -np.pi == np.pi, in terms of rotation

    return _faces6dof_to_transformation_filter(centroid, centroid_angles)



