import unittest

from osaft.core.functions import BesselFunctions as Bf
from osaft.solutions.doinikov1994compressible.scattering import ScatteringField
from osaft.tests.basetest import BaseTest


class TestCoefficientMatrix(BaseTest):

    def setUp(self) -> None:
        super().setUp()

        self._v_particle_threshold = 1e-5
        self._v_fluid_threshold = 1e-3
        self._v_boundary_conditions = 1e-10

        self.cls = ScatteringField(
            self.f, self.R_0,
            self.rho_s, self.c_s,
            self.eta_p, self.zeta_p,
            self.rho_f, self.c_f,
            self.eta_f, self.zeta_f,
            self.p_0, self.wave_type,
            self.position,
        )

    @property
    def x(self):
        return self.cls.x

    @property
    def x_v(self):
        return self.cls.x_v

    @property
    def x_hat(self):
        return self.cls.x_hat

    @property
    def x_hat_v(self):
        return self.cls.x_hat_v

    def test_matrix_coefficients(self) -> None:

        for k in range(1, 5):
            for l in range(1, 5):
                for n in range(3):
                    with self.subTest(msg=f'M_{k}{l}', n=n):
                        func_1 = getattr(self, f'm_{k}{l}')
                        func_2 = getattr(self, f'cls_m_{k}{l}')
                        self.do_testing(func_1, func_2, n, n, 1e-6)

    def test_vector_coefficients(self):
        for k in range(1, 5):
            for n in range(3):
                with self.subTest(msg=f'N_{k}', n=n):
                    func_1 = getattr(self, f'n_{k}')
                    func_2 = getattr(self, f'cls_n_{k}')
                    self.do_testing(func_1, func_2, n, n, 1e-6)

    # ------------------
    # testing m_1i
    # ------------------

    def cls_m_11(self, n: int) -> complex:
        return self.cls.M(n)[0, 0]

    def m_11(self, n: int) -> complex:
        out = self.x * Bf.d1_hankelh1(n, self.x)
        return out

    def cls_m_12(self, n: int) -> complex:
        return self.cls.M(n)[0, 1]

    def m_12(self, n: int) -> complex:
        out = -n * (n + 1) * Bf.hankelh1(n, self.x_v)
        return out

    def cls_m_13(self, n: int) -> complex:
        return self.cls.M(n)[0, 2]

    def m_13(self, n: int) -> complex:
        out = -self.x_hat * Bf.d1_besselj(n, self.x_hat)
        return out

    def cls_m_14(self, n: int) -> complex:
        return self.cls.M(n)[0, 3]

    def m_14(self, n: int) -> complex:
        out = n * (n + 1) * Bf.besselj(n, self.x_hat_v)
        return out

    # ------------------
    # testing m_2i
    # ------------------

    def cls_m_21(self, n: int) -> complex:
        return self.cls.M(n)[1, 0]

    def m_21(self, n: int) -> complex:
        out = Bf.hankelh1(n, self.x)
        return out

    def cls_m_22(self, n: int) -> complex:
        return self.cls.M(n)[1, 1]

    def m_22(self, n: int) -> complex:
        out = -Bf.hankelh1(n, self.x_v)
        out -= self.x_v * Bf.d1_hankelh1(n, self.x_v)
        return out

    def cls_m_23(self, n: int) -> complex:
        return self.cls.M(n)[1, 2]

    def m_23(self, n: int) -> complex:
        out = -Bf.besselj(n, self.x_hat)
        return out

    def cls_m_24(self, n: int) -> complex:
        return self.cls.M(n)[1, 3]

    def m_24(self, n: int) -> complex:
        out = Bf.besselj(n, self.x_hat_v)
        out += self.x_hat_v * Bf.d1_besselj(n, self.x_hat_v)
        return out

    # ------------------
    # testing m_3i
    # ------------------

    def cls_m_31(self, n: int) -> complex:
        return self.cls.M(n)[2, 0]

    def m_31(self, n: int) -> complex:
        out = 1j * self.cls.rho_f * self.cls.c_f ** 2 / self.cls.omega
        out += self.cls.zeta_f
        out -= 2 * self.cls.eta_f / 3
        out *= -Bf.hankelh1(n, self.x)

        out += 2 * self.cls.eta_f * Bf.d2_hankelh1(n, self.x)

        out *= self.x ** 2

        return out

    def cls_m_32(self, n: int) -> complex:
        return self.cls.M(n)[2, 1]

    def m_32(self, n: int) -> complex:
        out = Bf.hankelh1(n, self.x_v)
        out -= self.x_v * Bf.d1_hankelh1(n, self.x_v)

        out *= 2 * n * (n + 1) * self.cls.eta_f
        return out

    def cls_m_33(self, n: int) -> complex:
        return self.cls.M(n)[2, 2]

    def m_33(self, n: int) -> complex:
        out = 1j * self.cls.rho_s * self.cls.c_s ** 2 / self.cls.omega
        out += self.cls.zeta_s
        out -= 2 * self.cls.eta_s / 3
        out *= Bf.besselj(n, self.x_hat)

        out -= 2 * self.cls.eta_s * Bf.d2_besselj(n, self.x_hat)

        out *= self.x_hat ** 2
        return out

    def cls_m_34(self, n: int) -> complex:
        return self.cls.M(n)[2, 3]

    def m_34(self, n: int) -> complex:
        out = -Bf.besselj(n, self.x_hat_v)
        out += self.x_hat_v * Bf.d1_besselj(n, self.x_hat_v)

        out *= 2 * n * (n + 1) * self.cls.eta_s
        return out

    # ------------------
    # testing m_4i
    # ------------------

    def cls_m_41(self, n: int) -> complex:
        return self.cls.M(n)[3, 0]

    def m_41(self, n: int) -> complex:
        out = self.x * Bf.d1_hankelh1(n, self.x)
        out -= Bf.hankelh1(n, self.x)

        out *= 2 * self.cls.eta_f

        return out

    def cls_m_42(self, n: int) -> complex:
        return self.cls.M(n)[3, 1]

    def m_42(self, n: int) -> complex:
        out = (n ** 2 + n - 2) * Bf.hankelh1(n, self.x_v)

        out += self.x_v ** 2 * Bf.d2_hankelh1(n, self.x_v)

        out *= -self.cls.eta_f
        return out

    def cls_m_43(self, n: int) -> complex:
        return self.cls.M(n)[3, 2]

    def m_43(self, n: int) -> complex:
        out = Bf.besselj(n, self.x_hat)
        out -= self.x_hat * Bf.d1_besselj(n, self.x_hat)

        out *= 2 * self.cls.eta_s
        return out

    def cls_m_44(self, n: int) -> complex:
        return self.cls.M(n)[3, 3]

    def m_44(self, n: int) -> complex:
        out = (n ** 2 + n - 2) * Bf.besselj(n, self.x_hat_v)

        out += self.x_hat_v ** 2 * Bf.d2_besselj(n, self.x_hat_v)

        out *= self.cls.eta_s
        return out

    # ------------------
    # testing n_i
    # ------------------

    def cls_n_1(self, n: int) -> complex:
        return self.cls.N(n)[0]

    def n_1(self, n: int) -> complex:
        out = -self.x * Bf.d1_besselj(n, self.x)
        return out

    def cls_n_2(self, n: int) -> complex:
        return self.cls.N(n)[1]

    def n_2(self, n: int) -> complex:
        out = -Bf.besselj(n, self.x)
        return out

    def cls_n_3(self, n: int) -> complex:
        return self.cls.N(n)[2]

    def n_3(self, n: int) -> complex:
        out = 1j * self.cls.rho_f * self.cls.c_f ** 2 / self.cls.omega
        out += self.cls.zeta_f
        out -= 2 * self.cls.eta_f / 3
        out *= Bf.besselj(n, self.x)
        out -= 2 * self.cls.eta_f * Bf.d2_besselj(n, self.x)
        out *= self.x ** 2

        return out

    def cls_n_4(self, n: int) -> complex:
        return self.cls.N(n)[3]

    def n_4(self, n: int) -> complex:
        out = Bf.besselj(n, self.x)
        out -= self.x * Bf.d1_besselj(n, self.x)
        out *= 2 * self.cls.eta_f
        return out

    if __name__ == '__main__':
        unittest.main()
