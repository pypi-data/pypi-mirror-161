import unittest

from osaft import hasegawa1969
from osaft.core.functions import BesselFunctions as Bf
from osaft.tests.basetest import BaseTest
from osaft.tests.basetest_scattering import HelperScattering


class TestScattering(BaseTest, HelperScattering):

    def setUp(self) -> None:

        BaseTest.setUp(self)

        self._v_boundary_conditions = 1e-9
        self.N_max = 5

        self.cls = hasegawa1969.ScatteringField(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s, E_s=self.E_s, nu_s=self.nu_s,
            rho_f=self.rho_f, c_f=self.c_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
        )

        self.list_cls = [self.cls]

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def c_n(self, n: int) -> complex:

        nu = self.cls.nu_s
        k_f = self.cls.k_f
        k_s_1 = self.cls.k_s_l
        k_s_2 = self.cls.k_s_t
        x_f = self.R_0 * k_f
        x_s_1 = self.R_0 * k_s_1
        x_s_2 = self.R_0 * k_s_2
        j = lambda x: Bf.besselj(n, x)
        dj = lambda x: Bf.d1_besselj(n, x)
        ddj = lambda x: Bf.d2_besselj(n, x)
        h = lambda x: Bf.hankelh2(n, x)
        dh = lambda x: Bf.d1_hankelh2(n, x)

        frac1 = (
            (x_s_1 * dj(x_s_1)) /
            (x_s_1 * dj(x_s_1) - j(x_s_1))
        )
        frac2 = (
            2 * n * (n + 1) * j(x_s_2) /
            ((n + 2) * (n - 1) * j(x_s_2) + x_s_2 ** 2 * ddj(x_s_2))
        )
        frac3 = (
            x_s_1 ** 2 *
            (nu / (1 - 2 * nu) * j(x_s_1) - ddj(x_s_1)) /
            (x_s_1 * dj(x_s_1) - j(x_s_1))
        )
        frac4 = (
            2 * n * (n + 1) * (j(x_s_2) - x_s_2 * dj(x_s_2)) /
            ((n + 2) * (n - 1) * j(x_s_2) + x_s_2 ** 2 * ddj(x_s_2))
        )

        F_n = (frac1 - frac2) / (frac3 - frac4)
        F_n *= 1 / 2 * self.rho_f / self.rho_s * x_s_2 ** 2

        c_n = - (
            (F_n * j(x_f) - x_f * dj(x_f)) /
            (F_n * h(x_f) - x_f * dh(x_f))
        )

        return c_n

    def c_n_A(self, n: int) -> complex:
        return self.cls.c_n(n) * self.cls.A_in(n)

    def a_n(self, n: int) -> complex:

        k_f = self.cls.k_f
        k_s_1 = self.cls.k_s_l
        k_s_2 = self.cls.k_s_t
        x_f = self.R_0 * k_f
        x_s_1 = self.R_0 * k_s_1
        x_s_2 = self.R_0 * k_s_2
        A_in = self.cls.A_in(n)
        c_n = self.cls.c_n_A(n)
        j = lambda x: Bf.besselj(n, x)
        dj = lambda x: Bf.d1_besselj(n, x)
        ddj = lambda x: Bf.d2_besselj(n, x)
        dh = lambda x: Bf.d1_hankelh1(n, x)

        a_num = (
            x_f *
            (c_n * dh(x_f) + A_in * dj(x_f)) *
            ((n**2 + n - 1) * x_s_2 * dj(x_s_2) - j(x_s_2))
        )
        a_den = (
            n * (n + 1) *
            (- (x_s_1 ** 2) * ddj(x_s_1) + j(x_s_1)) * j(x_s_2)
        )
        a_den += (
            x_s_1 * dj(x_s_1) * (
                (n ** 2 + n - 1) * x_s_2 * dj(x_s_2)
                - (n ** 2 + n + 1) * j(x_s_2)
            )
        )

        return a_num / a_den

    def b_n(self, n: int) -> complex:

        k_f = self.cls.k_f
        k_s_1 = self.cls.k_s_l
        k_s_2 = self.cls.k_s_t
        x_f = self.R_0 * k_f
        x_s_1 = self.R_0 * k_s_1
        x_s_2 = self.R_0 * k_s_2
        A_in = self.cls.A_in(n)
        c_n = self.cls.c_n_A(n)
        j = lambda x: Bf.besselj(n, x)
        dj = lambda x: Bf.d1_besselj(n, x)
        ddj = lambda x: Bf.d2_besselj(n, x)
        dh = lambda x: Bf.d1_hankelh1(n, x)

        b_nom = (
            - x_f *
            (c_n * dh(x_f) + A_in * dj(x_f)) *
            (x_s_1 * (x_s_1 * ddj(x_s_1) + dj(x_s_1)) - j(x_s_1))
        )
        b_num = (
            n * (n + 1) *
            (x_s_1 ** 2 * ddj(x_s_1) - j(x_s_1)) * j(x_s_2)
        )
        b_num += (
            x_s_1 * dj(x_s_1) * (
                - (n ** 2 + n - 1) * x_s_2 * dj(x_s_2)
                + (n ** 2 + n + 1) * j(x_s_2)
            )
        )

        return b_nom / b_num

    def V_r_sc(self, n, r):
        c_n = self.cls.c_n_A(n)
        k_f = self.cls.k_f
        return k_f * c_n * Bf.d1_hankelh1(n, k_f * r)

    def V_theta_sc(self, n, r):
        c_n = self.cls.c_n_A(n)
        k_f = self.cls.k_f
        return c_n * Bf.hankelh1(n, k_f * r) / r

    def radial_particle_velocity(self, r, theta, t, mode):

        def radial_func(l, x):
            k_s_1 = self.cls.k_s_l
            k_s_2 = self.cls.k_s_t
            a_n = self.cls.a_n(l)
            b_n = self.cls.b_n(l)
            j = Bf.besselj
            dj = Bf.d1_besselj
            term1 = k_s_1 * a_n * dj(l, k_s_1 * x)
            term2 = l * (l + 1) / x * b_n * j(l, k_s_2 * x)
            return term1 - term2

        return self.cls.radial_mode_superposition(
            radial_func, r, theta, t,
            mode,
        )

    def tangential_particle_velocity(self, r, theta, t, mode):

        def radial_func(l, x):
            k_s_1 = self.cls.k_s_l
            k_s_2 = self.cls.k_s_t
            a_n = self.cls.a_n(l)
            b_n = self.cls.b_n(l)
            j = Bf.besselj
            dj = Bf.d1_besselj
            term1 = a_n * j(l, k_s_1 * x)
            term2 = b_n * (j(l, k_s_2 * x) + k_s_2 * x * dj(l, k_s_2 * x))
            return (term1 - term2) / x

        return self.cls.tangential_mode_superposition(
            radial_func, r, theta, t,
            mode,
        )

    def test_c_n(self):
        for n in range(self.n_runs, -1, -1):
            self.do_testing(
                func_1=self.cls.c_n, args_1=n,
                func_2=self.c_n, args_2=n,
                threshold=1e-9,
            )

    def test_c_n_A(self):
        for n in range(self.n_runs, -1, -1):
            self.do_testing(
                func_1=self.cls.c_n_A, args_1=n,
                func_2=self.c_n_A, args_2=n,
                threshold=1e-9,
            )

    def test_a_n(self):
        for n in range(self.n_runs, -1, -1):
            self.do_testing(
                func_1=self.cls.a_n, args_1=n,
                func_2=self.a_n, args_2=n,
                threshold=1e-9,
            )

    def test_b_n(self):
        for n in range(self.n_runs, -1, -1):
            self.do_testing(
                func_1=self.cls.b_n, args_1=n,
                func_2=self.b_n, args_2=n,
                threshold=1e-9,
            )

    def test_V_r_sc(self):
        for n in range(self.n_runs):
            r = self.get_random_r(self.cls)
            self.do_testing(
                func_1=self.cls.V_r_sc, args_1=(n, r),
                func_2=self.V_r_sc, args_2=(n, r),
            )

    def test_V_theta_sc(self):
        for n in range(self.n_runs):
            r = self.get_random_r(self.cls)
            self.do_testing(
                func_1=self.cls.V_theta_sc, args_1=(n, r),
                func_2=self.V_theta_sc, args_2=(n, r),
            )


if __name__ == '__main__':
    unittest.main()
