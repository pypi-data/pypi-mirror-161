import unittest

import numpy as np

from osaft import king1934
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import LegendreFunctions as Leg
from osaft.core.functions import cos, exp, sin
from osaft.tests.basetest_scattering import HelperScattering
from osaft.tests.king1934.test_base import BaseKing


class TestScattering(HelperScattering, BaseKing):

    def setUp(self) -> None:

        super().setUp()

        self.small_particle_limit = False
        self.cls = king1934.ScatteringField(
            self.f,
            self.R_0, self.rho_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type,
            self.position,
        )
        self.list_cls = [self.cls]

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def A_dash_n(self, n: int):
        arg = self.cls.alpha
        out = - self.cls.A_in(n) * self.G_n(n, arg)
        out /= (self.G_n(n, arg) + 1j * self.F_n(n, arg))
        return out

    def V_r_sc(self, n, r) -> complex:
        out = self.A_dash_n(n)
        out *= self.cls.k_f
        out *= Bf.d1_hankelh2(n, self.cls.k_f * r)
        return out

    def V_theta_sc(self, n, r) -> complex:
        out = self.A_dash_n(n)
        out *= Bf.hankelh2(n, self.cls.k_f * r)
        out /= r
        return out

    def Phi_incident(
        self, r, theta, t,
    ) -> complex:
        def Phi_n(n):
            arg = self.cls.A_in(n) * Bf.besselj(n, r * self.cls.k_f)
            out = exp(-1j * self.cls.omega * t)
            out *= Leg.cos_monomial(n, theta, arg)
            return out

        return np.sum([Phi_n(n) for n in range(self.N_max + 1)])

    def Phi_scattering(
        self, r, theta, t,
    ) -> complex:
        def Phi_n(n):
            arg = - self.G_n(n, self.cls.alpha)
            arg /= (
                self.G_n(n, self.cls.alpha) + 1j * self.F_n(n, self.cls.alpha)
            )
            arg *= self.cls.A_in(n) * Bf.hankelh2(n, r * self.cls.k_f)
            out = exp(-1j * self.cls.omega * t)
            out *= Leg.cos_monomial(n, theta, arg)
            return out

        return np.sum([Phi_n(n) for n in range(self.N_max + 1)])

    def radial_particle_velocity(self, r, theta, t, mode):
        if mode == 1 or mode is None:
            return self.particle_velocity(t) * cos(theta)
        else:
            return 0

    def tangential_particle_velocity(self, r, theta, t, mode):
        if mode == 1 or mode is None:
            return -self.particle_velocity(t) * sin(theta)
        else:
            return 0

    def particle_velocity(self, t):
        alpha = self.cls.alpha

        out = self.F_n(1, alpha)
        out -= 1j * self.G_n(1, alpha)
        out = 1 / out

        out *= self.cls.A_in(1) / alpha**3
        out *= self.cls.k_f * self.rho_f / self.rho_s
        out *= exp(-1j * self.cls.omega * t)

        return out

    # -------------------------------------------------------------------------
    # Test coefficients
    # -------------------------------------------------------------------------

    def test_methods(self) -> None:
        method_dict = {}
        method_dict['A_dash_n'] = None

        # need to be float otherwise
        # Integers to negative integer powers are not allowed.
        method_dict['phi_n'] = 2.0
        method_dict['psi_n'] = 2.0

        arg = self.cls.k_f * self.get_random_r(self.cls)
        method_dict['F_n'] = arg
        method_dict['G_n'] = arg

        arg = self.get_random_r(self.cls)
        method_dict['V_r_sc'] = arg
        method_dict['V_theta_sc'] = arg

        self._test_methods_n(method_dict)

    def test_Phi_incident(self) -> None:
        for i in range(5):
            r = self.get_random_r(self.cls)
            t = self.get_random_t()
            theta = self.get_random_theta()
            self.N_max = i
            self.cls.N_max = i

            self.do_testing(
                func_1=self.Phi_incident, args_1=(r, theta, t),
                func_2=self.cls.Phi_incident, args_2=(r, theta, t),
            )

    def test_Phi_scattering(self) -> None:
        for i in range(5):
            r = self.get_random_r(self.cls)
            t = self.get_random_t()
            theta = self.get_random_theta()

            self.N_max = i
            self.cls.N_max = i

            self.do_testing(
                func_1=self.Phi_scattering, args_1=(r, theta, t),
                func_2=self.cls.Phi_scattering, args_2=(r, theta, t),
            )


if __name__ == '__main__':
    unittest.main()
