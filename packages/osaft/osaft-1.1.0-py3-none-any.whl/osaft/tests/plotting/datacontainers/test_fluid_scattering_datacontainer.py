import unittest

import numpy as np

from osaft import yosioka1955
from osaft.core.functions import exp
from osaft.plotting.datacontainers.scattering_datacontainer import (
    FluidScatteringData,
)
from osaft.tests.basetest import BaseTest


class TestFluidScatteringDatacontainer(BaseTest):

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

        self.cls = FluidScatteringData(
            self.sol, 5 * self.sol.R_0,
        )

    def test_r_min(self):
        self.assertEqual(self.cls.r_min, self.sol.R_0)

    def test_velocity_magnitude(self):
        self.cls.scattered = True
        self.cls.incident = True
        # Instantaneous
        _, _, u_mag = self.cls.get_velocity_magnitude(
            instantaneous=True, scattered=True, incident=True,
        )
        _, _, u, v = self.cls.get_velocity_vector(scattered=True)
        u_mag_tests = np.hypot(u, v)
        np.testing.assert_allclose(u_mag, u_mag_tests)
        # Average
        _, _, u_mag = self.cls.get_velocity_magnitude(
            instantaneous=False, scattered=True, incident=True,
        )
        u_mag_tests = np.hypot(np.abs(self.cls.u), np.abs(self.cls.w))
        np.testing.assert_allclose(u_mag, u_mag_tests)
        # Instantaneous With Phase
        phase = 1
        _, _, u_mag = self.cls.get_velocity_magnitude(
            instantaneous=True, phase=phase, scattered=True, incident=True,
        )
        _, _, u, v = self.cls.get_velocity_vector(phase=phase)
        u_mag_tests = np.hypot(u, v)
        np.testing.assert_allclose(u_mag, u_mag_tests)

    def test_compare_velocity_displacement(self):
        _, _, v = self.cls.get_velocity_magnitude()
        _, _, u = self.cls.get_displacement_magnitude()

    def test_displacement_phase(self):
        self.cls.scattered = True
        self.cls.incident = False
        phase = 1
        _, _, u, v = self.cls.get_displacement_vector(
            phase=phase, scattered=True, incident=False,
        )
        u_test = (self.cls.u * exp(-1j * phase) / self.sol.omega).real
        v_test = (self.cls.w * exp(-1j * phase) / self.sol.omega).real
        np.testing.assert_allclose(u, u_test)
        np.testing.assert_allclose(v, v_test)

    def test_velocity_phase(self):
        phase = 1
        _, _, u, v = self.cls.get_velocity_vector(
            phase=phase,
            scattered=True,
            incident=False,
        )
        u_test = (self.cls.u * exp(-1j * phase)).real
        v_test = (self.cls.w * exp(-1j * phase)).real
        np.testing.assert_allclose(u, u_test)
        np.testing.assert_allclose(v, v_test)

    def test_incident_scattering(self):
        _, _, u_incident, v_incident = self.cls.get_velocity_vector(
            scattered=False, incident=True,
        )
        _, _, u_scattered, v_scattered = self.cls.get_velocity_vector(
            scattered=True, incident=False,
        )
        _, _, u_total, v_total = self.cls.get_velocity_vector(
            scattered=True, incident=True,
        )
        np.testing.assert_allclose(u_incident + u_scattered, u_total)
        np.testing.assert_allclose(v_incident + v_scattered, v_total)


if __name__ == '__main__':
    unittest.main()
