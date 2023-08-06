import unittest

from osaft import yosioka1955
from osaft.core.functions import pi
from osaft.plotting.datacontainers.scattering_datacontainer import (
    FluidScatteringData,
)
from osaft.solutions import doinikov1994rigid
from osaft.tests.basetest import BaseTest


class TestBaseScatteringDatacontainer(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.sol = yosioka1955.ScatteringField(
            self.f, self.R_0,
            self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0,
            self.wave_type,
            self.position,
        )

        self.cls = FluidScatteringData(
            self.sol, 5 * self.sol.R_0,
        )

    def test_setters_and_getters(self):
        # Change solution
        sol_2 = doinikov1994rigid.ScatteringField(
            self.f, self.R_0,
            self.rho_s,
            self.rho_f, self.c_f,
            self.eta_f, self.zeta_f,
            self.p_0,
            self.wave_type,
            self.position,
        )
        self.cls.sol = sol_2

        # Change r_min
        self.cls.r_min = 2e-6
        self.assertEqual(self.cls.r_min, 2e-6)

        # Change r_max
        self.cls.r_max = 10e-6
        self.assertEqual(self.cls.r_max, 10e-6)

        # Change theta min
        self.cls.theta_min = pi / 4
        self.assertEqual(self.cls.theta_min, pi / 4)

        # Change theta max
        self.cls.theta_max = pi / 2
        self.assertEqual(self.cls.theta_max, pi / 2)

    def test_change_resolution(self):
        self.cls.resolution = 200
        self.assertEqual(self.cls.grid.r_res, 200)


if __name__ == '__main__':
    unittest.main()
