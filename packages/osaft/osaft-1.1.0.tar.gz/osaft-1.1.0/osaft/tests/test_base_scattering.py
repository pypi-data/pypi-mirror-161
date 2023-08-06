import unittest

import numpy as np

from osaft import BackgroundField, InviscidFluid, WaveType
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import LegendreFunctions as Leg
from osaft.core.functions import full_range
from osaft.solutions.base_scattering import (
    BaseScattering,
    BaseScatteringRigidParticle,
)


class Scattering(BaseScattering):

    def __init__(self, N_max: int):
        super().__init__(N_max)
        self.f = 1e6
        self.fluid = InviscidFluid(self.f, 1000, 1500)
        self.field = BackgroundField(self.fluid, 1e5, WaveType.TRAVELLING)

    @property
    def omega(self):
        return 2 * np.pi * self.f

    @property
    def R_0(self):
        return 1e-6

    @property
    def k_f(self):
        return 2e4

    def V_r_sc(self, n, r) -> complex:
        pass

    def V_theta_sc(self, n, r) -> complex:
        pass

    def radial_particle_velocity(self, r, theta, t, mode) -> complex:
        pass

    def tangential_particle_velocity(self, r, theta, t, mode) -> complex:
        pass

    def A_in(self, n):
        return self.field.A_in(n)


class ScatteringRigidParticle(BaseScatteringRigidParticle):
    def __init__(self, N_max: int):
        super().__init__()
        self.f = 1e6
        self.fluid = InviscidFluid(self.f, 1000, 1500)
        self.field = BackgroundField(self.fluid, 1e5, WaveType.TRAVELLING)

    @property
    def omega(self):
        return 2 * np.pi * self.f

    @property
    def R_0(self):
        return 1e-6

    @property
    def k_f(self):
        return 2e4

    def V_r_sc(self, n, r) -> complex:
        pass

    def V_theta_sc(self, n, r) -> complex:
        pass

    def radial_particle_velocity(self, r, theta, t, mode):
        if mode is None or mode == 1:
            return self.particle_velocity(t) * np.cos(theta)
        else:
            return 0 * r * theta * t

    def tangential_particle_velocity(self, r, theta, t, mode):
        if mode is None or mode == 1:
            return -self.particle_velocity(t) * np.sin(theta)
        else:
            return 0 * r * theta * t

    def particle_velocity(self, t):
        return t

    def A_in(self, n):
        return self.field.A_in(n)


class TestBaseScattering(unittest.TestCase):

    def setUp(self) -> None:
        self.cls = Scattering(5)

    def test_tangential_acoustic_fluid_velocity(self) -> None:
        self.assertRaises(
            ValueError,
            self.cls.tangential_acoustic_fluid_velocity,
            0, 0, 0, False, False,
        )

    def test_radial_acoustic_fluid_velocity(self) -> None:
        self.assertRaises(
            ValueError,
            self.cls.radial_acoustic_fluid_velocity,
            0, 0, 0, False, False,
        )

    def test_N_max(self) -> None:
        self.assertEqual(5, self.cls.N_max)
        self.cls.N_max = 7
        self.assertEqual(7, self.cls.N_max)

    def test_radial_mode_superposition(self) -> None:
        def radial_mode_superposition(r_func, r, theta, t, mode):
            out = np.exp(-1j * self.cls.omega * t)
            if mode is not None:
                out *= Leg.cos_monomial(mode, theta, r_func(mode, r))
            else:
                array = [r_func(n, r) for n in full_range(0, self.cls.N_max)]
                out *= Leg.cos_poly(theta, np.array(array))
            return out

        def radial_func(n, r):
            return Bf.besselj(n, r) - 1j * Bf.hankelh1(n, r)

        for mode in [0, 1, 2, 3, 4, None]:
            r = self.cls.R_0 * (np.random.random() + 1)
            theta = np.pi * np.random.random()
            t = np.random.random()
            with self.subTest(r=r, theta=theta, t=t, mode=mode):
                val1 = radial_mode_superposition(
                    radial_func, r, theta, t, mode,
                )
                val2 = self.cls.radial_mode_superposition(
                    radial_func, r, theta, t, mode,
                )
                self.assertEqual(val1, val2)

    def test_tangential_mode_superposition(self) -> None:
        def tangential_mode_superposition(t_func, r, theta, t, mode):
            out = np.exp(-1j * self.cls.omega * t)
            if mode is not None:
                out *= Leg.first_cos_monomial(mode, theta, t_func(mode, r))
            else:
                array = [t_func(n, r) for n in full_range(0, self.cls.N_max)]
                out *= Leg.first_cos_poly(theta, np.array(array))
            return out

        def tangential_func(n, r):
            return Bf.besselj(n, r) - 1j * Bf.hankelh1(n, r)

        for mode in [0, 1, 2, 3, 4, None]:
            r = self.cls.R_0 * (np.random.random() + 1)
            theta = np.pi * np.random.random()
            t = np.random.random()
            with self.subTest(r=r, theta=theta, t=t, mode=mode):
                val1 = tangential_mode_superposition(
                    tangential_func, r, theta, t, mode,
                )
                val2 = self.cls.tangential_mode_superposition(
                    tangential_func, r, theta, t, mode,
                )
                self.assertEqual(val1, val2)

    def test_V_r_i(self) -> None:
        def V_r_i(n, r):
            out = self.cls.field.A_in(n) * self.cls.k_f
            out *= Bf.d1_besselj(n, self.cls.k_f * r)
            return out

        for n in np.arange(5):
            r = self.cls.R_0 * (np.random.random() + 1)
            with self.subTest(n=n, r=r):
                self.assertEqual(V_r_i(n, r), self.cls.V_r_i(n, r))

    def test_V_theta_i(self) -> None:
        def V_theta_i(n, r):
            out = self.cls.field.A_in(n)
            out *= Bf.besselj(n, self.cls.k_f * r) / r
            return out

        for n in np.arange(5):
            r = self.cls.R_0 * (np.random.random() + 1)
            with self.subTest(n=n, r=r):
                self.assertAlmostEqual(
                    V_theta_i(n, r), self.cls.V_theta_i(n, r),
                )


class TestBaseScatteringRigidParticle(unittest.TestCase):

    def setUp(self):
        self.cls = ScatteringRigidParticle(5)

    def test_radial_particle_velocity(self):
        def radial_particle_velocity(r, theta, t, mode):
            if mode is None or mode == 1:
                return np.cos(theta) * t
            else:
                return 0

        for mode in [0, 1, 2, 3, 4, None]:
            r = np.random.random()
            theta = np.random.random() * np.pi
            t = np.random.random()

            with self.subTest(r=r, theta=theta, t=t, mode=mode):
                self.assertEqual(
                    radial_particle_velocity(r, theta, t, mode),
                    self.cls.radial_particle_velocity(r, theta, t, mode),
                )

    def test_tangential_particle_velocity(self):
        def tangential_particle_velocity(r, theta, t, mode):
            if mode is None or mode == 1:
                return -np.sin(theta) * t
            else:
                return 0

        for mode in [0, 1, 2, 3, 4, None]:
            r = np.random.random()
            theta = np.random.random() * np.pi
            t = np.random.random()

            with self.subTest(r=r, theta=theta, t=t, mode=mode):
                self.assertEqual(
                    tangential_particle_velocity(r, theta, t, mode),
                    self.cls.tangential_particle_velocity(r, theta, t, mode),
                )


if __name__ == '__main__':
    unittest.main()
