import unittest

import numpy as np

from osaft import doinikov1994rigid
from osaft.core.functions import pi
from osaft.core.functions import spherical_2_cartesian_coordinates as s2c_coord
from osaft.core.functions import spherical_2_cartesian_vector as s2c_vector
from osaft.plotting.datacontainers.wireframe_datacontainer import (
    DeformedLine,
    ParticleWireframeData,
)
from osaft.tests.basetest import BaseTest


class TestWireframeDatacontainer(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.sol = doinikov1994rigid.ScatteringField(
            self.f, self.R_0,
            self.rho_s,
            self.rho_f, self.c_f,
            self.eta_f, self.zeta_f,
            self.p_0,
            self.wave_type,
            self.position,
        )

        self.cls = ParticleWireframeData(
            self.sol, nbr_r_levels=10,
            nbr_theta_levels=10,
            resolution=(50, 50),
            scale_factor=0.2,
        )

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def arr_r(self):
        return np.linspace(1e-30, self.sol.R_0, self.cls.resolution[0])

    def arr_theta(self):
        if self.cls.symmetric:
            return np.linspace(0, pi, self.cls.resolution[1])
        else:
            return np.linspace(0, 2 * pi, self.cls.resolution[1])

    def deformed_radius(self, theta):
        # Displacements
        u_r = self.sol.radial_particle_displacement(
            self.arr_r(), theta, t=0,
        )
        u_t = self.sol.tangential_particle_displacement(
            self.arr_r(), theta, t=0,
        )
        u, v = s2c_vector(u_r, u_t, theta)
        u_scaled = u * self.cls.scale_factor
        v_scaled = v * self.cls.scale_factor

        # Coordinates
        x, y = s2c_coord(self.arr_r(), theta)

        return DeformedLine(x, y, u_scaled, v_scaled)

    def deformed_circle(self, radius):
        # Displacements
        u_r = self.sol.radial_particle_displacement(
            radius, self.arr_theta(), t=0,
        )
        u_t = self.sol.tangential_particle_displacement(
            radius, self.arr_theta(), t=0,
        )
        u, v = s2c_vector(u_r, u_t, self.arr_theta())
        u_scaled = u * self.cls.scale_factor
        v_scaled = v * self.cls.scale_factor

        # Coordinates
        x, y = s2c_coord(radius, self.arr_theta())

        return DeformedLine(x, y, u_scaled, v_scaled)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def compare_deformed_lines(df_1: DeformedLine, df_2: DeformedLine):
        x_1, y_1 = df_1.get_reference()
        x_2, y_2 = df_2.get_reference()
        u_1, v_1 = df_2.get_deformed(0)
        u_2, v_2 = df_2.get_deformed(0)
        np.testing.assert_array_equal(x_1, x_2)
        np.testing.assert_array_equal(y_1, y_2)
        np.testing.assert_array_equal(u_1, u_2)
        np.testing.assert_array_equal(v_1, v_2)

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_nbr_t_level_setter(self) -> None:
        self.cls.symmetric = True
        self.cls.nbr_theta_levels = 9
        self.assertEqual(self.cls.nbr_theta_levels, 10)
        self.cls.symmetric = False
        self.cls.nbr_theta_levels = 9
        self.assertEqual(self.cls.nbr_theta_levels, 9)

    def test_nbr_levels_dependencies(self) -> None:
        self.cls.nbr_r_levels = 15
        self.assertEqual(len(self.cls.r_levels), 15)
        self.cls.nbr_theta_levels = 16
        self.assertEqual(len(self.cls.theta_levels), 8)

    def test_resolution_setter(self) -> None:
        def test_res(value: int) -> None:
            self.assertEqual(self.cls.resolution[0], value)
        self.cls.resolution = (100, 100)
        test_res(100)
        self.cls.resolution = 120
        test_res(120)
        self.cls.resolution = [130]
        test_res(130)
        with self.assertRaises(ValueError):
            self.cls.resolution = (100, 100, 100)

    def test_symmetric(self) -> None:
        self.cls.nbr_theta_levels = 16
        self.assertEqual(len(self.cls.theta_levels), 8)
        self.cls.symmetric = False
        self.assertEqual(len(self.cls.theta_levels), 16)

    def test_scale_factor(self) -> None:
        self.cls.rel_scale_factor = 1
        sf_1 = self.cls.scale_factor
        self.cls.rel_scale_factor = 2
        sf_2 = self.cls.scale_factor
        self.assertAlmostEqual(sf_1, sf_2 / 2)

    def test_setters_and_getters(self) -> None:
        # Solution
        self.cls.sol = self.sol
        self.assertEqual(self.cls.sol, self.sol)
        # nbr_r_levels
        self.cls.nbr_r_levels = 10
        self.assertEqual(self.cls.nbr_r_levels, 10)
        # Mode
        self.cls.mode = None
        self.assertIsNone(self.cls.mode)
        # Scale Factor
        self.cls.rel_scale_factor = 0.3
        self.assertEqual(self.cls.rel_scale_factor, 0.3)

    def test_arr_r(self) -> None:
        np.testing.assert_array_equal(self.arr_r(), self.cls.arr_r)
        self.assertEqual(self.cls.arr_r.max(), self.sol.R_0)

    def test_arr_theta(self):
        # Not symmetric
        self.cls.symmetric = False
        np.testing.assert_array_equal(self.arr_theta(), self.cls.arr_theta)
        self.assertEqual(self.cls.arr_theta.max(), 2 * pi)
        # Symmetric
        self.cls.symmetric = True
        np.testing.assert_array_equal(self.arr_theta(), self.cls.arr_theta)
        self.assertEqual(self.cls.arr_theta.max(), pi)

    def test_deformed_circles(self):
        deformed_circles = self.cls.deformed_circles
        for index, radius in enumerate(self.cls.r_levels):
            df_1 = deformed_circles[index]
            df_2 = self.deformed_circle(radius)
            self.compare_deformed_lines(df_1, df_2)

    def test_deformed_radii(self):
        deformed_radii, _ = self.cls.get_displacements()
        for index, theta in enumerate(self.cls.theta_levels):
            df_1 = deformed_radii[index]
            df_2 = self.deformed_radius(theta)
            self.compare_deformed_lines(df_1, df_2)


if __name__ == '__main__':
    unittest.main()
