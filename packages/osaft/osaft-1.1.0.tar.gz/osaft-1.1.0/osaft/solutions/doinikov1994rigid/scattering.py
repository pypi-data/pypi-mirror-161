from __future__ import annotations

from typing import Optional, Union

from osaft import log
from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import exp
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import ActiveListVariable, ActiveVariable
from osaft.solutions.base_scattering import BaseScatteringRigidParticle
from osaft.solutions.basedoinikov1994.scattering import (
    BaseScatteringDoinikov1994,
)
from osaft.solutions.doinikov1994rigid.base import BaseDoinikov1994Rigid


class ScatteringField(
    BaseDoinikov1994Rigid, BaseScatteringRigidParticle,
    BaseScatteringDoinikov1994,
):
    """Scattering field class for Doinikov (viscous fluid-rigid sphere; 1994)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param eta_f: shear viscosity [Pa s]
    :param zeta_f: bulk viscosity [Pa s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: Type of wave, traveling or standing
    :param position: Position in the standing wave field [rad]
    :param N_max: Highest order mode included in the computation [-]
    """

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float,
        rho_f: float, c_f: float,
        eta_f: float, zeta_f: float,
        p_0: float,
        wave_type: Optional[WaveType] = WaveType.STANDING,
        position: Optional[float] = None,
        N_max: int = 5,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        BaseDoinikov1994Rigid.__init__(
            self,
            f=f, R_0=R_0, rho_s=rho_s,
            rho_f=rho_f, c_f=c_f, eta_f=eta_f, zeta_f=zeta_f,
            p_0=p_0, wave_type=wave_type, position=position,
        )
        BaseScatteringDoinikov1994.__init__(self, N_max=N_max)

        if type(self) is ScatteringField:
            log.debug(repr(self))
            log.info(str(self))

        # Dependent variables
        self._alpha_n = ActiveListVariable(
            self._compute_alpha_n,
            'scattering coefficient alpha_n',
        )

        self._beta_n = ActiveListVariable(
            self._compute_beta_n,
            'scattering coefficient beta_n',
        )

        self._gamma_n = ActiveListVariable(self._compute_gamma_n)
        self._xi_n = ActiveListVariable(self._compute_xi_n)

        self._mu_1 = ActiveVariable(self._compute_mu_1)
        self._mu_2 = ActiveVariable(self._compute_mu_2)
        self._mu_3 = ActiveVariable(self._compute_mu_3)
        self._mu_4 = ActiveVariable(self._compute_mu_4)

        # define dependencies
        self._mu_1.is_computed_by(
            self._rho_t, self._x,
        )
        self._mu_2.is_computed_by(
            self._rho_t, self._x,
        )
        self._mu_3.is_computed_by(
            self._rho_t, self._x_v,
        )
        self._mu_4.is_computed_by(
            self._rho_t, self._x_v, self._x,
            self._mu_2, self._mu_3,
        )

        self._gamma_n.is_computed_by(self._x_v)

        self._xi_n.is_computed_by(
            self._x, self._x_v, self._gamma_n,
        )

        self._alpha_n.is_computed_by(
            self._gamma_n, self._xi_n, self._x, self._x_v,
            self._mu_1, self._mu_3, self._mu_4,
        )

        self._beta_n.is_computed_by(
            self._gamma_n, self._xi_n, self._x, self._x_v,
            self._mu_1, self._mu_2, self._mu_4,
        )

    def __repr__(self):
        return (
            f'Donikov1994Rigid.ScatteringFiels(f={self.f}, '
            f'R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, c_f={self.c_f}, '
            f'eta_f={self.eta_f}, zeta_f={self.zeta_f}, '
            f'p_0={self.p_0}, position={self.position}, {self.wave_type}, '
            f'N_max={self.N_max})'
        )

    def __str__(self):
        out = 'Doinikov\'s(1994 rigid - viscous) solution '
        out += 'to the scattering field'
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
            'Viscosity', 'eta_f',
            self.eta_f, 'Pa s',
        )
        out += SF.get_str_text(
            'Bulk Viscosity', 'zeta_f',
            self.zeta_f, 'Pa s',
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
    # Dependent Variables
    # -----------------------------------------------------

    def xi_n(self, n: int) -> complex:
        """ coefficient :math:`\\xi_n` (3.22)

        :param n: order
        """
        return self._xi_n.item(n)

    def _compute_xi_n(self, n: int) -> complex:
        # computation according to (3.13) and (3.20)
        new_value = -n * (n + 1)
        new_value *= Bf.hankelh1(n, self.x) * Bf.hankelh1(n, self.x_v)
        new_value += self.x * Bf.d1_hankelh1(n, self.x) * self.gamma_n(n)

        return new_value

    def gamma_n(self, n: int) -> complex:
        """ coefficient :math:`\\gamma_n` (3.22)

        :param n: order
        """
        return self._gamma_n.item(n)

    def _compute_gamma_n(self, n: int) -> complex:
        # computation according to (3.13) and (3.20)
        new_value = Bf.hankelh1(n, self.x_v)
        new_value += self.x_v * Bf.d1_hankelh1(n, self.x_v)
        return new_value

    def alpha_n(self, n: int) -> complex:
        """ coefficient :math:`\\alpha_n` (3.13) and (3.20)

        :param n: order
        """
        return self._alpha_n.item(n)

    def _compute_alpha_n(self, n: int) -> complex:
        # computation according to (3.13), (3.14) and (3.20)
        if n == 0:
            new_value = -Bf.besselj(1, self.x) / Bf.hankelh1(1, self.x)
        elif n == 1:
            new_value = -2 * (1 - self.rho_t**2)
            new_value *= Bf.besselj(1, self.x) * Bf.hankelh1(1, self.x_v)
            new_value -= self.mu_1 * self.mu_3
            new_value /= self.mu_4
        else:
            new_value = n * (n + 1) * Bf.besselj(n, self.x)
            new_value *= Bf.hankelh1(n, self.x_v)

            new_value -= self.x * (
                self.gamma_n(n) *
                Bf.d1_besselj(n, self.x)
            )
            new_value /= self.xi_n(n)
        return new_value

    def beta_n(self, n: int) -> complex:
        """ coefficient :math:`\\beta_n` (3.13) and (3.20)

        :param n: order
        """
        return self._beta_n.item(n)

    def _compute_beta_n(self, n: int) -> complex:
        # computation according to (3.13), (3.15) and (3.21)

        if n == 0:
            new_value = 0.0
        elif n == 1:
            new_value = self.mu_1 * Bf.hankelh1(1, self.x)
            new_value -= self.mu_2 * Bf.besselj(1, self.x)

            new_value *= -(1 - self.rho_t)
            new_value /= self.mu_4
        else:
            new_value = Bf.d1_besselj(n, self.x) * Bf.hankelh1(n, self.x)
            new_value -= Bf.besselj(n, self.x) * Bf.d1_hankelh1(n, self.x)
            new_value *= self.x
            new_value /= -self.xi_n(n)

        return new_value

    @property
    def mu_1(self) -> complex:
        """ :math:`\\mu_1` according to (3.16)
        """
        return self._mu_1.value

    def _compute_mu_1(self) -> complex:
        out = self.rho_t * Bf.besselj(1, self.x)
        out -= self.x * Bf.d1_besselj(1, self.x)
        return out

    @property
    def mu_2(self) -> complex:
        """ :math:`\\mu_2` according to (3.17)
        """
        return self._mu_2.value

    def _compute_mu_2(self) -> complex:
        out = self.rho_t * Bf.hankelh1(1, self.x)
        out -= self.x * Bf.d1_hankelh1(1, self.x)
        return out

    @property
    def mu_3(self) -> complex:
        """ :math:`\\mu_3` according to (3.18)
        """
        return self._mu_3.value

    def _compute_mu_3(self) -> complex:
        out = (1 + 2 * self.rho_t) * Bf.hankelh1(1, self.x_v)
        out += self.x_v * Bf.d1_hankelh1(1, self.x_v)
        return out

    @property
    def mu_4(self) -> complex:
        """ :math:`\\mu_4` according to (3.19)
        """
        return self._mu_4.value

    def _compute_mu_4(self) -> complex:
        out = 2 * (1 - self.rho_t**2)
        out *= Bf.hankelh1(1, self.x)
        out *= Bf.hankelh1(1, self.x_v)
        out += self.mu_2 * self.mu_3
        return out

    # -----------------------------------------------------
    # Methods
    # -----------------------------------------------------

    def particle_velocity(self, t: float) -> complex:
        """Particle velocity

        Returns the value of the particle velocity
        in the direction of the axis of rotational
        symmetry of the radiation field in [m/s]

        :param t: time [s]
        """

        out = Bf.besselj(1, self.x) + self.alpha_n(1) * Bf.hankelh1(1, self.x)
        out += 2 * self.beta_n(1) * Bf.hankelh1(1, self.x_v)
        out *= self.rho_t * self.A_in(1) * self.k_f
        out /= self.x
        out *= exp(-1j * self.omega * t)
        return out


if __name__ == '__main__':
    pass
