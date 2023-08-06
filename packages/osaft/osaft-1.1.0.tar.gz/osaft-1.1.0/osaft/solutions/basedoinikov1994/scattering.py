from __future__ import annotations

from abc import ABC, abstractmethod

from osaft.core.functions import BesselFunctions as Bf
from osaft.solutions.base_scattering import BaseScattering


class BaseScatteringDoinikov1994(BaseScattering, ABC):
    """Base scattering class for Doinikov solutions from 1994

    :param N_max: Highest order mode included in the computation [-]
    """
    def __init__(self, N_max: int) -> None:
        """"init method"""
        super().__init__(N_max)

    # -------------------------------------------------------------------------
    # Velocity amplitudes
    # -------------------------------------------------------------------------

    def V_r_sc(self, n: int, r: float) -> complex:
        """Radial scattering field velocity term of mode `n`
        without Legendre coefficients

        Returns radial scattering field velocity in [m/s]

        :param n: mode
        :param r: radial coordinate [m]
        """
        out = self.k_f * self.alpha_n(n) * Bf.d1_hankelh1(n, r * self.k_f)
        out -= n * (n + 1) / r * self.beta_n(n) * Bf.hankelh1(n, r * self.k_v)
        out *= self.A_in(n)
        return out

    def V_theta_sc(self, n: int, r: float) -> complex:
        """Tangential scattering field velocity term of mode n
        without Legendre coefficients

        Returns tangential scattering field velocity in [m/s]

        :param n: mode
        :param r: radial coordinate [m]
        """
        arg = self.k_v * r
        out = Bf.hankelh1(n, arg)
        out += arg * Bf.d1_hankelh1(n, arg)
        out *= -self.beta_n(n)
        out += self.alpha_n(n) * Bf.hankelh1(n, self.k_f * r)
        out *= self.A_in(n)
        return out / r

    # -------------------------------------------------------------------------
    # Abstract methods
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def k_f(self) -> complex:
        """Returns the wave number in the fluid :math:`k_f` [1/m]
        """
        pass

    @property
    @abstractmethod
    def k_v(self) -> complex:
        """Returns the viscous wave number in the fluid :math:`k_v` [1/m]
            """
        pass

    @abstractmethod
    def A_in(self, n: int):
        pass

    @abstractmethod
    def alpha_n(self, n: int) -> complex:
        pass

    @abstractmethod
    def beta_n(self, n: int) -> complex:
        pass


if __name__ == '__main__':
    pass
