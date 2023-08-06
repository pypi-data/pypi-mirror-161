import unittest

import numpy as np

from osaft import yosioka1955
from osaft.core.functions import exp
from osaft.plotting.datacontainers.scattering_datacontainer import (
    ParticleScatteringData,
)
from osaft.tests.basetest import BaseTest


class TestParticleScatteringDatacontainer(BaseTest):

    def setUp(self) -> None:

        super().setUp()

        self.sol = yosioka1955.ScatteringField(
            self.f, self.R_0,
            self.rho_s, self.c_s,
            self.rho_f, self.c_f,
            self.p_0,
            self.wave_type,
            self.position,
        )

        self.cls = ParticleScatteringData(
            self.sol,
        )

    def test_r_min(self):
        self.assertEqual(self.cls.r_min, 1e-30)

    def test_r_max(self):
        self.assertEqual(self.cls.r_max, self.sol.R_0)

    def test_changing_mode(self):
        # mode = 1
        _, _, v_1 = self.cls.get_velocity_magnitude(mode=1)
        # mode = 2
        _, _, v_2 = self.cls.get_velocity_magnitude(mode=2)
        self.assertFalse(np.array_equal(v_1, v_2))
        # mode = 1
        _, _, v_3 = self.cls.get_velocity_magnitude(mode=1)
        np.testing.assert_array_equal(v_1, v_3)

    def test_displacement_magnitude(self):
        # Instantaneous
        _, _, u_mag = self.cls.get_displacement_magnitude(instantaneous=True)
        _, _, u, v = self.cls.get_displacement_vector()
        u_mag_tests = np.hypot(u, v)
        np.testing.assert_allclose(u_mag, u_mag_tests)
        # Average
        _, _, u_mag = self.cls.get_displacement_magnitude(instantaneous=False)
        _, _, v_mag = self.cls.get_velocity_magnitude(instantaneous=False)
        np.testing.assert_allclose(u_mag, v_mag / self.cls.sol.omega)
        # Instantaneous With Phase
        phase = 1
        _, _, u_mag = self.cls.get_velocity_magnitude(
            instantaneous=True,
            phase=phase,
        )
        _, _, u, v = self.cls.get_velocity_vector(phase=phase)
        u_mag_tests = np.hypot(u, v)

    def test_velocity_magnitude(self):
        # Instantaneous
        _, _, u_mag = self.cls.get_velocity_magnitude(instantaneous=True)
        _, _, u, v = self.cls.get_velocity_vector()
        u_mag_tests = np.hypot(u, v)
        np.testing.assert_allclose(u_mag, u_mag_tests)
        # Average
        _, _, u_mag = self.cls.get_velocity_magnitude(instantaneous=False)
        u_mag_tests = np.hypot(np.abs(self.cls.u), np.abs(self.cls.w))
        np.testing.assert_allclose(u_mag, u_mag_tests)
        # Instantaneous With Phase
        phase = 1
        _, _, u_mag = self.cls.get_velocity_magnitude(
            instantaneous=True,
            phase=phase,
        )
        _, _, u, v = self.cls.get_velocity_vector(phase=phase)
        u_mag_tests = np.hypot(u, v)
        np.testing.assert_allclose(u_mag, u_mag_tests)

    def test_compare_velocity_displacement(self):
        _, _, v = self.cls.get_velocity_magnitude()
        _, _, u = self.cls.get_displacement_magnitude()

    def test_displacement_phase(self):
        phase = 1
        _, _, u, v = self.cls.get_displacement_vector(phase=phase)
        u_test = (self.cls.u * exp(-1j * phase) / self.sol.omega).real
        v_test = (self.cls.w * exp(-1j * phase) / self.sol.omega).real
        np.testing.assert_allclose(u, u_test)
        np.testing.assert_allclose(v, v_test)

    def test_velocity_phase(self):
        phase = 1
        _, _, u, v = self.cls.get_velocity_vector(phase=phase)
        u_test = (self.cls.u * exp(-1j * phase)).real
        v_test = (self.cls.w * exp(-1j * phase)).real
        np.testing.assert_allclose(u, u_test)
        np.testing.assert_allclose(v, v_test)


if __name__ == '__main__':
    unittest.main()
