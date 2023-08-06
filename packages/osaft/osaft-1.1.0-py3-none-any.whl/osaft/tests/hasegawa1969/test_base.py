from osaft import hasegawa1969
from osaft.tests.basetest import BaseTest


class TestScattering(BaseTest):

    def setUp(self) -> None:
        super().setUp()

        self.cls = hasegawa1969.BaseHasegawa(
            f=self.f,
            R_0=self.R_0,
            rho_s=self.rho_s, E_s=self.E_s, nu_s=self.nu_s,
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
    def x_f(self) -> float:
        return self.R_0 * self.cls.k_f

    @property
    def x_s_l(self) -> float:
        return self.R_0 * self.cls.k_s_l

    @property
    def x_s_t(self) -> float:
        return self.R_0 * self.cls.k_s_t

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_properties(self) -> None:
        properties = ['lambda_rho', 'x_s_l', 'x_s_t', 'x_f']
        self._test_properties(properties)
