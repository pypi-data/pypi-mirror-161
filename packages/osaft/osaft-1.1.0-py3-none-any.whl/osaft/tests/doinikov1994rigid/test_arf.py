import unittest
import warnings
from enum import auto

from osaft import doinikov1994rigid
from osaft.core.backgroundfields import WaveType, WrongWaveTypeError
from osaft.core.functions import pi, sin, xexpexp1
from osaft.tests.basedoinikov1994.test_base import BaseTestDoinikov1994
from osaft.tests.basetest_arf import HelperStandingARF, HelperTravelingARF


class TestARFBase(BaseTestDoinikov1994):

    def setUp(self) -> None:

        super().setUp()

        self.small_particle_limit = True
        self.small_viscous_boundary_layer = False
        self.large_viscous_boundary_layer = False
        self.fastened_sphere = False
        self.N_max = 5

        self._eta_f.low = 1e-5
        self._eta_f.high = 1e-3
        self._f.low = 1e6
        self._f.high = 10e6
        self._R_0.low = 1e-6

        self.cls = doinikov1994rigid.ARF(
            self.f,
            self.R_0, self.rho_s,
            self.rho_f, self.c_f, self.eta_f, self.zeta_f,
            self.p_0, WaveType.STANDING,
            self.position,
            self.small_particle_limit,
            self.small_viscous_boundary_layer,
            self.large_viscous_boundary_layer,
            self.fastened_sphere,
            self.N_max,
        )

        self.list_cls = [self.cls]

    def assign_parameters(self) -> None:
        super().assign_parameters()

        self.cls.fastened_sphere = self.fastened_sphere
        self.cls.small_viscous_boundary_layer = (
            self.small_viscous_boundary_layer
        )
        self.cls.large_viscous_boundary_layer = (
            self.large_viscous_boundary_layer
        )
        self.cls.small_particle_limit = self.small_particle_limit
        self.cls.N_max = self.N_max

    # ------------------

    def test_fastened_sphere(self) -> None:
        self.assign_parameters()
        self.assertEqual(self.fastened_sphere, self.cls.fastened_sphere)
        self.fastened_sphere = True
        self.assign_parameters()
        self.assertEqual(self.fastened_sphere, self.cls.fastened_sphere)

    def test_wrong_wave_type_error(self):

        # Wrong wave type
        WaveType.WRONGWAVETYPE = auto()
        self.cls.wave_type = WaveType.WRONGWAVETYPE
        self.assertRaises(WrongWaveTypeError, self.cls.compute_arf)

    # ------------------

    def test_small_particle_limit(self) -> None:
        self.assign_parameters()
        self.assertEqual(
            self.small_particle_limit,
            self.cls.small_particle_limit,
        )

    def test_small_particle_limit_error(self) -> None:
        self.small_particle_limit = False
        self.assertRaises(NotImplementedError, self.assign_parameters)

    def test_small_viscous_boundary_layer(self) -> None:
        self.assign_parameters()
        self.assertEqual(
            self.small_viscous_boundary_layer,
            self.cls.small_viscous_boundary_layer,
        )
        self.small_viscous_boundary_layer = True
        self.assign_parameters()
        self.assertEqual(
            self.small_viscous_boundary_layer,
            self.cls.small_viscous_boundary_layer,
        )

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def physical_position(self) -> float:
        return self.position * self.c_f / self.cls.omega
    # -------------------------------------------------------------------------
    # F2 (Streaming contribution)
    # -------------------------------------------------------------------------

    @property
    def F_2_standing(self):
        k = self.cls.k_f
        x = self.x
        x_v = self.x_v
        d = self.cls.abs_pos
        first = sin(k * d + k.conjugate() * d) * sin(x + x.conjugate())
        first *= (x - x.conjugate()) / (x + x.conjugate())
        second = sin(k * d - k.conjugate() * d) * sin(x - x.conjugate())
        second *= (x + x.conjugate()) / (x - x.conjugate())
        out = first - second
        out *= - 3 / 4 * pi * self.rho_f * self.cls.field.abs_A_squared
        out *= x * x.conjugate()
        out /= x_v ** 2
        return out

    @property
    def F_2_travelling(self):
        x = self.x
        x_v = self.x_v

        out = sin(x - x.conjugate()) / (x - x.conjugate()) * 1j / x_v ** 2
        out *= x * x.conjugate() * (x + x.conjugate())
        out *= - 3 / 2 * pi * self.rho_f * self.cls.field.abs_A_squared
        return out

    # -------------------------------------------------------------------------
    # D_n
    # -------------------------------------------------------------------------
    @property
    def D_0(self):
        out = self.G_1
        out += self.x_v ** 3 * (12 + self.x_v ** 2) * self.function(self.x_v)
        out *= -self.x ** 3 * self.G_0
        out += 2 * self.x ** 3 / 9
        out += self.x ** 3 / (3 * self.x_v ** 2)
        return out

    @property
    def D_1(self):
        out = - 2 * (1 + 1j) * (9 + self.x_v ** 2)
        out *= self.function(self.x_v - 1j * self.x_v)
        out += 2 * self.G_3 * self.function(self.x_v)
        out += 1j * self.G_4 * self.function(-1j * self.x_v)
        out *= - self.x_v ** 3
        out += self.G_2
        out *= self.cls.x ** 3 * self.G_0.conjugate() / (1 + self.x_v)
        out += self.cls.x ** 3 / (3 * self.x_v ** 2)
        return out

    @staticmethod
    def function(z):
        return xexpexp1(z)

    # -------------------------------------------------------------------------
    # G_n
    # -------------------------------------------------------------------------

    @property
    def G_0(self) -> complex:
        denominator = 72 * (
            9 * self.rho_t + 9 * self.rho_t * self.x_v
            + (2 + self.rho_t) * self.x_v ** 2
        )
        numerator = (1 - self.rho_t)
        return numerator / denominator

    @property
    def G_1(self) -> complex:
        out = 48 - 96 * self.x_v + 2 * self.x_v ** 2 - 14 * self.x_v ** 3
        out += self.x_v ** 4 - self.x_v ** 5
        return out

    @property
    def G_2(self):
        out = 48 + (48 + 192 * 1j / 5) * self.x_v
        out += (122 + 192 * 1j) * self.x_v ** 2 / 5
        out += 42 * (1 - 1j) * self.x_v ** 3 / 5
        out += (49 + 36 * 1j) * self.x_v ** 4 / 10
        out -= (31 - 17 * 1j) * self.x_v ** 5 / 10
        out += (6 + 31 * 1j) * self.x_v ** 6 / 30
        out += (1 + 6 * 1j) * self.x_v ** 7 / 30
        out += 1j * self.x_v ** 8 / 30
        return out

    @property
    def G_3(self):
        return 3 - 3 * 1j * self.x_v - self.x_v ** 2

    @property
    def G_4(self):
        out = 9 + 9 * self.x_v + 41 * self.x_v ** 2 / 10
        out += 11 * self.x_v ** 3 / 10
        out += self.x_v ** 4 / 5 + self.x_v ** 5 / 30
        return out

    # -------------------------------------------------------------------------
    # Test Properties
    # -------------------------------------------------------------------------

    def test_D_1(self):
        warnings.filterwarnings('error', category=RuntimeWarning)
        try:
            self.do_testing(
                func_1=lambda: self.D_1,
                func_2=lambda: self.cls.D_1,
                threshold=1e-3,
            )
        except RuntimeWarning:
            pass
        warnings.filterwarnings('default', category=RuntimeWarning)

    def test_properties(self) -> None:
        properties = [
            'rho_t', 'G_0', 'G_1', 'G_2', 'G_3', 'G_4',
            'D_0', 'F_2_standing', 'F_2_travelling',
        ]
        self._test_properties(properties, threshold=1e-6)


# |x| << 1  |x| << |x_v|

class TestSmallParticleTravelling(HelperTravelingARF, TestARFBase):

    def setUp(self):
        TestARFBase.setUp(self)
        self._threshold = 1e-7
        self.fastened_sphere = False
        self.large_viscous_boundary_layer = False
        self.small_viscous_boundary_layer = False
        self.assign_parameters()

    def compute_arf(self):
        F1 = self.D_0 - self.D_0.conjugate()
        F1 += 2 * (self.D_1 - self.D_1.conjugate())
        F1 *= 3 / 2 * 1j * pi * self.rho_f * self.cls.field.abs_A_squared
        F2 = self.F_2_travelling
        return (F1 + F2).real


class TestSmallParticleStanding(HelperStandingARF, TestARFBase):

    def setUp(self):
        TestARFBase.setUp(self)
        self._threshold = 1e-7
        self.fastened_sphere = False
        self.large_viscous_boundary_layer = False
        self.small_viscous_boundary_layer = False
        self.assign_parameters()

    def compute_arf(self):
        d = self.cls.abs_pos
        sine = sin(2 * self.cls.k_f * d)
        sine_conj = sin(2 * self.cls.k_f.conjugate() * d)
        F1 = self.D_0 * sine + self.D_0.conjugate() * sine_conj
        F1 -= 2 * (self.D_1 * sine + self.D_1.conjugate() * sine_conj)
        F1 *= 3 / 4 * pi * self.rho_f * self.cls.field.abs_A_squared
        F2 = self.F_2_standing
        return (F1 + F2).real


# |x| << 1 << |x_v|

class TestARFLimit1Standing(HelperStandingARF, TestARFBase):

    def setUp(self) -> None:
        TestARFBase.setUp(self)
        self.fastened_sphere = False
        self.large_viscous_boundary_layer = False
        self.small_viscous_boundary_layer = True
        self.assign_parameters()

    def compute_arf(self):
        out = (5 - 2 * self.rho_t) / (3 * (2 + self.rho_t))
        out += 3 * (1 - self.rho_t)**2 / (2 + self.rho_t)**2 * self.norm_delta

        out *= pi * self.rho_f * self.x_0**3 * self.cls.field.abs_A_squared
        out *= sin(2 * self.position)

        return out


class TestARFLimit1Traveling(HelperTravelingARF, TestARFBase):

    def setUp(self) -> None:
        TestARFBase.setUp(self)
        self.fastened_sphere = False
        self.large_viscous_boundary_layer = False
        self.small_viscous_boundary_layer = True
        self.assign_parameters()

    def compute_arf(self):
        out = 2 + 12 * self.rho_t - 21 * self.rho_t**2 + 7 * self.rho_t**3
        out *= -self.norm_delta / (2 + self.rho_t)

        out += (1 - self.rho_t)**2

        out *= 6 * pi * self.rho_f * self.x_0**3 * self.norm_delta
        out *= self.cls.field.abs_A_squared / (2 + self.rho_t)**2

        return out


# |x| << |x_v| << 1

class TestARFLimit2Standing(HelperStandingARF, TestARFBase):

    def setUp(self) -> None:
        TestARFBase.setUp(self)
        self.fastened_sphere = False
        self.large_viscous_boundary_layer = True
        self.small_viscous_boundary_layer = False
        self.assign_parameters()

    def compute_arf(self):
        out = 11 * (1 - self.rho_t)
        out /= 5 * self.norm_delta

        out += 2 * self.rho_t - 1

        out *= pi / 3 * self.rho_s * self.x_0**3 * self.cls.field.abs_A_squared
        out *= sin(2 * self.position)

        return out


class TestARFLimit2Traveling(HelperTravelingARF, TestARFBase):

    def setUp(self) -> None:
        TestARFBase.setUp(self)
        self.fastened_sphere = False
        self.large_viscous_boundary_layer = True
        self.small_viscous_boundary_layer = False
        self.assign_parameters()

    def compute_arf(self):
        out = -22 / 15 * pi * self.rho_s * self.x_0**3
        out *= self.cls.field.abs_A_squared

        out *= (1 - self.rho_t) / self.norm_delta

        return out


# |x| << 1 << |x_v|

class TestARFLimit3Standing(HelperStandingARF, TestARFBase):

    def setUp(self) -> None:
        TestARFBase.setUp(self)
        self.fastened_sphere = True
        self.large_viscous_boundary_layer = False
        self.small_viscous_boundary_layer = True
        self.assign_parameters()

    def compute_arf(self):
        out = 5 / 6 + 3 / 4 * self.norm_delta

        out *= pi * self.rho_f * self.x_0**3 * self.cls.field.abs_A_squared
        out *= sin(2 * self.position)

        return out


class TestARFLimit3Traveling(HelperTravelingARF, TestARFBase):

    def setUp(self) -> None:
        TestARFBase.setUp(self)
        self.fastened_sphere = True
        self.large_viscous_boundary_layer = False
        self.small_viscous_boundary_layer = True
        self.assign_parameters()

    def compute_arf(self):
        out = 3 / 2 * pi * self.rho_f * self.x_0**3
        out *= self.cls.field.abs_A_squared

        out *= self.norm_delta * (1 - self.norm_delta)

        return out


# |x| << |x_v| << 1

class TestARFLimit4Standing(HelperStandingARF, TestARFBase):

    def setUp(self) -> None:
        TestARFBase.setUp(self)
        self.fastened_sphere = True
        self.large_viscous_boundary_layer = True
        self.small_viscous_boundary_layer = False
        self.assign_parameters()

    def compute_arf(self):
        out = 1 + 10 / 27 / self.norm_delta

        out *= pi * self.rho_f * self.x_0**3 * self.cls.field.abs_A_squared
        out *= 0.9 * sin(2 * self.position) * self.norm_delta

        return out


class TestARFLimit4Traveling(HelperTravelingARF, TestARFBase):

    def setUp(self) -> None:
        TestARFBase.setUp(self)
        self.fastened_sphere = True
        self.large_viscous_boundary_layer = True
        self.small_viscous_boundary_layer = False
        self.assign_parameters()

    def compute_arf(self):
        out = -3 / 2 * pi * self.rho_f * self.x_0**3
        out *= self.cls.field.abs_A_squared

        out *= self.norm_delta**2 * (1 - 6 / 5 / self.norm_delta)

        return out


if __name__ == '__main__':
    unittest.main()
