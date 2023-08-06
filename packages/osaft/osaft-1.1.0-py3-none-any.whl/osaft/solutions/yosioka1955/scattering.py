from collections.abc import Sequence
from typing import Optional, Union

from osaft import log
from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.geometries import Sphere
from osaft.core.helper import InputHandler
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import ActiveListVariable
from osaft.solutions.base_scattering import BaseScattering
from osaft.solutions.yosioka1955.base import BaseYosioka


class ScatteringField(BaseYosioka, BaseScattering):
    """Scattering field class for Yosioka & Kawasima (1955)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
    :param c_s: Speed of sound of the particle [m/s]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: either standing or progressive wave
    :param position: Position in the standing wave field [rad]
    :param N_max: Highest order mode included in the computation [-]
    """

    def __init__(
        self, f: Union[Frequency, float],
        R_0: Union[Sphere, float],
        rho_s: float, c_s: float, rho_f: float, c_f: float,
        p_0: float, wave_type: WaveType,
        position: Optional[float] = None,
        N_max: int = 5,
    ) -> None:
        """Constructor method
        """
        BaseYosioka.__init__(
            self, f, R_0,
            rho_s, c_s, rho_f, c_f,
            p_0, wave_type, position,
        )
        BaseScattering.__init__(self, N_max)

        log.info('Create ScatteringField')

        # Dependent Variables
        self._A_n = ActiveListVariable(
            self._compute_A_n,
            'Coefficient A_n'
            ' for scattered potential',
        )

        self._B_n = ActiveListVariable(
            self._compute_B_n,
            'Coefficient B_n'
            ' for potential inside particle',
        )

        # Dependencies
        self._A_n.is_computed_by(
            self._lambda_rho, self.fluid._k_f,
            self.scatterer._k_f, self.sphere._R_0, self.field._A_in,
        )
        self._B_n.is_computed_by(
            self._lambda_rho, self.fluid._k_f,
            self.scatterer._k_f, self.sphere._R_0, self.field._A_in,
        )

        if type(self) is ScatteringField:
            log.info(str(self))
            log.debug(repr(self))

    def __repr__(self):
        return (
            f'{type(self)}(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, '
            f'c_f={self.c_f}, c_s={self.c_s}'
            f'p_0={self.p_0}, position={self.position}, '
            f'wave_type={self.wave_type}, N_max={self.N_max})'
        )

    def __str__(self):
        out = 'Yosioka\'s solution to the Scattering field'
        out += ' with following properties: \n'
        out += SF.get_str_text('Wave type', '', self.wave_type, '')
        out += SF.get_str_text('Frequency', 'f', self.f, 'Hz')
        out += SF.get_str_text('Pressure', 'p_0', self.p_0, 'Pa')
        out += SF.get_str_text(
            'Position', 'd',
            self.position, 'Pa',
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
            'Sound Speed', 'c_f',
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
        out += SF.get_str_text(
            'Speed of sound', 'c_s',
            self.c_s, 'm/s',
        )
        out += 'Other\n'
        out += SF.get_str_text(
            '#modes', 'N_max',
            self.N_max, None,
        )
        return out

    # -------------------------------------------------------------------------
    # User-facing functions
    # -------------------------------------------------------------------------

    def radial_particle_velocity(
        self,
        r: Union[float, Sequence[float]],
        theta: Union[float, Sequence[float]],
        t: Union[float, Sequence[float]],
        mode: Optional[int] = None,
    ) -> Union[float, Sequence[float]]:
        """Radial particle velocity [m/s]

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        :param mode: mode
        """

        def radial_func(l, x):
            return self.B_n(l) * self.k_s * Bf.d1_besselj(l, self.k_s * x)
        r, theta, t = InputHandler.handle_input(
            r, theta, t, self.R_0,
            inside_sphere=True,
        )
        out = self.radial_mode_superposition(radial_func, r, theta, t, mode)
        return out

    def tangential_particle_velocity(
        self,
        r: Union[float, Sequence[float]],
        theta: Union[float, Sequence[float]],
        t: Union[float, Sequence[float]],
        mode: Optional[int] = None,
    ) -> Union[float, Sequence[float]]:
        """Tangential particle velocity [m/s]

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        :param mode: mode
        """

        def radial_func(l, x):
            return self.B_n(l) * Bf.besselj(l, self.k_s * x) / x
        r, theta, t = InputHandler.handle_input(
            r, theta, t, self.R_0,
            inside_sphere=True,
        )
        out = self.tangential_mode_superposition(
            radial_func, r, theta, t,
            mode,
        )
        return out

    # -------------------------------------------------------------------------
    # Velocity Amplitudes and Velocity Potentials
    # -------------------------------------------------------------------------

    def Phi_1(
        self, r: float, theta: float, t: float,
        mode: Optional[int] = None,
    ) -> complex:
        r"""Fluid velocity potential :math:`\Phi_1` [m^2/s]

        (Eq. 17)

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        :param mode: mode
        """

        return self.Phi_i(r, theta, t, mode) + self.Phi_s(r, theta, t, mode)

    def Phi_i(
        self, r: float, theta: float, t: float,
        mode: Optional[int] = None,
    ) -> complex:
        r"""Fluid velocity potential of the incident field :math:`\Phi_i`
        [m^2/s]

        (Eq. 16, 27)

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        :param mode: mode
        """

        def radial_func(l, x):
            return self.field.A_in(l) * Bf.besselj(l, self.k_f * x)

        out = self.radial_mode_superposition(radial_func, r, theta, t, mode)
        return out

    def Phi_s(
        self, r: float, theta: float, t: float,
        mode: Optional[int] = None,
    ) -> complex:
        r"""Fluid velocity potential of the scattered field :math:`\Phi_s`
        [m^2/s]

        (Eq. 18, 29)

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        :param mode: mode
        """
        def radial_func(l, x):
            return self.A_n(l) * Bf.hankelh2(l, self.k_f * x)

        out = self.radial_mode_superposition(radial_func, r, theta, t, mode)
        return out

    def Phi_star(
        self, r: float, theta: float, t: float,
        mode: Optional[int] = None,
    ) -> complex:
        r"""Particle velocity potential :math:`\Phi^*` [m^2/s]

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        :param mode: mode
        """
        def radial_func(l, x):
            return self.B_n(l) * Bf.besselj(l, self.k_s * x)

        out = self.radial_mode_superposition(radial_func, r, theta, t, mode)
        return out

    def V_r_sc(
        self, n: int,
        r: Union[float, Sequence[float]],
    ) -> Union[complex, Sequence[complex]]:
        """Radial scattering field velocity term of mode `n`
        without Legendre coefficients

        Returns radial scattering field velocity in [m/s]

        :param n: mode
        :param r: radial coordinate [m]
        """
        return (
            self.A_n(n)
            * self.k_f * Bf.d1_hankelh2(n, self.k_f * r)
        )

    def V_theta_sc(
        self, n: int,
        r: Union[float, Sequence[float]],
    ) -> Union[complex, Sequence[complex]]:
        """Tangential scattering field velocity term of mode n
        without Legendre coefficients

        Returns tangential scattering field velocity in [m/s]

        :param n: mode
        :param r: radial coordinate [m]
        """
        return self.A_n(n) * Bf.hankelh2(n, self.k_f * r) / r

    # -------------------------------------------------------------------------
    # Coefficients
    # -------------------------------------------------------------------------

    def A_n(self, n: int) -> complex:
        """Coefficient :math:`A_n` [m^2/s]

        (Eq. 22)

        :param n: mode [-]
        """
        return self._A_n.item(n)

    def B_n(self, n: int) -> complex:
        """Coefficient :math:`B_n` [m^2/s]

        (Eq. 23)

        :param n: mode [-]
        """
        return self._B_n.item(n)

    def _compute_A_n(self, n: int) -> complex:
        """ Compute A_n according to (22), multiplied with the incident
        amplitude
        """
        term1 = (
            self.lambda_rho * self.k_f *
            Bf.besselj(n, self.x_s) * Bf.d1_besselj(n, self.x_f)
        )
        term2 = (
            self.k_s * Bf.d1_besselj(n, self.x_s)
            * Bf.besselj(n, self.x_f)
        )
        term3 = (
            self.k_s * Bf.d1_besselj(n, self.x_s)
            * Bf.hankelh2(n, self.x_f)
        )
        term4 = (
            self.lambda_rho * self.k_f *
            Bf.besselj(n, self.x_s) * Bf.d1_hankelh2(n, self.x_f)
        )
        out = (term1 - term2) / (term3 - term4)
        out *= self.A_in(n)
        return out

    def _compute_B_n(self, n: int) -> complex:
        """Compute B_n according to (23), multiplied with the incident
        amplitude
        """
        out = 1j * self.k_f
        out /= self.x_f ** 2
        term1 = (
            self.k_s * Bf.d1_besselj(n, self.x_s)
            * Bf.hankelh2(n, self.x_f)
        )
        term2 = (
            self.lambda_rho * self.k_f *
            Bf.besselj(n, self.x_s) * Bf.d1_hankelh2(n, self.x_f)
        )
        out /= (term1 - term2)
        out *= self.A_in(n)
        return out


if __name__ == '__main__':
    pass
