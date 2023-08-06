from osaft import yosioka1955
from osaft.tests.basetest import BaseTest


class TestScattering(BaseTest):

    def setUp(self) -> None:
        super().setUp()

        self.cls = yosioka1955.BaseYosioka(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s, c_s=self.c_s,
            rho_f=self.rho_f, c_f=self.c_f,
            p_0=self.p_0,
            wave_type=self.wave_type,
            position=self.position,
        )

        self.list_cls = [self.cls]

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    @property
    def lambda_rho(self) -> float:
        return self.rho_s / self.rho_f

    @property
    def sigma(self) -> float:
        return self.c_s / self.c_f

    @property
    def x_f(self) -> float:
        return self.R_0 * self.cls.k_f

    @property
    def x_s(self) -> float:
        return self.R_0 * self.cls.k_s

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_properties(self) -> None:
        properties = ['lambda_rho', 'sigma', 'x_s', 'x_f']
        self._test_properties(properties)
