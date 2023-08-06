import unittest

from osaft import WaveType, gorkov1962, king1934, yosioka1955
from osaft.core.backgroundfields import WrongWaveTypeError
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import conj, pi, sin
from osaft.tests.basetest import BaseTest
from osaft.tests.basetest_arf import HelperCompareARF


class TestARF(BaseTest):

    def setUp(self) -> None:
        super().setUp()

        self.N_max = 5

        self.cls = yosioka1955.ARF(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s, c_s=self.c_s,
            rho_f=self.rho_f, c_f=self.c_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
        )

        self.list_cls = [self.cls]

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    @property
    def F(self):
        sigma = self.cls.sigma
        lamb = self.cls.lambda_rho
        x_s = self.cls.x_s

        if self.wave_type == WaveType.STANDING:
            if self.cls.bubble_solution:
                out = sigma * x_s ** 3 * (3 * lamb - x_s**2)
                out /= sigma ** 2 * x_s ** 6 + (3 * lamb - x_s ** 2) ** 2
                return out
            else:
                out = lamb + (2 * (lamb - 1) / 3)
                out /= 1 + 2 * lamb
                out -= 1 / (3 * lamb * sigma ** 2)
                return out
        else:
            if self.cls.bubble_solution:
                pass
            else:
                out = (lamb - (1 + 2 * lamb) / (3 * lamb * sigma ** 2)) ** 2
                out += 2 / 9 * (1 - lamb) ** 2
                out *= 1 / (1 + 2 * lamb) ** 2
                return out

    def small_particle_ARF(self):
        if self.wave_type == WaveType.STANDING:
            if self.cls.bubble_solution:
                return self._small_bubble_standing()
            else:
                return self._small_particle_standing()
        else:
            if self.cls.bubble_solution:
                return self._small_bubble_travelling()
            else:
                return self._small_particle_travelling()

    def _small_particle_standing(self):
        k = self.cls.k_f
        E = self.cls.E_ac
        R = self.R_0
        F = self.F
        h = self.cls.position
        return pi * R ** 3 * 4 * k * E * sin(2 * h) * F

    def _small_particle_travelling(self):
        R = self.R_0
        I = self.cls.I_ac
        c = self.c_f
        F = self.F
        x = self.cls.x_f
        return pi * R ** 2 * 4 * x ** 4 * I / c * F

    def _small_bubble_travelling(self):
        I = self.cls.I_ac
        sigma = self.cls.sigma
        lamb = self.cls.lambda_rho
        x_s = self.cls.x_s
        R = self.R_0
        c = self.c_f
        res = (3 * lamb - x_s ** 2)
        out = 4 * pi * R ** 2 * x_s ** 4 * I
        out /= c * (sigma ** 2 * x_s ** 6 + res ** 2)
        return out

    def _small_bubble_standing(self):
        E = self.cls.E_ac
        k = self.cls.k_f
        h = self.position
        F = self.F
        return - 4 * pi / k ** 2 * E * sin(2 * h) * F

    def M_n(self, n):
        B_n = self.cls.B_n(n)
        x_s = self.cls.x_s
        return (-1) ** n / (2 * n + 1) * B_n * Bf.besselj(n, x_s)

    def K_n(self, n):
        B_n = self.cls.B_n(n)
        k_s = self.cls.k_s
        x_s = self.cls.x_s
        return (-1) ** n / (2 * n + 1) * B_n * k_s * Bf.d1_besselj(n, x_s)

    def compute_arf(self):
        a = self.R_0
        rho = self.rho_f
        lamb = self.cls.lambda_rho
        k = self.cls.k_f
        s = 0
        for n in range(self.cls.N_max):
            s1 = (
                - 2 * pi * a ** 2 * rho * 2 * (n + 1)
                * (self.K_n(n) * conj(self.K_n(n + 1))).real / 2
            )
            s2 = (
                2 * pi * lamb ** 2 * rho * 2 * n * (n + 1) * (n + 2) *
                (self.M_n(n) * conj(self.M_n(n + 1))).real / 2
            )
            s3 = (
                -2 * pi * a * lamb * rho * 2 * (n + 1) * (n + 2) *
                (self.K_n(n) * conj(self.M_n(n + 1))).real / 2
                + 2 * pi * a * lamb * rho * 2 * n * (n + 1)
                * (self.M_n(n) * conj(self.K_n(n + 1))).real / 2
            )
            s4 = (
                - 2 * pi * k ** 2 * a ** 2 * lamb ** 2 * rho
                * 2 * (n + 1) *
                (self.M_n(n) * conj(self.M_n(n + 1))).real / 2
            )
            s += s1 + s2 + s3 + s4
        if self.cls.wave_type == WaveType.STANDING:
            return -s
        return s

    # -------------------------------------------------------------------------
    # Test
    # -------------------------------------------------------------------------

    def test_F(self) -> None:
        try:
            self.do_testing(
                func_1=lambda: self.F,
                func_2=lambda: self.cls.F,
            )
        except ValueError:
            pass

    def test_small_particle_solution(self):
        self.cls.small_particle = True
        self.do_testing(
            self.cls.compute_arf,
            self.small_particle_ARF,
        )

    def test_small_bubble_solution(self):
        self.cls.small_particle = True
        self.cls.bubble_solution = True
        self.do_testing(
            self.cls.compute_arf,
            self.small_particle_ARF,
        )

    def test_value_error_wrong_wavetype(self):
        self.cls.wave_type = 'wrong_wavetype'

        # Small Particle
        self.cls.small_particle = True
        self.assertRaises(
            WrongWaveTypeError,
            self.cls.compute_arf,
        )

        # Small Bubble
        self.cls.bubble_solution = True
        self.assertRaises(
            WrongWaveTypeError,
            self.cls.compute_arf,
        )

    def test_large_bubble_error(self):
        self.cls.bubble_solution = True
        self.cls.small_particle = False
        self.assertRaises(
            ValueError,
            self.cls.compute_arf,
        )

    def test_value_error_F(self):
        # Small Particle
        self.cls.bubble_solution = True
        self.cls.wave_type = WaveType.TRAVELLING
        self.assertRaises(WrongWaveTypeError, lambda: self.cls.F)

    def test_M_n(self):
        for n in range(self.n_runs):
            self.do_testing(self.cls.M_n, self.M_n, n, n)

    def test_K_n(self):
        for n in range(self.n_runs):
            self.do_testing(self.cls.K_n, self.K_n, n, n)

    def test_general_arf(self):
        self.do_testing(
            self.compute_arf,
            self.cls.compute_arf,
        )

    def test_run_large_particle_warning(self):
        self.cls.small_particle = True
        self.R_0 = 2 * pi * self.cls.fluid.lambda_f
        self.assign_parameters()
        self.cls.compute_arf()
        self.cls.bubble_solution = True
        self.assign_parameters()
        self.cls.compute_arf()


class TestCompareToKing(BaseTest, HelperCompareARF):

    def setUp(self) -> None:

        BaseTest.setUp(self)

        # Setting speed of sound in particle to be large
        self.c_s = 1e3 * self.c_f
        self._c_s.low = 1e3 * self.c_f

        self.arf_compare_threshold = 1e-4

        self.cls = yosioka1955.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
        )
        self.compare_cls = king1934.ARF(
            self.f,
            self.R_0, self.rho_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type,
            self.position,
        )

        self.list_cls = [self.cls, self.compare_cls]


class TestCompareToGorkov(BaseTest, HelperCompareARF):

    def setUp(self) -> None:

        BaseTest.setUp(self)

        self.arf_compare_threshold = 1e-3

        self.cls = yosioka1955.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
        )
        self.compare_cls = gorkov1962.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
        )

        # Setting size of the particle to be small
        self.R_0 = self.cls.fluid.lambda_f * 1e-4
        self._R_0.high = self.cls.fluid.lambda_f * 1e-3

        self.list_cls = [self.cls, self.compare_cls]


class TestCompareToSmallParticle(BaseTest, HelperCompareARF):

    def setUp(self) -> None:

        BaseTest.setUp(self)

        self.arf_compare_threshold = 5e-3

        self.cls = yosioka1955.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
        )
        self.compare_cls = yosioka1955.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position, small_particle=True,
        )

        # Setting size of the particle to be small
        self.R_0 = self.cls.fluid.lambda_f * 1e-4
        self._R_0.high = self.cls.fluid.lambda_f * 1e-3

        self.list_cls = [self.cls, self.compare_cls]


class TestCompareSmallBubble(BaseTest, HelperCompareARF):

    def setUp(self) -> None:
        BaseTest.setUp(self)

        self.arf_compare_threshold = 5e-3

        self.cls = yosioka1955.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
        )
        self.compare_cls = yosioka1955.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
            small_particle=True, bubble_solution=True,
        )

        # Setting size of the particle to be small
        self.R_0 = self.cls.fluid.lambda_f * 1e-4
        self._R_0.high = self.cls.fluid.lambda_f * 1e-3

        # Set density to be small inside to be small
        self.rho_s = self.cls.x_f ** 2 * self.rho_f
        self._rho_s.high = 1.1 * self.rho_s

        self.list_cls = [self.cls, self.compare_cls]


if __name__ == '__main__':
    unittest.main()
