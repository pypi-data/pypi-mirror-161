import matplotlib
import numpy as np

from dodecahedron import Dodecahedron
from transformations import faces6dof_to_center

if __name__ == "__main__":
    matplotlib.use('TKAgg')
    temp = Dodecahedron()
    temp.plot()

    def test(translate, rotate):
        temp2 = temp.transform(translate, rotate)
        temp2.plot()

        ids = np.arange(12)[3:7]
        faces_xyz = temp2.faces_6dof[3:7]
        recovered_translate, recovered_rotate = faces6dof_to_center(faces_xyz, ids)
        assert np.allclose(recovered_translate, translate) and np.allclose(recovered_rotate, rotate)

    test(np.array([10,0,0]), np.array([0, 0,np.pi]))
    test(np.array([10,30,80]), np.array([np.pi, np.pi/8, np.pi]))
