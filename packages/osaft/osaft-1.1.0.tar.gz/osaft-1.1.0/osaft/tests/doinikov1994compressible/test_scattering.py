import unittest

from osaft.core.functions import BesselFunctions as Bf
from osaft.solutions.doinikov1994compressible.scattering import ScatteringField
from osaft.tests.basetest import BaseTest
from osaft.tests.basetest_scattering import HelperScattering


class TestScattering(HelperScattering, BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self._v_particle_threshold = 1e-5
        self._v_fluid_threshold = 1e-3
        self._v_boundary_conditions = 1e-8

        self.cls = ScatteringField(
            self.f, self.R_0,
            self.rho_s, self.c_s,
            self.eta_s, self.zeta_s,
            self.rho_f, self.c_f,
            self.eta_f, self.zeta_f,
            self.p_0, self.wave_type,
            self.position,
        )

    # ------------------
    # fluid velocity
    # ------------------

    def V_r_sc(self, n, r) -> complex:
        # grad(phi)
        out = self.cls.k_f * self.alpha_n(n)
        out *= Bf.d1_hankelh1(n, self.cls.k_f * r)
        # curl(Psi)
        arg = self.cls.k_v * r
        out -= n * (n + 1) / r * self.beta_n(n) * Bf.hankelh1(n, arg)
        out *= self.cls.A_in(n)
        return out

    def V_theta_sc(self, n, r) -> complex:
        # curl(Psi)
        arg_v = self.cls.k_v * r
        out = Bf.hankelh1(n, arg_v)
        out += arg_v * Bf.d1_hankelh1(n, arg_v)
        out *= -self.beta_n(n)
        # grad(phi)
        out += self.alpha_n(n) * Bf.hankelh1(n, self.cls.k_f * r)

        out *= self.cls.A_in(n) / r
        return out

    # ------------------
    # particle velocity
    # ------------------

    def radial_particle_velocity(self, r, theta, t, mode):
        def vel(n, r):
            out = self.cls.k_s * self.alpha_hat_n(n)
            out *= Bf.d1_besselj(n, r * self.cls.k_s)
            arg = r * self.cls.k_vs
            out -= n * (n + 1) / r * self.beta_hat_n(n) * Bf.besselj(n, arg)
            out *= self.cls.A_in(n)
            return out

        out = self.cls.radial_mode_superposition(
            vel, r, theta, t, mode,
        )

        return out

    def tangential_particle_velocity(self, r, theta, t, mode):
        def vel(n, r):
            arg = r * self.cls.k_vs
            out = Bf.besselj(n, arg) + arg * Bf.d1_besselj(n, arg)
            out *= -self.beta_hat_n(n)
            out += self.alpha_hat_n(n) * Bf.besselj(n, r * self.cls.k_s)
            out *= self.cls.A_in(n) / r
            return out

        out = self.cls.tangential_mode_superposition(
            vel, r, theta, t, mode,
        )

        return out

    # ------------------
    # generic test method for coefficients
    # ------------------

    def test_coefficients(self) -> None:
        dict_of_methods = {}
        names = [
            'alpha_n', 'beta_n', 'alpha_hat_n', 'beta_hat_n',
        ]
        for name in names:
            dict_of_methods[name] = None

        self._test_methods_n(dict_of_methods, threshold=1e-8)

    # ------------------
    # testing scattering coefficients
    # ------------------

    def alpha_n(self, n: int) -> complex:
        return self.cls.det_M_n(n, 0) / self.cls.det_M_n(n)

    def beta_n(self, n: int) -> complex:
        if n > 0:
            return self.cls.det_M_n(n, 1) / self.cls.det_M_n(n)
        else:
            return 0

    def alpha_hat_n(self, n: int) -> complex:
        return self.cls.det_M_n(n, 2) / self.cls.det_M_n(n)

    def beta_hat_n(self, n: int) -> complex:
        if n > 0:
            return self.cls.det_M_n(n, 3) / self.cls.det_M_n(n)
        else:
            return 0

    # ------------------
    @property
    def x(self):
        return self.cls.x

    @property
    def x_v(self):
        return self.cls.x_v

    @property
    def x_hat(self):
        return self._compute_x_hat()

    def _compute_x_hat(self) -> complex:
        return self.R_0 * self.cls.k_s

    def test_x(self) -> None:
        self.do_testing(
            func_1=self._compute_x_hat,
            func_2=lambda: self.cls.x_hat,
        )

    # ------------------

    @property
    def x_hat_v(self):
        return self._compute_x_hat_v()

    def _compute_x_hat_v(self) -> complex:
        return self.R_0 * self.cls.k_vs

    def test_x_hat_v(self) -> None:
        self.do_testing(
            func_1=self._compute_x_hat_v,
            func_2=lambda: self.cls.x_hat_v,
        )


if __name__ == '__main__':
    unittest.main()
