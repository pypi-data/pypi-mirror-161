import unittest
from unittest import TestCase

import numpy as np

from osaft.core.functions import pi
from osaft.plotting.grid import Grid


class TestGrid(TestCase):

    def setUp(self) -> None:

        self.r_min = 1
        self.r_max = 10
        self.theta_min = 0
        self.theta_max = 2 * pi
        self.res_1 = 100
        self.res_2 = 50

        # Grid with the same resolution in both dimensions
        self.grid_1_res = Grid(
            self.r_min, self.r_max, self.theta_min,
            self.theta_max, self.res_1,
        )
        # Grid with the same resolution in both dimensions from a tuple
        self.grid_1_from_seq_res = Grid(
            self.r_min, self.r_max, self.theta_min,
            self.theta_max, [self.res_1],
        )
        # Grid with the different resolutions in the two dimensions
        self.grid_2_res = Grid(
            self.r_min, self.r_max, self.theta_min,
            self.theta_max, (self.res_1, self.res_2),
        )

    def test_dr(self):
        dr = (self.r_max - self.r_min) / self.res_1
        self.assertEqual(self.grid_1_res.dr, dr)
        self.assertEqual(self.grid_1_from_seq_res.dr, dr)
        self.assertEqual(self.grid_2_res.dr, dr)

    def test_dtheta(self):
        dtheta_1 = (self.theta_max - self.theta_min) / self.res_1
        dtheta_2 = (self.theta_max - self.theta_min) / self.res_2
        self.assertEqual(self.grid_1_res.dtheta, dtheta_1)
        self.assertEqual(self.grid_1_from_seq_res.dtheta, dtheta_1)
        self.assertEqual(self.grid_2_res.dtheta, dtheta_2)

    def test_arr_r(self):
        arr_r = np.linspace(self.r_min, self.r_max, self.res_1)
        np.testing.assert_array_equal(self.grid_1_res.arr_r, arr_r)
        np.testing.assert_array_equal(self.grid_1_from_seq_res.arr_r, arr_r)
        np.testing.assert_array_equal(self.grid_2_res.arr_r, arr_r)

    def test_arr_theta(self):
        arr_theta_1 = np.linspace(self.theta_min, self.theta_max, self.res_1)
        arr_theta_2 = np.linspace(self.theta_min, self.theta_max, self.res_2)
        np.testing.assert_array_equal(self.grid_1_res.arr_theta, arr_theta_1)
        np.testing.assert_array_equal(
            self.grid_1_from_seq_res.arr_theta,
            arr_theta_1,
        )
        np.testing.assert_array_equal(self.grid_2_res.arr_theta, arr_theta_2)

    def test_ValuerError(self):

        self.assertRaises(
            ValueError, Grid, r_min=self.r_min, r_max=self.r_max,
            theta_min=self.theta_min, theta_max=self.theta_max,
            res=3 * [self.res_1],
        )


if __name__ == '__main__':
    unittest.main()
