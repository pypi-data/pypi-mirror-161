import unittest

from osaft import gorkov1962, settnes2012
from osaft.core.backgroundfields import WrongWaveTypeError
from osaft.core.functions import pi, sin
from osaft.tests.basetest import BaseTest
from osaft.tests.basetest_arf import (
    HelperCompareARF,
    HelperStandingARF,
    HelperTravelingARF,
)


class TestSettnes(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.cls = settnes2012.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f, self.eta_f,
            self.p_0, self.wave_type, self.position,
        )

        self.list_cls = [self.cls]

    # ------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------

    @property
    def f_1(self) -> float:
        return 1 - self.cls.kappa_s / self.cls.kappa_f

    @property
    def f_2(self) -> complex:
        return (
            2 * (1 - self.gamma) * (self.rho_t - 1) /
            (2 * self.rho_t + 1 - 3 * self.gamma)
        )

    @property
    def delta_t(self) -> float:
        return self.cls.delta / self.R_0

    @property
    def gamma(self) -> complex:
        return (
            -3 / 2 * (1 + 1j * (1 + self.delta_t)) *
            self.delta_t
        )

    @property
    def kappa_t(self) -> float:
        return self.cls.kappa_s / self.cls.kappa_f

    @property
    def rho_t(self) -> float:
        return self.rho_s / self.rho_f

    @property
    def Phi(self) -> float:
        return self.f_1 / 3 + self.f_2.real / 2

    # ------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------

    def test_properties(self) -> None:
        properties = [
            'f_1', 'f_2', 'delta_t', 'gamma', 'kappa_t', 'rho_t',
            'Phi',
        ]
        self._test_properties(properties)

    def test_wrong_wavetype(self):
        self.cls.wave_type = 'wrong_wave_type'
        self.assertRaises(
            WrongWaveTypeError,
            self.cls.compute_arf,
        )

    def test_not_small_particle(self):
        # This method is not actually testing, only for coverage
        self.cls.R_0 = self.cls.fluid.lambda_f
        self.cls.compute_arf()


class TestCompareToGorkov(BaseTest, HelperCompareARF):

    def setUp(self):
        super().setUp()

        self.arf_compare_threshold = 1e-4
        self.eta_f = 0

        self.cls = settnes2012.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f, self.eta_f,
            self.p_0, self.wave_type, self.position,
        )

        self.compare_cls = gorkov1962.ARF(
            self.f,
            self.R_0, self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type,
            self.position,
        )

        self.list_cls = [self.cls, self.compare_cls]


class TestStanding(TestSettnes, HelperStandingARF):

    def compute_arf(self) -> float:
        return (
            4 * pi * self.Phi * self.R_0**3 * self.cls.k_f.real
            * self.cls.E_ac
            * sin(2 * self.position)
        )


class TestTraveling(TestSettnes, HelperTravelingARF):

    def compute_arf(self) -> float:
        return (
            pi * self.R_0**3 * self.cls.k_f.real
            * self.f_2.imag * self.cls.E_ac
        )


if __name__ == '__main__':
    unittest.main()
