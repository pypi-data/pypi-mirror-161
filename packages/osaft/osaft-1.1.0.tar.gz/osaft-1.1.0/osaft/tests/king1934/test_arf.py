import unittest
from enum import auto

import numpy as np

from osaft import WaveType, gorkov1962, king1934
from osaft.core.backgroundfields import WrongWaveTypeError
from osaft.core.functions import pi, sin
from osaft.tests.basetest_arf import HelperCompareARF
from osaft.tests.king1934.test_base import BaseKing


class TestARF(BaseKing):

    def setUp(self) -> None:
        super().setUp()

        self.small_particle_limit = False
        self.cls = king1934.ARF(
            self.f, self.R_0, self.rho_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type,
            self.position,
            self.small_particle_limit,
        )
        self.list_cls = [self.cls]

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def f_2(self):
        rho_tilde = self.rho_s / self.rho_f
        return 2 * (rho_tilde - 1) / (2 * rho_tilde + 1)

    @property
    def Phi(self):
        if self.wave_type == WaveType.TRAVELLING:
            return self.compute_Phi_traveling()
        elif self.wave_type == WaveType.STANDING:
            return self.compute_Phi_standing()

    def compute_Phi_standing(self):
        return 1 / 3 + self.f_2 / 2

    def compute_Phi_traveling(self):
        rho_tilde = self.rho_s / self.rho_f
        return (
            (1 + 2 / 9 * (1 - 1 / rho_tilde) ** 2)
            / (2 + 1 / rho_tilde) ** 2
        )

    def FFGG(self, n):
        alpha = self.cls.alpha
        out = self.F_n(n, alpha) * self.F_n(n + 1, alpha)
        out += self.G_n(n, alpha) * self.G_n(n + 1, alpha)
        return out

    def FGFG(self, n):
        alpha = self.cls.alpha
        out = self.F_n(n + 1, alpha)
        out *= self.G_n(n, alpha)
        out -= self.G_n(n + 1, alpha) * self.F_n(n, alpha)
        return out

    def HH(self, n):
        out = self.cls.alpha**2
        if n == 1:
            out -= 3 * (1 - 1 / self.cls.rho_tilde)
        else:
            out -= n * (n + 2)
        out = out**2
        out /= self.cls.alpha**(4 * n + 6)
        out += self.FFGG(n)**2
        return out

    def compute_general_ARF(self):
        if self.wave_type == WaveType.TRAVELLING:
            return self.compute_traveling_general_ARF()
        elif self.wave_type == WaveType.STANDING:
            return self.compute_standing_general_ARF()

    def compute_standing_general_ARF(self):
        alpha = self.cls.alpha
        # n = 0
        out = self.FFGG(0)
        out /= self.HH(0)
        out /= alpha
        # n = 1
        tmp = 2 / alpha**5
        tmp *= self.FFGG(1)
        tmp /= self.HH(1)
        tmp *= alpha**2 - 3 * (1 - 1 / self.cls.rho_tilde)
        out -= tmp
        # n > 1
        for i in range(2, self.cls.N_max):
            tmp = (-1)**i
            tmp *= (i + 1) / alpha**(2 * i + 3)
            tmp *= self.FFGG(i)
            tmp /= self.HH(i)
            tmp *= alpha**2 - i * (i + 2)

            out += tmp

        out *= pi * self.cls.rho_f
        out *= np.abs(self.cls.field.A)**2
        out *= sin(2 * self.position)

        return out

    def compute_traveling_general_ARF(self):
        alpha = self.cls.alpha
        # n = 0
        out = 1 / self.HH(0)
        # n = 1
        tmp = 2 / self.HH(1)
        tmp *= (alpha**2 - 3 * (1 - 1 / self.cls.rho_tilde))**2
        tmp /= alpha**8
        out += tmp
        # n > 1
        for i in range(2, self.cls.N_max):
            tmp = (i + 1) / self.HH(i)
            tmp *= (alpha**2 - i * (i + 2))**2
            tmp /= alpha**(4 * i + 4)
            out += tmp

        out *= 2 * pi * self.cls.rho_f
        out *= np.abs(self.cls.field.A)**2 / alpha**2

        return out

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_properties(self) -> None:
        properties = ['Phi', 'f_2']
        self._test_properties(properties)

    def test_methods_n(self) -> None:
        dict_method = {}
        dict_method['FGFG'] = None
        dict_method['FFGG'] = None
        dict_method['HH'] = None

        self._test_methods_n(dict_method)

    # -------------------------------------------------------------------------
    # Test ARF
    # -------------------------------------------------------------------------

    def test_general_solution(self) -> None:
        for n in range(0, self.n_runs + 3):
            self.do_testing(
                func_1=self.cls.compute_arf,
                func_2=self.compute_general_ARF,
                threshold=5e-4,
            )

    def test_NotImplemented_solution(self) -> None:
        WaveType.WRONGWAVETYPE = auto()
        self.cls.wave_type = WaveType.WRONGWAVETYPE
        self.assertRaises(WrongWaveTypeError, self.cls.compute_arf)

    def test_not_small_particle(self):
        # This method is not actually testing, only for coverage
        self.cls.R_0 = self.cls.fluid.lambda_f
        self.cls.small_particle_limit = True
        self.cls.compute_arf()


class TestCompareToGorkov(BaseKing, HelperCompareARF):

    def setUp(self) -> None:

        super().setUp()

        self.R_0 = 1e-7
        self._R_0.high = 1e-6

        self.c_s = 1e10
        self._c_s.low = 1e9

        self.arf_compare_threshold = 1e-4

        self.cls = king1934.ARF(
            self.f,
            self.R_0, self.rho_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
            small_particle_limit=False,
        )

        self.compare_cls = gorkov1962.ARF(
            self.f,
            self.R_0, self.rho_s,
            self.c_s, self.rho_f, self.c_f,
            self.p_0, self.wave_type,
            self.position,
        )

        self.list_cls = [self.cls, self.compare_cls]


class TestCompareToKing(HelperCompareARF, BaseKing):

    def setUp(self) -> None:

        BaseKing.setUp(self)

        self.R_0 = 1e-7
        self._R_0.high = 1e-6

        self.arf_compare_threshold = 1e-4

        self.small_particle_limit = True

        self.cls = king1934.ARF(
            self.f,
            self.R_0, self.rho_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
            small_particle_limit=True,
        )
        self.compare_cls = king1934.ARF(
            self.f,
            self.R_0, self.rho_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type,
            self.position,
            small_particle_limit=False,
        )

        self.list_cls = [self.cls, self.compare_cls]


if __name__ == '__main__':
    unittest.main()
