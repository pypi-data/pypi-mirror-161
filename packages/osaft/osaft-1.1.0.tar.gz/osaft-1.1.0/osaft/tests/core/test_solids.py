import unittest

from osaft.core.frequency import Frequency
from osaft.core.functions import sqrt
from osaft.core.solids import ElasticSolid, RigidSolid
from osaft.tests.basetest import BaseTest


class TestConversion(unittest.TestCase):

    def setUp(self) -> None:
        self.rho = 8960
        self.c_1 = 4521.3
        self.c_2 = 2226.1

        self.E = 130e9
        self.nu = 0.34

        self.lam = 1.03e11
        self.G = 4.85e10

    def test_elastic_to_lame(self):
        lam = ElasticSolid.lambda_from_E_nu(self.E, self.nu)
        G = ElasticSolid.G_from_E_nu(self.E, self.nu)
        E_test = ElasticSolid.E_from_Lame(lam, G)
        nu_test = ElasticSolid.nu_from_Lame(lam, G)
        self.assertAlmostEqual(self.E, E_test)
        self.assertAlmostEqual(self.nu, nu_test)

    def test_lame_to_elastic(self):
        E = ElasticSolid.E_from_Lame(self.lam, self.G)
        nu = ElasticSolid.nu_from_Lame(self.lam, self.G)
        lam_test = ElasticSolid.lambda_from_E_nu(E, nu)
        G_test = ElasticSolid.G_from_E_nu(E, nu)
        self.assertAlmostEqual(self.lam, lam_test, delta=1)
        self.assertAlmostEqual(self.G, G_test, delta=1)

    def test_wave_speed_to_elastic(self):
        E = ElasticSolid.E_from_wave_speed(self.c_1, self.c_2, self.rho)
        nu = ElasticSolid.nu_from_wave_speed(self.c_1, self.c_2)
        c_1_test = ElasticSolid.c1_from_E_nu(E, nu, self.rho)
        c_2_test = ElasticSolid.c2_from_E_nu(E, nu, self.rho)
        self.assertAlmostEqual(self.c_1, c_1_test)
        self.assertAlmostEqual(self.c_2, c_2_test)

    def test_elastic_to_wave_speed(self):
        c_1 = ElasticSolid.c1_from_E_nu(self.E, self.nu, self.rho)
        c_2 = ElasticSolid.c2_from_E_nu(self.E, self.nu, self.rho)
        E_test = ElasticSolid.E_from_wave_speed(c_1, c_2, self.rho)
        nu_test = ElasticSolid.nu_from_wave_speed(c_1, c_2)
        self.assertAlmostEqual(self.E, E_test)
        self.assertAlmostEqual(self.nu, nu_test)

    def test_wave_speed_to_lame(self):
        lam = ElasticSolid.lambda_from_wave_speed(self.c_1, self.c_2, self.rho)
        G = ElasticSolid.G_from_wave_speed(self.c_2, self.rho)
        c_1_test = ElasticSolid.c1_from_Lame(lam, G, self.rho)
        c_2_test = ElasticSolid.c2_from_Lame(G, self.rho)
        self.assertAlmostEqual(self.c_1, c_1_test)
        self.assertAlmostEqual(self.c_2, c_2_test)

    def test_lame_to_wave_speed(self):
        c_1 = ElasticSolid.c1_from_Lame(self.lam, self.G, self.rho)
        c_2 = ElasticSolid.c2_from_Lame(self.G, self.rho)
        lam_test = ElasticSolid.lambda_from_wave_speed(c_1, c_2, self.rho)
        G_test = ElasticSolid.G_from_wave_speed(c_2, self.rho)
        self.assertAlmostEqual(self.lam, lam_test, delta=1)
        self.assertAlmostEqual(self.G, G_test, delta=1)


class TestRigidSolid(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.cls = RigidSolid(self.f, self.rho_s)
        self.composite_cls = RigidSolid(self.frequency, self.rho_s)
        self.list_cls = [self.cls, self.composite_cls]

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_properties(self):
        self.do_testing(lambda: self.rho_s, lambda: self.cls.rho_s)
        self.do_testing(
            lambda: self.cls.rho_s,
            lambda: self.composite_cls.rho_s,
        )

        self.do_testing(
            lambda: self.f,
            lambda: self.cls.f,
        )
        self.do_testing(
            lambda: self.cls.f,
            lambda: self.composite_cls.f,
        )


class TestElasticSolid(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.frequency = Frequency(self.f)
        self.cls = ElasticSolid(self.f, self.E_s, self.nu_s, self.rho_s)
        self.composite_cls = ElasticSolid(
            self.frequency, self.E_s, self.nu_s,
            self.rho_s,
        )
        self.list_cls = [self.cls, self.composite_cls]
    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def compute_G(self) -> float:
        return ElasticSolid.G_from_E_nu(self.E_s, self.nu_s)

    def compute_lambda(self) -> float:
        return ElasticSolid.lambda_from_E_nu(self.E_s, self.nu_s)

    def compute_B_s(self) -> float:
        return self.E_s / 3 / (1 - 2 * self.nu_s)

    def compute_kappa_s(self) -> float:
        return 3 * (1 - 2 * self.nu_s) / self.E_s

    def compute_c_l(self) -> float:
        return sqrt(
            self.E_s * (1 - self.nu_s)
            / (self.rho_s * (1 + self.nu_s) * (1 - 2 * self.nu_s)),
        )

    def compute_c_t(self) -> float:
        return sqrt(self.E_s / (2 * (1 + self.nu_s) * self.rho_s))

    def compute_k_l(self) -> float:
        omega = self.frequency.omega
        c_l = self.compute_c_l()
        return omega / c_l

    def compute_k_t(self) -> float:
        omega = self.frequency.omega
        c_t = self.compute_c_t()
        return omega / c_t

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_G(self) -> None:
        self.do_testing(
            func_1=self.compute_G,
            func_2=lambda: self.cls.G,
        )

    def test_lambe_2(self) -> None:
        self.do_testing(
            func_1=self.compute_G,
            func_2=lambda: self.cls.lame_2,
        )

    def test_lambda(self) -> None:
        self.do_testing(
            func_1=self.compute_lambda,
            func_2=lambda: self.cls.lame_1,
        )

    def test_c_l(self) -> None:
        self.do_testing(
            func_1=self.compute_c_l,
            func_2=lambda: self.cls.c_l,
        )
        self.do_testing(
            func_1=self.compute_c_l,
            func_2=lambda: self.composite_cls.c_l,
        )

    def test_c_t(self) -> None:
        self.do_testing(
            func_1=self.compute_c_t,
            func_2=lambda: self.cls.c_t,
        )
        self.do_testing(
            func_1=self.compute_c_t,
            func_2=lambda: self.composite_cls.c_t,
        )

    def test_k_l(self) -> None:
        self.do_testing(
            func_1=self.compute_k_l,
            func_2=lambda: self.cls.k_l,
        )
        self.do_testing(
            func_1=self.compute_k_l,
            func_2=lambda: self.composite_cls.k_l,
        )

    def test_k_t(self) -> None:
        self.do_testing(
            func_1=self.compute_k_t,
            func_2=lambda: self.cls.k_t,
        )
        self.do_testing(
            func_1=self.compute_k_t,
            func_2=lambda: self.composite_cls.k_t,
        )

    def test_kappa_s(self) -> None:
        self.do_testing(
            func_1=self.compute_kappa_s,
            func_2=lambda: self.cls.kappa_s,
        )
        self.do_testing(
            func_1=self.compute_kappa_s,
            func_2=lambda: self.composite_cls.kappa_s,
        )

    def test_B_s(self) -> None:
        self.do_testing(
            func_1=self.compute_B_s,
            func_2=lambda: self.cls.B_s,
        )
        self.do_testing(
            func_1=self.compute_B_s,
            func_2=lambda: self.composite_cls.B_s,
        )


if __name__ == '__main__':
    unittest.main()
