import unittest

import osaft
from osaft import WaveType, hasegawa1969, yosioka1955
from osaft.core.functions import BesselFunctions as Bf
from osaft.tests.basetest import BaseTest
from osaft.tests.basetest_arf import HelperCompareARF


class TestARF(BaseTest):

    def setUp(self) -> None:
        super().setUp()

        self.N_max = 5

        self.cls = hasegawa1969.ARF(
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

    def U_n(self, n):
        cn = self.cls.c_n(n)
        x = self.cls.x_f
        j = Bf.besselj(n, x)
        n = Bf.bessely(n, x)
        return (1 + cn.real) * j + cn.imag * n

    def V_n(self, n):
        cn = self.cls.c_n(n)
        x = self.cls.x_f
        j = Bf.besselj(n, x)
        n = Bf.bessely(n, x)
        return cn.imag * j - cn.real * n

    def U_n_d1(self, n):
        cn = self.cls.c_n(n)
        x = self.cls.x_f
        dj = Bf.d1_besselj(n, x)
        dn = Bf.d1_bessely(n, x)
        return (1 + cn.real) * dj + cn.imag * dn

    def V_n_d1(self, n):
        cn = self.cls.c_n(n)
        x = self.cls.x_f
        dj = Bf.d1_besselj(n, x)
        dn = Bf.d1_bessely(n, x)
        return cn.imag * dj - cn.real * dn

    def _compute_arf(self):
        s = 0
        for n in range(self.cls.N_max):
            s1 = (
                - self.cls.x_f ** 2 * (n + 1) * (
                    self.U_n_d1(n) * self.V_n_d1(n + 1)
                    - self.V_n_d1(n) * self.U_n_d1(n + 1)
                )
            )
            s2 = (
                n * (n + 1) * (n + 2) * (
                    self.U_n(n) * self.V_n(n + 1)
                    - self.V_n(n) * self.U_n(n + 1)
                )
            )
            s3 = (
                self.cls.x_f * n * (n + 1) * (
                    self.U_n(n) * self.V_n_d1(n + 1)
                    - self.V_n(n) * self.U_n_d1(n + 1)
                )
            )
            s4 = (
                - self.cls.x_f * (n + 1) * (n + 2) * (
                    self.U_n_d1(n) * self.V_n(n + 1)
                    - self.V_n_d1(n) * self.U_n(n + 1)
                )
            )
            s5 = (
                - self.cls.x_f ** 2 * (n + 1) * (
                    self.U_n(n) * self.V_n(n + 1)
                    - self.V_n(n) * self.U_n(n + 1)
                )
            )
            s += s1 + s2 + s3 + s4 + s5

        s *= 2 * osaft.pi * self.rho_f * abs(self.cls.field.A) ** 2
        return s

    def _compute_arf_standing(self):
        s = 0
        for n in range(self.cls.N_max):
            s1 = (
                - self.cls.x_f ** 2 * (n + 1) * (-1) ** (n + 1) * (
                    self.U_n_d1(n) * self.U_n_d1(n + 1)
                    + self.V_n_d1(n) * self.V_n_d1(n + 1)
                )
            )
            s2 = (
                n * (n + 1) * (n + 2) * (-1) ** (n + 1) * (
                    self.U_n(n) * self.U_n(n + 1)
                    + self.V_n(n) * self.V_n(n + 1)
                )
            )
            s3 = (
                self.cls.x_f * n * (n + 1) * (-1) ** (n + 1) * (
                    self.U_n(n) * self.U_n_d1(n + 1)
                    + self.V_n(n) * self.V_n_d1(n + 1)
                )
            )
            s4 = (
                - self.cls.x_f * (n + 1) * (n + 2) * (-1) ** (n + 1) * (
                    self.U_n_d1(n) * self.U_n(n + 1)
                    + self.V_n_d1(n) * self.V_n(n + 1)
                )
            )
            s5 = (
                - self.cls.x_f ** 2 * (n + 1) * (-1) ** (n + 1) * (
                    self.U_n(n) * self.U_n(n + 1)
                    + self.V_n(n) * self.V_n(n + 1)
                )
            )
            s += s1 + s2 + s3 + s4 + s5

        s *= (
            1 * osaft.pi * self.rho_f * self.cls.field.A ** 2
            * osaft.core.functions.sin(
                2 * self.cls.position / self.cls.k_f.real * self.cls.k_f,
            )
        )
        return -s.real

    def compute_arf(self):
        self.cls.check_wave_type()
        if self.cls.wave_type == WaveType.STANDING:
            return self._compute_arf_standing()
        else:
            return self._compute_arf()

    def _compute_arf_from_Yp(self) -> float:
        """
        Computes general analytical solution for the
        acoustic radiation force function.
        Replace in compute_arf to use for simple plotting.
        Used to recreate figures that are in the paper.
        (Eq. 29)
        """
        out = 4 * [0]

        for n in range(self.N_max):
            # (29, first row)
            s1 = (self.V_n_d1(n) * self.U_n_d1(n + 1))
            s1 -= (self.U_n_d1(n) * self.V_n_d1(n + 1))
            s1 *= n + 1
            out[0] += s1

            # (29, second row)
            s2 = (self.V_n(n) * self.U_n(n + 1))
            s2 -= (self.U_n(n) * self.V_n(n + 1))
            s2 *= n * (n + 1) * (n + 2)
            out[1] += s2

            # (29, third and fourth row)
            s3 = (self.U_n(n) * self.V_n_d1(n + 1))
            s3 -= (self.V_n(n) * self.U_n_d1(n + 1))
            s3 *= n * (n + 1)
            s4 = (self.U_n_d1(n) * self.V_n(n + 1))
            s4 -= (self.V_n_d1(n) * self.U_n(n + 1))
            s4 *= (n + 1) * (n + 2)
            out[2] += s3
            out[2] -= s4
            # (29, last row)
            s5 = (self.V_n(n) * self.U_n(n + 1))
            s5 -= (self.U_n(n) * self.V_n(n + 1))
            s5 *= n + 1
            out[3] += s5

        out[0] *= self.cls.x_f ** 2
        out[1] *= -1
        out[2] *= self.cls.x_f
        out[3] *= self.cls.x_f ** 2

        out = 4 / (self.cls.x_f ** 2) * sum(out)
        E = .5 * self.cls.rho_f * self.cls.k_f ** 2 * self.cls.field.A ** 2
        out *= osaft.pi * self.cls.R_0 ** 2 * E
        return -out

    def _compute_arf_from_Yp_standing(self) -> float:
        """
        Computes general analytical solution for the
        acoustic radiation force function, standing wave case.
        Replace in compute_arf to use for simple plotting.
        Used to recreate figures that are in the paper.
        (Eq. 19 in 1979 paper)
        """
        out = 0
        for n in range(self.N_max):
            out += (
                2 * (n + 1) * (-1) ** (n + 1) * (
                    self.cls.c_n(n).imag * (1 + 2 * self.cls.c_n(n + 1).real)
                    - self.cls.c_n(n + 1).imag * (1 + 2 * self.cls.c_n(n).real)
                ) / self.cls.x_f ** 2
            )

        # (Eq. 29)
        E = .5 * self.cls.rho_f * self.cls.k_f ** 2 * self.cls.field.A ** 2
        sin = osaft.core.functions.sin(
            2 * self.position / self.cls.k_f.real * self.cls.k_f,
        )
        out *= osaft.pi * self.cls.R_0 ** 2 * E * sin
        return out.real

    def compute_arf_from_Yp(self) -> float:
        """
        Acoustic radiation force function [-]

        Computes the radiation force function based on (29, Hasegawa1969) and
        (19, Hasegawa1979).
        To check if the functions are implemented correctly, as you can
        compare to the figures in the paper.

        :raises WrongWaveTypeError: if wrong :attr:`wave_type`
        """

        # Checking wave_type
        self.cls.check_wave_type()

        if self.wave_type == WaveType.STANDING:
            return self._compute_arf_from_Yp_standing()
        else:
            return self._compute_arf_from_Yp()

    # -------------------------------------------------------------------------
    # Test
    # -------------------------------------------------------------------------

    def test_U_n(self):
        for n in range(self.n_runs):
            self.do_testing(self.cls.U_n, self.U_n, n, n)

    def test_V_n(self):
        for n in range(self.n_runs):
            self.do_testing(self.cls.V_n, self.V_n, n, n)

    def test_U_n_d1(self):
        for n in range(self.n_runs):
            self.do_testing(self.cls.d_U_n, self.U_n_d1, n, n)

    def test_V_n_d1(self):
        for n in range(self.n_runs):
            self.do_testing(self.cls.d_V_n, self.V_n_d1, n, n)

    def test_arf(self):
        self.do_testing(
            self.compute_arf,
            self.cls.compute_arf,
        )

    def test_arf_from_Yp(self):
        self.do_testing(
            self.compute_arf_from_Yp,
            self.cls.compute_arf,
        )


class TestCompareToYosioka(BaseTest, HelperCompareARF):

    def setUp(self) -> None:

        BaseTest.setUp(self)

        self.arf_compare_threshold = 5e-3

        self.cls = hasegawa1969.ARF(
            self.f, self.R_0,
            self.rho_s, self.E_s, self.nu_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
        )
        self.compare_cls = yosioka1955.ARF(
            self.f, self.R_0,
            self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0, self.wave_type, self.position,
        )

        self.test_variables.remove(self._rho_s)
        self.test_variables.remove(self._E_s)
        self.test_variables.remove(self._nu_s)
        self.test_variables.remove(self._c_s)

        self._R_0.low = 1e-6
        self._R_0.high = 5e-6

        self.cls.E_s = (
            3 * (1 - 2 * self.nu_s) /
            self.compare_cls.scatterer.kappa_f
        )

        self.list_cls = [self.cls, self.compare_cls]


if __name__ == '__main__':
    unittest.main()
