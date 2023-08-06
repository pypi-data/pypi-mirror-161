from typing import Optional, Union

import numpy as np

from osaft import log
from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import LegendreFunctions as Leg
from osaft.core.functions import exp
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import ActiveListVariable
from osaft.solutions.base_scattering import (
    BaseScattering,
    BaseScatteringRigidParticle,
)
from osaft.solutions.king1934.base import BaseKing


class ScatteringField(BaseKing, BaseScatteringRigidParticle, BaseScattering):
    """Scattering field class for King (1934)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: Type of incident wave (traveling/standing)
    :param position: Position in the standing wave field [rad]
    :param N_max: Highest order mode included in the computation [-]
    """

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float,
        rho_f: float, c_f: float,
        p_0: float, wave_type: WaveType, position: Optional[float] = None,
        N_max: int = 5,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        BaseKing.__init__(
            self, f, R_0, rho_s, rho_f, c_f, p_0,
            wave_type, position,
        )
        BaseScattering.__init__(self, N_max)

        # Dependent variables
        self._A_dash_n = ActiveListVariable(self._compute_A_dash_n, 'A_dash_n')
        self._A_dash_n.is_computed_by(
            self.field._A_in, self._alpha,
            self._rho_tilde,
        )
        if type(self) is ScatteringField:
            log.info(str(self))
            log.debug(repr(self))

    def __repr__(self):
        return (
            f'{type(self)}(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, c_f={self.c_f}, '
            f'p_0={self.p_0}, position={self.position}, '
            f'wave_type={self.wave_type}, N_max={self.N_max})'
        )

    def __str__(self):
        out = 'King\'s solution to the Scattering field'
        out += ' with following properties: \n'
        out += SF.get_str_text('Wave type', '', self.wave_type, '')
        out += SF.get_str_text('Frequency', 'f', self.f, 'Hz')
        out += SF.get_str_text('Pressure', 'p_0', self.p_0, 'Pa')
        out += SF.get_str_text(
            'Position', 'd',
            self.position, 'rad',
        )
        out += SF.get_str_text(
            'Wavelength', 'lambda',
            self.field.lambda_f, 'm',
        )

        out += 'Fluid\n'
        out += SF.get_str_text(
            'Density', 'rho_f',
            self.rho_f, 'kg/m^3',
        )
        out += SF.get_str_text(
            'Sound Speed', 'c_0',
            self.c_f, 'm/s',
        )
        out += SF.get_str_text(
            'Compressibility', 'kappa_f',
            self.kappa_f, '1/Pa',
        )

        out += 'Particle\n'
        out += SF.get_str_text(
            'Radius', 'R_0',
            self.R_0, 'm',
        )
        out += SF.get_str_text(
            'Density', 'rho_s',
            self.rho_s, 'kg/m^3',
        )
        out += 'Other\n'
        out += SF.get_str_text(
            '#modes', 'N_max',
            self.N_max, None,
        )
        return out

    # -----------------------------------------------------
    # User-facing Methods
    # -----------------------------------------------------

    def particle_velocity(self, t: float) -> float:
        """Particle velocity

        Returns the value of the particle velocity
        in the direction of the axis of rotational
        symmetry of the radiation field in [m/s]

        :param t: time [s]
        """

        out = exp(- 1j * self.omega * t) * self.A_in(1) / self.alpha ** 3
        out *= self.k_f / self.rho_tilde
        out /= (self.F_n(1, self.alpha) - 1j * self.G_n(1, self.alpha))
        return out

    # -----------------------------------------------------
    # Coefficients
    # -----------------------------------------------------

    @staticmethod
    def phi_n(n: int, arg: float) -> complex:
        r"""From King equation (22)

        Returns :math:`\phi_n`

        :param n: mode
        :param arg: argument for spherical Bessel function
        """
        return - Bf.bessely(n, arg) * arg ** (- n)

    @staticmethod
    def psi_n(n: int, arg: float) -> complex:
        r"""From King equation (22)

        Returns :math:`\psi_n`

        :param n: mode
        :param arg: argument for spherical Bessel function
        """
        return Bf.besselj(n, arg) * arg ** (- n)

    def F_n(self, n: int, arg: float) -> float:
        """From King equation (30) and (31)

        Returns :math:`F_n`

        :param n: mode
        :param arg: argument for spherical Bessel function
        """
        out = self.alpha ** 2 * self.phi_n(n + 1, arg)
        if n == 1:
            out -= (1 - 1 / self.rho_tilde) * self.phi_n(n, arg)
        else:
            out -= n * self.phi_n(n, arg)

        return out

    def G_n(self, n: int, arg: float) -> complex:
        """From King equation (30) and (31)

        Returns :math:`G_n`

        :param n: mode
        :param arg: argument for spherical Bessel function
        """
        out = self.alpha ** 2 * self.psi_n(n + 1, arg)
        if n == 1:
            out -= (1 - 1 / self.rho_tilde) * self.psi_n(n, arg)
        else:
            out -= n * self.psi_n(n, arg)

        return out

    def A_dash_n(self, n: int) -> complex:
        r"""From King equation (21), (28)
        potential from 28 to form of 21

        Returns Scattering field coefficient :math:`A^{\prime}_{n}`

        :param n: mode number
        """
        return self._A_dash_n.item(n)

    def _compute_A_dash_n(self, n: int) -> complex:
        out = - self.A_in(n) * self.G_n(n, self.alpha)
        out /= (self.G_n(n, self.alpha) + 1j * self.F_n(n, self.alpha))
        return out

    # -----------------------------------------------------
    # Methods
    # -----------------------------------------------------

    def Phi_scattering(
        self,
        r: Union[float, np.ndarray, list[float]],
        theta: Union[float, np.ndarray, list[float]],
        t: Union[float, np.ndarray, list[float]],
    ) -> complex:
        r"""King equation (28) for scattering potential
        :math:`\Phi_{\mathrm{scattering}}`

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        """
        def Phi_n(n: int):
            num = - self.G_n(n, self.alpha)
            num *= self.A_in(n) * Bf.hankelh2(n, r * self.k_f)
            denom = self.G_n(n, self.alpha)
            denom += 1j * self.F_n(n, self.alpha)
            coefficient = num / denom

            out = exp(-1j * self.omega * t)
            out *= Leg.cos_monomial(n, theta, coefficient)
            return out

        out = 0
        for n in range(self.N_max + 1):
            out += Phi_n(n)
        return out

    def Phi_incident(
        self,
        r: Union[float, np.ndarray, list[float]],
        theta: Union[float, np.ndarray, list[float]],
        t: Union[float, np.ndarray, list[float]],
    ) -> complex:
        r"""King equation (28) for scattering potential
        :math:`\Phi_{\mathrm{incident}}`

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        """
        def Phi_n(n: int):
            coefficient = self.A_in(n) * Bf.besselj(n, r * self.k_f)
            out = exp(-1j * self.omega * t)
            out *= Leg.cos_monomial(n, theta, coefficient)
            return out

        out = 0
        for n in range(self.N_max + 1):
            out += Phi_n(n)
        return out

    def V_r_sc(
        self, n: int,
        r: Union[float, np.ndarray, list[float]],
    ) -> complex:
        """Implements :meth:`osaft.solutions.base_scattering.BaseScattering.\
V_r_sc`
        """
        return self.A_dash_n(n) * self.k_f * Bf.d1_hankelh2(n, self.k_f * r)

    def V_theta_sc(
        self, n: int,
        r: Union[float, np.ndarray, list[float]],
    ) -> complex:
        """Implements :meth:`osaft.solutions.base_scattering.BaseScattering.\
V_theta_sc`
        """
        return self.A_dash_n(n) * Bf.hankelh2(n, self.k_f * r) / r


if __name__ == '__main__':
    pass
