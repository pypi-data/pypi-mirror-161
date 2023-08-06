import unittest

import numpy as np

from osaft.core.functions import pi
from osaft.core.helper import InputHandler as IH


class TestInputHandler(unittest.TestCase):

    def setUp(self):
        self.R_0 = 1
        self.arr_r_inside = np.linspace(0, 1)
        self.arr_r_outside = np.linspace(1, 2)
        self.arr_theta = np.linspace(0, pi)
        self.arr_time = np.linspace(0, 1)

    def test_ValueError_float(self):
        self.assertRaises(
            ValueError, IH.handle_input, 2.1, self.arr_theta,
            self.arr_time, self.R_0, True,
        )
        self.assertRaises(
            ValueError, IH.handle_input, 2.1, self.arr_theta,
            self.arr_time, self.R_0, True,
        )
        self.assertRaises(
            ValueError, IH.handle_input, -2.1, self.arr_theta,
            self.arr_time, self.R_0, True,
        )
        self.assertRaises(
            ValueError, IH.handle_input, 6.1, self.arr_theta,
            self.arr_time, self.R_0, True,
        )
        self.assertRaises(
            ValueError, IH.handle_input, -6.1, self.arr_theta,
            self.arr_time, self.R_0, True,
        )

    def test_ValueError_list(self):
        lst = [self.R_0 * (1 + np.random.rand()) for _ in np.arange(10)]

        lst[2] = 0.99 * self.R_0
        lst[3] = 1.0 * self.R_0
        self.assertRaises(
            ValueError, IH.handle_input, lst, self.arr_theta,
            self.arr_time, self.R_0, False,
        )

        lst[2] = -1.01 * self.R_0
        self.assertRaises(
            ValueError, IH.handle_input, lst, self.arr_theta,
            self.arr_time, self.R_0, True,
        )
        self.assertRaises(
            ValueError, IH.handle_input, lst, self.arr_theta,
            self.arr_time, self.R_0, False,
        )

    def test_ValueError_np_ndarray(self):
        self.assertRaises(
            ValueError, IH.handle_input, self.arr_r_outside,
            self.arr_theta, self.arr_time, self.R_0, True,
        )
        self.assertRaises(
            ValueError, IH.handle_input, self.arr_r_inside,
            self.arr_theta, self.arr_time, self.R_0, False,
        )


if __name__ == '__main__':
    unittest.main()
