import unittest

from osaft.core.fluids import InviscidFluid, ViscoelasticFluid, ViscousFluid
from osaft.core.frequency import Frequency
from osaft.core.functions import pi, sqrt
from osaft.tests.basetest import BaseTest


class TestInviscidFluid(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.cls = InviscidFluid(
            self.f,
            self.rho_f,
            self.c_f,
        )
        self.composite_cls = InviscidFluid(
            self.frequency,
            self.rho_f, self.c_f,
        )

        self.list_cls = [self.cls, self.composite_cls]

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def compute_k_f(self) -> float:
        omega = self.frequency.omega
        c_f = self.c_f
        return omega / c_f

    def compute_kappa_f(self) -> float:
        return 1 / self.c_f**2 / self.rho_f

    def compute_lambda_f(self) -> float:
        return self.c_f / self.f

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_omega(self) -> None:
        self.do_testing(
            func_1=lambda: self.frequency.omega,
            func_2=lambda: self.cls.omega,
        )
        self.do_testing(
            func_1=lambda: self.frequency.omega,
            func_2=lambda: self.composite_cls.omega,
        )

    def test_k_f(self) -> None:
        self.do_testing(
            func_1=self.compute_k_f,
            func_2=lambda: self.cls.k_f,
        )
        self.do_testing(
            func_1=self.compute_k_f,
            func_2=lambda: self.composite_cls.k_f,
        )

    def test_lambda_f(self) -> None:
        self.do_testing(
            func_1=self.compute_lambda_f,
            func_2=lambda: self.cls.lambda_f,
        )
        self.do_testing(
            func_1=self.compute_lambda_f,
            func_2=lambda: self.composite_cls.lambda_f,
        )

    def test_kappa_f(self) -> None:
        self.do_testing(
            func_1=self.compute_kappa_f,
            func_2=lambda: self.cls.kappa_f,
        )
        self.do_testing(
            func_1=self.compute_kappa_f,
            func_2=lambda: self.composite_cls.kappa_f,
        )


class TestViscousFluid(TestInviscidFluid):

    def setUp(self) -> None:

        BaseTest.setUp(self)

        self.cls = ViscousFluid(
            self.f, self.rho_f, self.c_f,
            self.eta_f, self.zeta_f,
        )
        self.composite_cls = ViscousFluid(
            self.frequency,
            self.rho_f, self.c_f,
            self.eta_f, self.zeta_f,
        )
        self.cls_inviscid = InviscidFluid(
            self.f, self.rho_f,
            self.c_f,
        )

        self.list_cls = [self.cls, self.composite_cls, self.cls_inviscid]

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def compute_k_f(self) -> complex:

        omega = self.cls.omega
        c = self.c_f
        rho = self.rho_f
        eta = self.eta_f
        zeta = self.zeta_f
        return omega / c / sqrt(
            1 - 1j * omega / (rho * c**2)
            * (zeta + 4 * eta / 3),
        )

    def compute_k_v(self) -> complex:
        omega = self.cls.omega
        eta = self.eta_f
        rho = self.rho_f
        return (1 + 1j) * sqrt(rho * omega / (2 * eta))

    def compute_delta(self) -> complex:
        return 1 / self.compute_k_v().imag

    def compute_lambda_v(self) -> complex:
        return 2 * pi / self.compute_k_v().real

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_delta(self) -> None:
        self.do_testing(
            func_1=self.compute_delta,
            func_2=lambda: self.cls.delta,
        )
        self.do_testing(
            func_1=self.compute_delta,
            func_2=lambda: self.composite_cls.delta,
        )

    def test_delta_inviscid(self) -> None:
        self.cls.eta_f = 0
        self.assertEqual(self.cls.delta, 0)

    def test_lambda_v(self) -> None:
        self.do_testing(
            func_1=self.compute_lambda_v,
            func_2=lambda: self.cls.lambda_v,
        )
        self.do_testing(
            func_1=self.compute_lambda_v,
            func_2=lambda: self.composite_cls.lambda_v,
        )

    def test_lambda_v_inviscid(self) -> None:
        self.cls.eta_f = 0
        self.assertEqual(self.cls.lambda_v, 0)

    def test_k_v(self) -> None:
        self.do_testing(
            func_1=self.compute_k_v,
            func_2=lambda: self.cls.k_v,
        )
        self.do_testing(
            func_1=self.compute_k_v,
            func_2=lambda: self.composite_cls.k_v,
        )

    def test_k_v_inviscid(self) -> None:
        self.cls.eta_f = 0
        self.assertEqual(self.cls.k_v, 0)

    def test_k_f_inviscid(self):
        self.cls.eta_f = 0
        self.cls.zeta_f = 0
        self.assertAlmostEqual(self.cls.k_f, self.cls_inviscid.k_f)


class TestViscoelasticFluid(TestViscousFluid):

    def setUp(self) -> None:

        BaseTest.setUp(self)

        self.frequency = Frequency(self.f)
        self.cls = ViscoelasticFluid(
            self.f, self.rho_f,
            self.c_f,
            self.eta_f, self.eta_p,
            self.zeta_f, self.zeta_p,
            self.lambda_M,
        )

        self.composite_cls = ViscoelasticFluid(
            self.frequency,
            self.rho_f,
            self.c_f,
            self.eta_f,
            self.eta_p,
            self.zeta_f,
            self.zeta_p,
            self.lambda_M,
        )

        self.cls_inviscid = InviscidFluid(
            self.f, self.rho_f,
            self.c_f,
        )

        self.list_cls = [self.cls, self.composite_cls, self.cls_inviscid]

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def compute_eta_c(self):
        omega = self.cls.omega
        eta_f = self.eta_f
        eta_p = self.eta_p
        lambda_M = self.lambda_M
        return eta_f + eta_p / (1 - 1j * omega * lambda_M)

    def compute_zeta_c(self):
        omega = self.cls.omega
        zeta_f = self.zeta_f
        zeta_p = self.zeta_p
        lambda_M = self.lambda_M
        return zeta_f + zeta_p / (1 - 1j * omega * lambda_M)

    def compute_k_f(self) -> complex:
        omega = self.cls.omega
        c = self.c_f
        rho = self.rho_f
        eta = self.compute_eta_c()
        zeta = self.compute_zeta_c()
        return omega / c / sqrt(
            1 - 1j * omega / (rho * c**2)
            * (zeta + 4 * eta / 3),
        )

    def compute_k_v(self) -> complex:
        omega = self.cls.omega
        eta = self.compute_eta_c()
        rho = self.rho_f
        out = (1 + 1j) * sqrt(rho * omega / (2 * eta))
        return out

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_eta_c(self):
        self.do_testing(
            func_1=self.compute_eta_c,
            func_2=lambda: self.cls.eta_c,
        )
        self.do_testing(
            func_1=self.compute_eta_c,
            func_2=lambda: self.composite_cls.eta_c,
        )

    def test_zeta_c(self):
        self.do_testing(
            func_1=self.compute_zeta_c,
            func_2=lambda: self.cls.zeta_c,
        )
        self.do_testing(
            func_1=self.compute_zeta_c,
            func_2=lambda: self.composite_cls.zeta_c,
        )

    def test_k_v_inviscid(self) -> None:
        self.cls.eta_f = 0
        self.cls.eta_p = 0
        self.assertEqual(self.cls.k_v, 0)

    def test_delta_inviscid(self) -> None:
        self.cls.eta_f = 0
        self.cls.eta_p = 0
        self.assertEqual(self.cls.delta, 0)

    def test_lambda_v_inviscid(self) -> None:
        self.cls.eta_f = 0
        self.cls.eta_p = 0
        self.assertEqual(self.cls.lambda_v, 0)

    def test_k_f_inviscid(self):
        self.cls.eta_f = 0
        self.cls.zeta_f = 0
        self.cls.eta_p = 0
        self.cls.zeta_p = 0
        self.assertAlmostEqual(self.cls.k_f, self.cls_inviscid.k_f)


if __name__ == '__main__':
    unittest.main()
