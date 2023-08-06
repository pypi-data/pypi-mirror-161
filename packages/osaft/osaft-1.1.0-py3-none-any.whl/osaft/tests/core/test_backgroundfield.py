import unittest

import numpy as np

from osaft.core.backgroundfields import (
    BackgroundField,
    WaveType,
    WrongWaveTypeError,
)
from osaft.core.fluids import InviscidFluid, ViscoelasticFluid, ViscousFluid
from osaft.core.functions import exp, pi
from osaft.tests.basetest import BaseTest


class TestBackgroundFieldWrappers(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.pi = pi

        self.inviscid = InviscidFluid(
            self.f, self.rho_f,
            self.c_f,
        )

        self.viscous = ViscousFluid(
            self.f,
            self.rho_f,
            self.c_f,
            self.eta_f,
            self.zeta_f,
        )

        self.viscoelastic = ViscoelasticFluid(
            self.f,
            self.rho_f,
            self.c_f,
            self.eta_f,
            self.zeta_f,
            self.eta_p,
            self.zeta_p,
            self.lambda_M,
        )

        self.wave_type = WaveType.STANDING
        self.position = pi / 4

        self.cls_inviscid = BackgroundField(
            self.inviscid,
            self.p_0,
            self.wave_type,
            self.position,
        )
        self.cls_viscous = BackgroundField(
            self.viscous,
            self.p_0,
            self.wave_type,
            self.position,
        )
        self.cls_viscoelastic = BackgroundField(
            self.viscoelastic,
            self.p_0,
            self.wave_type,
            self.position,
        )

        self.list_cls = [
            self.cls_inviscid, self.cls_viscous,
            self.cls_viscoelastic,
        ]

    def test_f(self) -> None:
        self._f.change()
        self.assign_parameters()
        self.assertEqual(self.cls_inviscid.f, self.f)
        self.assertEqual(self.cls_viscous.f, self.f)
        self.assertEqual(self.cls_viscoelastic.f, self.f)

    def test_c_f(self) -> None:
        self._c_f.change()
        self.assign_parameters()
        self.assertEqual(self.cls_inviscid.c_f, self.c_f)
        self.assertEqual(self.cls_viscous.c_f, self.c_f)
        self.assertEqual(self.cls_viscoelastic.c_f, self.c_f)

    def test_rho_f(self) -> None:
        self._rho_f.change()
        self.assign_parameters()
        self.assertEqual(self.cls_inviscid.rho_f, self.rho_f)
        self.assertEqual(self.cls_viscous.rho_f, self.rho_f)
        self.assertEqual(self.cls_viscoelastic.rho_f, self.rho_f)

    def tests_eta_f(self) -> None:
        self._eta_f.change()
        self.assign_parameters()
        self.assertEqual(self.cls_inviscid.eta_f, 0)
        self.assertEqual(self.cls_viscous.eta_f, self.eta_f)
        self.assertEqual(self.cls_viscoelastic.eta_f, self.eta_f)

    def tests_zeta_f(self) -> None:
        self._zeta_f.change()
        self.assign_parameters()
        self.assertEqual(self.cls_inviscid.zeta_f, 0)
        self.assertEqual(self.cls_viscous.zeta_f, self.zeta_f)
        self.assertEqual(self.cls_viscoelastic.zeta_f, self.zeta_f)

    def tests_eta_p(self) -> None:
        self._eta_p.change()
        self.assign_parameters()
        self.assertEqual(self.cls_inviscid.eta_p, 0)
        self.assertEqual(self.cls_viscous.eta_p, 0)
        self.assertEqual(self.cls_viscoelastic.eta_p, self.eta_p)

    def tests_zeta_p(self) -> None:
        self._zeta_p.change()
        self.assign_parameters()
        self.assertEqual(self.cls_inviscid.zeta_p, 0)
        self.assertEqual(self.cls_viscous.zeta_p, 0)
        self.assertEqual(self.cls_viscoelastic.zeta_p, self.zeta_p)

    def tests_lambda_M(self) -> None:
        self._lambda_M.change()
        self.assign_parameters()
        self.assertEqual(self.cls_inviscid.lambda_M, 0)
        self.assertEqual(self.cls_viscous.lambda_M, 0)
        self.assertEqual(self.cls_viscoelastic.lambda_M, self.lambda_M)


class TestViscousBackgroundField(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.fluid_cls = ViscousFluid(
            self.f, self.rho_f,
            self.c_f, self.eta_f,
            self.eta_f,
        )

        self.cls = BackgroundField(
            self.fluid_cls, self.p_0,
            self.wave_type, self.position,
        )

        self.list_cls = [self.fluid_cls, self.cls]
# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------

    def compute_abs_pos(self):
        return self.cls.position / self.cls.k_f.real

    def compute_A(self):
        omega = self.cls.omega
        rho_f = self.rho_f
        p_0 = self.p_0
        return p_0 / (1j * omega * rho_f)

    def compute_abs_A_squared(self):
        A = self.compute_A()
        return np.absolute(A)**2

    def compute_A_in(self, n) -> complex:

        A = self.compute_A()

        wave_type = self.wave_type
        position = self.cls.abs_pos
        k_f = self.cls.k_f

        if wave_type == WaveType.TRAVELLING:
            return A * (2 * n + 1) * 1j ** n
        elif wave_type == WaveType.STANDING:
            out = exp(1j * position * k_f)
            out += (-1)**n * exp(-1j * position * k_f)
            out *= A / 2 * (2 * n + 1) * 1j**n
            return out

    def compute_E(self):
        return 1 / 4 * (self.p_0**2 * self.fluid_cls.kappa_f)

    def compute_I(self):
        out = abs(self.compute_A() ** 2)
        out *= self.rho_f * self.c_f
        out *= (self.fluid_cls.k_f ** 2) / 2
        return out

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

    def test_abs_pos(self):
        self.do_testing(lambda: self.cls.abs_pos, self.compute_abs_pos)

    def test_k_v(self):
        self.do_testing(
            lambda: self.fluid_cls.k_v,
            lambda: self.cls.k_v,
        )

    def test_kappa_f(self):
        self.do_testing(
            lambda: self.fluid_cls.kappa_f,
            lambda: self.cls.kappa_f,
        )

    def test_wave_type(self):
        self.assertRaises(
            ValueError, BackgroundField,
            self.fluid_cls, self.p_0, WaveType.STANDING,
        )

    def test_A(self):
        self.do_testing(func_1=self.compute_A, func_2=lambda: self.cls.A)

    def test_abs_A_squared(self):
        self.do_testing(
            func_1=self.compute_abs_A_squared,
            func_2=lambda: self.cls.abs_A_squared,
        )

    def test_A_in(self) -> None:
        for n in range(4, 0, -1):
            self.do_testing(
                func_1=self.compute_A_in, args_1=n,
                func_2=self.cls.A_in, args_2=n,
            )

    def test_A_in_error(self) -> None:
        self.cls.wave_type = 'None'
        self.assertRaises(WrongWaveTypeError, self.cls.A_in, 20)

    def test_E(self) -> None:
        self.do_testing(lambda: self.cls.E_ac, self.compute_E)

    def test_error_E(self) -> None:
        self.cls.wave_type = 'wrong_wave_type'
        with self.assertRaises(WrongWaveTypeError):
            self.cls.E_ac

    def test_I(self) -> None:
        self.wave_type = WaveType.TRAVELLING
        self._wave_type.list_of_values = [WaveType.TRAVELLING]
        self.do_testing(self.compute_I, lambda: self.cls.I_ac)

    def test_error_I(self) -> None:
        self.cls.wave_type = 'wrong_wave_type'
        with self.assertRaises(WrongWaveTypeError):
            self.cls.I_ac


if __name__ == '__main__':
    unittest.main()
