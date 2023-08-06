from typing import Optional, Union

import numpy as np

from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.geometries import Sphere
from osaft.core.helper import InputHandler
from osaft.core.variable import ActiveListVariable
from osaft.solutions.basedoinikov1994.scattering import (
    BaseScatteringDoinikov1994,
)
from osaft.solutions.doinikov1994compressible.coefficientmatrix import (
    CoefficientMatrix,
)


class ScatteringField(CoefficientMatrix, BaseScatteringDoinikov1994):
    """Scattering field of Doinikov (viscous fluid-viscous sphere; 1994)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the sphere [kg/m^3]
    :param c_s: Speed of sound of in the sphere [m/s]
    :param eta_s: shear viscosity of in the sphere  [Pa s]
    :param zeta_s: bulk viscosity of in the sphere [Pa s]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param eta_f: shear viscosity [Pa s]
    :param zeta_f: bulk viscosity [Pa s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param position: Position within the standing wave field [m]
    :param wave_type: Type of wave, traveling or standing
    :param N_max: Highest order mode included in the computation [-]
    """

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float, c_s: float, eta_s: float, zeta_s: float,
        rho_f: float, c_f: float, eta_f: float, zeta_f: float,
        p_0: float, wave_type: WaveType, position: float,
        N_max: Optional[int] = 5,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        CoefficientMatrix.__init__(
            self,
            f=f, R_0=R_0,
            rho_s=rho_s, c_s=c_s, eta_s=eta_s, zeta_s=zeta_s,
            rho_f=rho_f, c_f=c_f, eta_f=eta_f, zeta_f=zeta_f,
            p_0=p_0, wave_type=wave_type, position=position,
        )
        BaseScatteringDoinikov1994.__init__(self, N_max=N_max)

        # Dependent variables
        self._alpha_n = ActiveListVariable(
            self._compute_alpha_n,
            'fluid scattering coefficient alpha_n',
        )
        self._beta_n = ActiveListVariable(
            self._compute_beta_n,
            'fluid scattering coefficient beta_n',
        )
        self._alpha_hat_n = ActiveListVariable(
            self._compute_alpha_hat_n,
            'sphere scattering coefficient alpha_hat_n',
        )
        self._beta_hat_n = ActiveListVariable(
            self._compute_beta_hat_n,
            'sphere scattering coefficient beta_hat_n',
        )

    def __repr__(self):  # pragma: no cover
        return (
            f'Doinikov1994Compressible.ScatteringFiels(f={self.f}, '
            f'R_0={self.R_0}, '
            f'rho_s={self.rho_s}, c_s={self.c_s}, '
            f'eta_s={self.eta_s}, zeta_s={self.zeta_s}, '
            f'rho_f={self.rho_f}, c_f={self.c_f}, '
            f'eta_f={self.eta_f}, zeta_f={self.zeta_f}, '
            f'p_0={self.p_0}, position={self.position}, {self.wave_type}, '
            f'N_max={self.N_max})'
        )

    # -----------------------------------------------------
    # Scattering coefficients fluid
    # -----------------------------------------------------

    def alpha_n(self, n: int) -> complex:
        """ coefficient :math:`\\alpha_n` (3.13) and (3.20)

        :param n: order
        """
        return self._alpha_n.item(n)

    def _compute_alpha_n(self, n: int) -> complex:
        # computation according to (3.13), (3.14) and (3.20)
        if n == 0:
            tmp1 = 4 * (self.eta_f - self.eta_s) * self.x * self.x_hat
            tmp1 *= Bf.besselj(1, self.x_hat)

            tmp2 = 1j * self.omega * self.R_0**2

            # numerator
            num = self.rho_f * self.x_hat
            num *= Bf.besselj(0, self.x) * Bf.besselj(1, self.x_hat)
            num -= self.rho_s * self.x * (
                Bf.besselj(1, self.x) *
                Bf.besselj(0, self.x_hat)
            )
            num *= tmp2
            num -= tmp1 * Bf.besselj(1, self.x)

            # denominator
            den = self.rho_s * self.x
            den *= Bf.hankelh1(1, self.x) * Bf.besselj(0, self.x_hat)
            den -= self.rho_f * self.x_hat * (
                Bf.hankelh1(0, self.x) * Bf.besselj(1, self.x_hat)
            )
            den *= tmp2
            den += tmp1 * Bf.hankelh1(1, self.x)

            new_value = num / den
        else:
            new_value = self.det_M_n(n, 0) / self.det_M_n(n)

        return new_value

    def beta_n(self, n: int) -> complex:
        """ coefficient :math:`\\beta_n` (3.13) and (3.20)

        :param n: order
        """
        return self._beta_n.item(n)

    def _compute_beta_n(self, n: int) -> complex:
        # computation according to (3.13), (3.15) and (3.21)
        if n == 0:
            return 0
        else:
            return self.det_M_n(n, 1) / self.det_M_n(n)

    # -----------------------------------------------------
    # Scattering coefficients sphere
    # -----------------------------------------------------

    def alpha_hat_n(self, n: int) -> complex:
        """ coefficient :math:`\\alpha_hat_n` (3.13) and (3.20)

        :param n: order
        """
        return self._alpha_hat_n.item(n)

    def _compute_alpha_hat_n(self, n: int) -> complex:
        # computation according to (3.13), (3.14) and (3.20)

        if n == 0:
            tmp1 = 4 * (self.eta_f - self.eta_s) * self.x * self.x_hat
            tmp2 = 1j * self.omega * self.R_0**2

            # numerator
            num = Bf.besselj(0, self.x) * Bf.hankelh1(1, self.x)

            num -= Bf.besselj(1, self.x) * Bf.hankelh1(0, self.x)

            num *= tmp2 * self.x * self.rho_f

            # denominator
            den = self.rho_s * self.x
            den *= Bf.hankelh1(1, self.x) * Bf.besselj(0, self.x_hat)

            den -= self.rho_f * self.x_hat * (
                Bf.hankelh1(0, self.x) *
                Bf.besselj(1, self.x_hat)
            )
            den *= tmp2
            den += tmp1 * (Bf.hankelh1(1, self.x) * Bf.besselj(1, self.x_hat))

            new_value = num / den
        else:
            new_value = self.det_M_n(n, 2) / self.det_M_n(n)
        return new_value

    def beta_hat_n(self, n: int) -> complex:
        """ coefficient :math:`\\beta_hat_n` (3.13) and (3.20)

        :param n: order
        """
        return self._beta_hat_n.item(n)

    def _compute_beta_hat_n(self, n: int) -> complex:
        # computation according to (3.13), (3.15) and (3.21)
        if n == 0:
            return 0
        else:
            return self.det_M_n(n, 3) / self.det_M_n(n)

    # -----------------------------------------------------
    # Methods
    # -----------------------------------------------------

    def radial_particle_velocity(
        self,
        r: Union[float, np.ndarray, list[float]],
        theta: Union[float, np.ndarray, list[float]],
        t: Union[float, np.ndarray, list[float]],
        mode: Optional[int] = None,
    ) -> complex:
        """Particle velocity in radial direction

        Returns the value of the particle velocity
        in radial direction in [m/s]

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        :param mode: mode to be plotted, if `None` then sum of all mode up
                     to `N_max`
        """
        r, theta, t = InputHandler.handle_input(
            r, theta, t, self.R_0,
            inside_sphere=True,
        )

        def radial_velocity(n: int, r: float) -> complex:
            out = self.k_s * self.alpha_hat_n(n)
            out *= Bf.d1_besselj(n, r * self.k_s)

            arg = r * self.k_vs
            out -= n * (n + 1) / r * self.beta_hat_n(n) * Bf.besselj(n, arg)
            out *= self.A_in(n)
            return out

        return self.radial_mode_superposition(
            radial_velocity, r, theta, t, mode,
        )

    def tangential_particle_velocity(
            self,
            r: Union[float, np.ndarray, list[float]],
            theta: Union[float, np.ndarray, list[float]],
            t: Union[float, np.ndarray, list[float]],
            mode: Optional[int] = None,
    ) -> complex:
        """Particle velocity in tangential direction

        Returns the value of the particle velocity
        in tangential direction in [m/s]

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        :param mode: mode to be plotted, if `None` then sum of all mode up
                     to `N_max`
        """
        r, theta, t = InputHandler.handle_input(
            r, theta, t, self.R_0,
            inside_sphere=True,
        )

        def tangential_velocity(n: int, r: float) -> complex:
            out = Bf.besselj(n, self.k_vs * r)
            out += r * self.k_vs * Bf.d1_besselj(n, self.k_vs * r)
            out *= -self.beta_hat_n(n)
            out += self.alpha_hat_n(n) * Bf.besselj(n, self.k_s * r)
            out *= self.A_in(n) / r
            return out

        return self.tangential_mode_superposition(
            tangential_velocity, r, theta, t, mode,
        )


if __name__ == '__main__':
    pass
