import unittest

from osaft import WaveType, doinikov1994rigid
from osaft.tests.basetest import BaseTest
from osaft.tests.basetest_arf import HelperCompareARF


@unittest.skip('Unstable test skipped')
class TestCompareSmallBoundaryLayer(BaseTest, HelperCompareARF):

    def setUp(self):
        super().setUp()

        self.arf_compare_threshold = 1e-2
        self.small_viscous_boundary_layer = True
        self.large_viscous_boundary_layer = False
        self.small_particle_limit = True

        # Frequency
        self._f.low = 0.9e5
        self._f.high = 1.1e5
        self.f = 1e5

        # Radius
        self._R_0.high = 12e-6
        self._R_0.low = 8e-6
        self.R_0 = 10e-6

        # Density
        self._rho_s.low = 4.9e3
        self._rho_s.high = 5e3
        self.rho_s = 5.1e3

        # Viscosity
        self._eta_f.low = 1e-7
        self._eta_f.high = 1e-6
        self.eta_f = 5e-7
        self.zeta_f = 0

        self.cls = doinikov1994rigid.ARF(
            self.f,
            self.R_0, self.rho_s,
            self.rho_f, self.c_f, self.eta_f, self.zeta_f,
            self.p_0, WaveType.STANDING,
            self.position,
            small_particle_limit=self.small_viscous_boundary_layer,
            large_viscous_boundary_layer=self.large_viscous_boundary_layer,
            small_viscous_boundary_layer=self.small_particle_limit,
        )

        self.compare_cls = doinikov1994rigid.ARF(
            self.f,
            self.R_0, self.rho_s,
            self.rho_f, self.c_f, self.eta_f, self.zeta_f,
            self.p_0, WaveType.STANDING,
            self.position,
            small_particle_limit=self.small_particle_limit,
        )

        self.list_cls = [self.cls, self.compare_cls]


if __name__ == '__main__':
    unittest.main()
