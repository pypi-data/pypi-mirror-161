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
from osaft.solutions.hasegawa1969.base import BaseHasegawa


class ScatteringField(BaseHasegawa, BaseScattering):
    """Scattering field class for Hasegawa (1969)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the solid elastic sphere [kg/m^3]
    :param E_s: Young's modulus [Pa]
    :param nu_s: Poisson's ratio of the solid sphere [-]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: progressive wave
    :param position: Position in the standing wave field [rad]
    :param N_max: Highest order mode included in the computation [-]
    """

    def __init__(
            self, f: Union[Frequency, float],
            R_0: Union[Sphere, float],
            rho_s: float, nu_s: float, E_s: float,
            rho_f: float, c_f: float,
            p_0: float, wave_type: WaveType,
            position: Optional[float] = None,
            N_max: int = 5,
    ) -> None:
        """Constructor method
        """
        BaseHasegawa.__init__(
            self, f, R_0,
            rho_s, E_s, nu_s,
            rho_f, c_f,
            p_0, wave_type, position,
        )
        BaseScattering.__init__(self, N_max)

        log.info('Create ScatteringField')

        # Dependent Variables
        self._c_n = ActiveListVariable(
            self._compute_c_n,
            'Coefficient c_n'
            ' for scattered potential',
        )

        self._c_n_A = ActiveListVariable(
            self._compute_c_n_A,
            'Coefficient c_n'
            ' for scattered potential',
        )

        self._a_n = ActiveListVariable(
            self._compute_a_n,
            'Coefficient a_n'
            ' for potential inside particle',
        )

        self._b_n = ActiveListVariable(
            self._compute_b_n,
            'Coefficient b_n'
            ' for potential inside particle',
        )

        # Dependencies
        self._c_n.is_computed_by(
            self._lambda_rho, self.fluid._k_f,
            self.scatterer._k_l, self.scatterer._k_t,
            self.sphere._R_0, self.scatterer._nu_s,
        )
        self._c_n_A.is_computed_by(
            self.field._A_in, self._c_n,
        )
        self._a_n.is_computed_by(
            self.fluid._k_f,
            self.scatterer._k_l, self.scatterer._k_t,
            self.sphere._R_0, self.field._A_in, self._c_n,
        )
        self._b_n.is_computed_by(
            self.fluid._k_f,
            self.scatterer._k_l, self.scatterer._k_t,
            self.sphere._R_0, self.field._A_in, self._c_n,
        )

        if type(self) is ScatteringField:
            log.info(str(self))
            log.debug(repr(self))

    def __repr__(self):
        return (
            f'{type(self)}(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, '
            f'c_f={self.c_f}, E_s={self.E_s}, nu_s={self.nu_s}'
            f'p_0={self.p_0}, position={self.position}, '
            f'wave_type={self.wave_type}, N_max={self.N_max})'
        )

    def __str__(self):
        out = 'Hasegawa\'s solution to the Scattering field'
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
            'Young\'s modulus', 'E_s',
            self.E_s, 'Pa',
        )
        out += SF.get_str_text(
            'Poisson\'s ratio', 'nu_s',
            self.nu_s, 'Pa',
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
            term1 = (
                self.k_s_l * self.a_n(l)
                * Bf.d1_besselj(l, self.k_s_l * x)
            )
            term2 = (
                l * (l + 1) / x * self.b_n(l)
                * Bf.besselj(l, self.k_s_t * x)
            )
            return term1 - term2

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
            term1 = self.a_n(l) * Bf.besselj(l, self.k_s_l * x)
            term2 = self.b_n(l) * (
                Bf.besselj(l, self.k_s_t * x) +
                self.k_s_t * x * Bf.d1_besselj(l, self.k_s_t * x)
            )
            return (term1 - term2) / x

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
        return self.c_n_A(n) * self.k_f * Bf.d1_hankelh1(n, self.k_f * r)

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
        return self.c_n_A(n) * Bf.hankelh1(n, self.k_f * r) / r

    # -------------------------------------------------------------------------
    # Coefficients
    # -------------------------------------------------------------------------
    def c_n(self, n: int) -> complex:
        """Coefficient :math:`c_n` [-]

        (Eq. 7)

        :param n: mode [-]
        """
        return self._c_n.item(n)

    def c_n_A(self, n: int) -> complex:
        """Coefficient :math:`c_n` [m]

        (Eq. 7)

        :param n: mode [-]
        """
        return self._c_n_A.item(n)

    def a_n(self, n: int) -> complex:
        """Coefficient :math:`a_n` [m]

        (determined by boundary conditions)

        :param n: mode [-]
        """
        return self._a_n.item(n)

    def b_n(self, n: int) -> complex:
        """Coefficient :math:`b_n` [m]

        (determined by boundary conditions)

        :param n: mode [-]
        """
        return self._b_n.item(n)

    def _compute_c_n(self, n: int) -> complex:
        """ Compute c_n according to (8, 9).
        """
        term0 = 1 / 2 / self.lambda_rho * self.x_s_t ** 2
        term1 = self.x_s_l * Bf.d1_besselj(n, self.x_s_l)
        term2 = term1 - Bf.besselj(n, self.x_s_l)
        term3 = 2 * n * (n + 1) * Bf.besselj(n, self.x_s_t)
        term4 = (n + 2) * (n - 1) * Bf.besselj(n, self.x_s_t)
        term4 += self.x_s_t ** 2 * Bf.d2_besselj(n, self.x_s_t)
        term5 = self.nu_s / (1 - 2 * self.nu_s) * Bf.besselj(n, self.x_s_l)
        term5 -= Bf.d2_besselj(n, self.x_s_l)
        term5 *= self.x_s_l ** 2
        term6 = -2 * n * (n + 1) * self.x_s_t * Bf.d1_besselj(n, self.x_s_t)
        term6 += term3

        F_n = term0 * ((term1 / term2) - (term3 / term4))
        F_n /= (term5 / term2) - (term6 / term4)

        num = self.x_f * Bf.d1_besselj(n, self.x_f)
        num -= F_n * Bf.besselj(n, self.x_f)
        denom = F_n * Bf.hankelh2(n, self.x_f)
        denom -= self.x_f * Bf.d1_hankelh2(n, self.x_f)

        return num / denom

    def _compute_c_n_A(self, n: int) -> complex:
        """ Compute c_n according to (8, 9), multiplied with the incident
        amplitude
        """
        out = self.c_n(n)
        out *= self.A_in(n)
        return out

    def _compute_a_n(self, n: int) -> complex:
        """Compute a_n such that boundary conditions (shear stress 0
        and radial velocity component equal to field at r = R_0),
        multiplied with the incident amplitude. Need this for eq. (3)
        """

        j = Bf.besselj
        dj = Bf.d1_besselj
        ddj = Bf.d2_besselj
        dh = Bf.d1_hankelh1
        cn = self.c_n_A(n)
        An = self.A_in(n)
        x = self.x_f
        x1 = self.x_s_l
        x2 = self.x_s_t

        num = x * ((n ** 2 + n - 1) * x2 * dj(n, x2) - j(n, x2))
        num *= An * dj(n, x) + cn * dh(n, x)

        denom = (n ** 2 + n - 1) * x2 * dj(n, x2) - (n ** 2 + n + 1) * j(n, x2)
        denom *= x1 * dj(n, x1)
        denom += n * (n + 1) * j(n, x2) * (j(n, x1) - x1 ** 2 * ddj(n, x1))

        return num / denom

    def _compute_b_n(self, n: int) -> complex:
        """Second part of the solution to the problem described in _compute_a_n
        """
        j = Bf.besselj
        dj = Bf.d1_besselj
        ddj = Bf.d2_besselj
        dh = Bf.d1_hankelh1
        cn = self.c_n_A(n)
        An = self.A_in(n)
        x = self.x_f
        x1 = self.x_s_l
        x2 = self.x_s_t

        num = - x * (x1 * (x1 * ddj(n, x1) + dj(n, x1)) - j(n, x1))
        num *= (An * dj(n, x) + cn * dh(n, x))

        denom = (n ** 2 + n + 1) * j(n, x2) - (n ** 2 + n - 1) * x2 * dj(n, x2)
        denom *= x1 * dj(n, x1)
        denom += n * (n + 1) * j(n, x2) * (x1 ** 2 * ddj(n, x1) - j(n, x1))

        return num / denom


if __name__ == '__main__':
    pass
