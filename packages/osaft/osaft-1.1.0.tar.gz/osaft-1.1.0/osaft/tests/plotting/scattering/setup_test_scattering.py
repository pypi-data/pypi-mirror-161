from osaft import WaveType, yosioka1955
from osaft.tests.basetest_plotting import BaseTestPlotting


class BaseTestScattering(BaseTestPlotting):

    def setUp(self) -> None:

        super().setUp()
        self.f = 10e6
        self.R_0 = 30e-6
        self.c_s = 3e2
        self.c_f = 1.5e3
        self.rho_s = 1e3
        self.rho_f = 1.5e3
        self.p_0 = 1e5
        self.wave_type = WaveType.TRAVELLING
        self.position = self.c_f / self.f / 8

        self.N_max = 10

        self.yosioka = yosioka1955.ScatteringField(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s, c_s=self.c_s,
            rho_f=self.rho_f, c_f=self.c_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
            N_max=self.N_max,
        )


if __name__ == '__main__':
    pass
