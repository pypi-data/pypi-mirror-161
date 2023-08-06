import unittest

from osaft import WaveType, doinikov1994compressible, settnes2012
from osaft.tests.basetest import BaseTest
from osaft.tests.basetest_arf import HelperCompareARF


@unittest.skip('')
class TestCompareSmallBoundaryLayer(BaseTest, HelperCompareARF):

    def setUp(self):
        super().setUp()

        self.arf_compare_threshold = 1e-2
        self.small_viscous_boundary_layer = True
        self.large_viscous_boundary_layer = False
        self.small_particle_limit = True
        self.wave_type = WaveType.TRAVELLING
        self._wave_type.list_of_values = [WaveType.TRAVELLING]

        # Frequency
        self._f.low = 1e6
        self._f.high = 3e6
        self.f = 1e6

        # Radius
        self._R_0.high = 5e-6
        self._R_0.low = 3e-6
        self.R_0 = 3e-6

        # Viscosity
        self._eta_f.low = 1e-4
        self._eta_f.high = 1e-2
        self.eta_f = 1e-4
        self.zeta_f = 0
        self.eta_s = 1
        self.zeta_s = 1

        self.cls = doinikov1994compressible.ARF(
            self.f,
            self.R_0,
            self.rho_s, self.c_s, self.eta_s, self.zeta_s,
            self.rho_f, self.c_f, self.eta_f, self.zeta_f,
            self.p_0, self.wave_type,
            self.position,
            small_particle_limit=self.small_viscous_boundary_layer,
            large_viscous_boundary_layer=self.large_viscous_boundary_layer,
            small_viscous_boundary_layer=self.small_particle_limit,
        )

        print(self.cls.x_v)
        print(self.cls.x)

        self.compare_cls = settnes2012.ARF(
            self.f,
            self.R_0,
            self.rho_s, self.c_s,
            self.rho_f, self.c_f, self.eta_f,
            self.p_0, self.wave_type,
            self.position,
        )

        self.list_cls = [self.cls, self.compare_cls]


if __name__ == '__main__':
    pass
