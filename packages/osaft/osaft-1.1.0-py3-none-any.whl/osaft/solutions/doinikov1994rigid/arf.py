from __future__ import annotations

from typing import Optional, Union

import numpy as np

from osaft import log
from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.functions import conj, pi, sin, xexpexp1
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import ActiveVariable, PassiveVariable
from osaft.solutions.base_arf import BaseARF
from osaft.solutions.doinikov1994rigid.scattering import ScatteringField


class ARF(ScatteringField, BaseARF):
    """ARF class for Doinikov (viscous fluid-rigid sphere; 1994)

    .. note::
       For all models the condition :math:`|x| \\ll 1` must hold.

       If :attr:`small_viscous_boundary_layer` is set to `True` than in
       addition :math:`|x| \\ll |x_v| \\ll 1` must hold. If set to
       `False` than :math:`|x| \\ll 1 \\ll |x_v|` must hold.

       Both values will be logged in the `info.log` when calling
       :meth:`compute_arf()`. These conditions will not be
       checked at runtime.


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
    :param small_particle_limit: using the limiting cases for the ARF
    :param small_viscous_boundary_layer: :math:`x_v \\ll 1`
    :param large_viscous_boundary_layer: :math:`x_v \\gg 1`
    :param fastened_sphere: use theory of fastened sphere
    :param N_max: Highest order mode
    """

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float,
        rho_f: float, c_f: float,
        eta_f: float, zeta_f: float,
        p_0: float,
        wave_type: WaveType = WaveType.STANDING,
        position: Optional[float] = None,
        small_particle_limit: bool = True,
        small_viscous_boundary_layer: bool = False,
        large_viscous_boundary_layer: bool = False,
        fastened_sphere: bool = False,
        N_max: int = 5,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        super().__init__(
            f=f, R_0=R_0, rho_s=rho_s,
            rho_f=rho_f, c_f=c_f, eta_f=eta_f, zeta_f=zeta_f,
            p_0=p_0, wave_type=wave_type, position=position, N_max=N_max,
        )

        # independent variables
        self._fastened_sphere = PassiveVariable(
            fastened_sphere,
            'fastened sphere limit',
        )

        self._check_small_particle_limit_value(small_particle_limit)
        self._small_particle_limit = PassiveVariable(
            small_particle_limit,
            'small particle limit',
        )
        self._small_viscous_boundary_layer = PassiveVariable(
            small_viscous_boundary_layer,
            'small viscous boundary layer limit',
        )

        self._large_viscous_boundary_layer = PassiveVariable(
            large_viscous_boundary_layer,
            'large viscous boundary layer limit',
        )
        # Coefficients G_n
        self._G_0 = ActiveVariable(self._compute_G_0, 'G_0')
        self._G_1 = ActiveVariable(self._compute_G_1, 'G_1')
        self._G_2 = ActiveVariable(self._compute_G_2, 'G_2')
        self._G_3 = ActiveVariable(self._compute_G_3, 'G_3')
        self._G_4 = ActiveVariable(self._compute_G_4, 'G_4')

        self._G_0.is_computed_by(self._rho_t, self._x_v)
        self._G_1.is_computed_by(self._x_v)
        self._G_2.is_computed_by(self._x_v)
        self._G_3.is_computed_by(self._x_v)
        self._G_4.is_computed_by(self._x_v)

        # Coefficients D_n
        self._D_0 = ActiveVariable(self._compute_D_0, 'D_0')
        self._D_1 = ActiveVariable(self._compute_D_1, 'D_1')

        self._D_0.is_computed_by(self._x, self._x_v, self._G_0, self._G_1)
        self._D_1.is_computed_by(
            self._x, self._x_v, self._G_0, self._G_2, self._G_3, self._G_4,
        )

        # Streaming contribution to the force F_2
        self._F_2_standing = ActiveVariable(
            self._compute_F_2_standing,
            'F_2 standing wave',
        )
        self._F_2_travelling = ActiveVariable(
            self._compute_F_2_travelling,
            'F_2 travelling wave',
        )
        self._F_2_standing.is_computed_by(
            self._x, self._x_v,
            self.fluid._rho_f,
            self.fluid._k_f,
            self.field._abs_pos,
            self.field._abs_A_squared,
        )
        self._F_2_travelling.is_computed_by(
            self._x, self._x_v,
            self.fluid._rho_f,
            self.fluid._k_f,
            self.field._abs_pos,
            self.field._abs_A_squared,
        )

        # logging
        log.debug(repr(self))
        log.info(str(self))

    def __repr__(self):
        return (
            f'Donikov1994Rigid.ARF(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, c_f={self.c_f}, '
            f'eta_f={self.eta_f}, zeta_f={self.zeta_f}, '
            f'p_0={self.p_0}, position={self.position}, {self.wave_type}, '
            f'small_viscous_boundary_layer='
            f'{self.small_viscous_boundary_layer}, '
            f'large_viscous_boundary_layer='
            f'{self.large_viscous_boundary_layer}, '
            f'small_particle_limit={self.small_particle_limit}, '
            f'fastened_sphere= {self.fastened_sphere}, '
            f'N_max={self.N_max})'
        )

    def __str__(self):
        out = 'Doinikovs\'s  (1994) model (viscous fluid-rigid sphere) for the'
        out += ' ARF with the following properties: \n'
        out += 'Limit Cases\n'
        out += SF.get_str_text(
            'Small particle limit',
            'small_particle_limit',
            self.small_particle_limit, None,
        )
        out += SF.get_str_text(
            'Small delta',
            'small_viscous_boundary_layer',
            self.small_viscous_boundary_layer, None,
        )
        out += SF.get_str_text(
            'Large delta',
            'large_viscous_boundary_layer',
            self.large_viscous_boundary_layer, None,
        )
        out += SF.get_str_text(
            'Fastened Sphere',
            'fastened_sphere',
            self.fastened_sphere, None,
        )
        out += 'Backgroundfield\n'
        out += SF.get_str_text('Frequency', 'f', self.f, 'Hz')
        out += SF.get_str_text('Pressure', 'p_0', self.p_0, 'Pa')
        out += SF.get_str_text('Wavetype', 'wave_type', self.wave_type, None)
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
        out += SF.get_str_text(
            'Shear viscosity', 'eta_f',
            self.eta_f, '1/Pa',
        )
        out += SF.get_str_text(
            'Bulk viscosity', 'zeta_f',
            self.zeta_f, '1/Pa',
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
        return out

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def compute_arf(self) -> float:
        """Acoustic radiation fore in [N]

        It logs the current values of :attr:`x` and :attr:`x_v`.

        :raises WrongWaveTypeError: if wrong :attr:`wave_type`
        """
        # Checking wave_type
        self.check_wave_type()

        log.info(
            'Computing the ARF with Doinikov1994Rigid.\n'
            f'x   = {self.x:+.4e} -> |x|   = {np.absolute(self.x):+.4e}\n'
            f'x_v = {self.x_v:+.4e} -> |x_v| = {np.absolute(self.x_v):+.4e}',
        )

        # Small Particle Solutions
        if self.fastened_sphere:
            if self.large_viscous_boundary_layer:
                return self._arf_fastened_large_delta()
            else:
                return self._arf_fastened_small_delta()
        if self.small_viscous_boundary_layer:
            return self._arf_small_particle_small_delta()
        elif self.large_viscous_boundary_layer:
            return self._arf_small_particle_large_delta()
        else:
            return self._arf_small_particle()

    # -------------------------------------------------------------------------
    # Special Expressions for the ARF
    # -------------------------------------------------------------------------

    def _arf_fastened_small_delta(self) -> float:
        # eq. (7.1) for travelling wave and
        # eq. (6.14) w/ \\delta -> 0 for standing
        if self.wave_type == WaveType.TRAVELLING:
            out = 1 - self.norm_delta
            out *= 1.5 * self.norm_delta
        else:
            out = 5 / 6 + 0.75 * self.norm_delta
            out *= self._standing_wave_contribution()
        out *= pi * self.rho_f * self.field.abs_A_squared * self.x_0**3
        return out

    def _arf_fastened_large_delta(self) -> float:
        # eq. (7.5) for travelling wave and eq. (7.6) for standing
        if self.wave_type == WaveType.TRAVELLING:
            out = 1 - 1.2 / self.norm_delta

            out *= -1.5 * self.norm_delta
        else:
            out = 1 + 10 / 27 / self.norm_delta
            out *= 0.9 * self._standing_wave_contribution()
        out *= pi * self.rho_f * self.field.abs_A_squared * self.x_0**3
        out *= self.norm_delta
        return out

    def _arf_small_particle_large_delta(self) -> float:
        # eq. (6.18) for travelling wave and eq. (6.19) for standing
        if self.wave_type == WaveType.TRAVELLING:
            out = (1 - self.rho_t) / self.norm_delta
            out *= -22 / 15
        else:
            out = 11 * (1 - self.rho_t) / 5 / self.norm_delta
            out += 2 * self.rho_t - 1
            out *= self._standing_wave_contribution() / 3
        out *= pi * self.rho_s * self.field.abs_A_squared * self.x_0**3
        return out

    def _arf_small_particle_small_delta(self) -> float:
        # eq. (6.13) for travelling wave and eq. (6.14) for standing
        if self.wave_type == WaveType.TRAVELLING:
            out = 2 + 12 * self.rho_t - 21 * self.rho_t**2 + 7 * self.rho_t**3
            out *= -self.norm_delta / (2 + self.rho_t)
            out += (1 - self.rho_t)**2
            out *= 6 * self.norm_delta
            out /= (2 + self.rho_t)**2
        else:
            out = 3 * (1 - self.rho_t)**2 * self.norm_delta
            out /= (2 + self.rho_t)**2
            out += (5 - 2 * self.rho_t) / (3 * (2 + self.rho_t))
            out *= self._standing_wave_contribution()
        out *= pi * self.rho_f * self.field.abs_A_squared * self.x_0**3
        return out

    def _arf_small_particle(self) -> float:
        """ Acoustic radiation force for the case where the particle radius
        and the viscous boundary layer are small compared to the wavelength
        """
        if self.wave_type == WaveType.TRAVELLING:
            return self._arf_small_particle_travelling()
        else:
            return self._arf_small_particle_standing()

    def _arf_small_particle_travelling(self) -> float:
        """Eq (5.10), (5.12), (6.1), (6.2)
        """
        # F1
        F1 = self.D_0 - self.D_0.conjugate()
        F1 += 2 * (self.D_1 - self.D_1.conjugate())
        F1 *= 3 / 2 * 1j * pi * self.rho_f * self.field.abs_A_squared
        # F_2
        F2 = self.F_2_travelling
        return (F1 + F2).real

    def _arf_small_particle_standing(self) -> float:
        """ Eq (5.15), (5.16), (6.1), (6.2)
        """
        # F1
        sine = sin(2 * self.k_f * self.abs_pos)
        sine_conj = sin(
            2 * self.k_f.conjugate() *
            self.abs_pos,
        )
        F1 = self.D_0 * sine + self.D_0.conjugate() * sine_conj
        F1 -= 2 * (self.D_1 * sine + self.D_1.conjugate() * sine_conj)
        F1 *= 3 / 4 * pi * self.rho_f * self.field.abs_A_squared
        # F_2
        F2 = self.F_2_standing
        return (F1 + F2).real

    def _standing_wave_contribution(self) -> float:
        return sin(2 * self.position)

    # -------------------------------------------------------------------------
    # Streaming Contribution to the ARF
    # -------------------------------------------------------------------------

    @property
    def F_2_standing(self) -> complex:
        """Returns the streaming contribution to the ARF for a standing wave

        (eq 5.17)
        """
        return self._F_2_standing.value

    def _compute_F_2_standing(self) -> complex:
        x = self.x
        x_con = self.x.conjugate()

        first = x - x_con
        first *= sin(
            self.abs_pos * (
                self.k_f +
                conj(self.k_f)
            ),
        )
        first *= sin(x + x_con) / (self.x + x_con)

        second = x + x_con
        second *= sin(
            self.abs_pos * (
                self.k_f -
                conj(self.k_f)
            ),
        )
        second *= sin(x - x_con) / (x - x_con)

        F2 = (first - second)
        F2 *= x * x_con / self.x_v**2
        F2 *= - 3 / 4 * pi * self.rho_f * self.field.abs_A_squared

        return F2

    @property
    def F_2_travelling(self) -> complex:
        """Returns the streaming contribution to the ARF for a standing wave

        (eq 5.12)
        """
        return self._F_2_travelling.value

    def _compute_F_2_travelling(self) -> complex:
        x = self.x
        x_con = self.x.conjugate()

        F2 = x * x_con * (x + x_con) * 1j / self.x_v**2
        F2 *= sin(x - x_con) / (x - x_con)
        F2 *= - 3 / 2 * pi * self.rho_f * self.field.abs_A_squared
        return F2

    # -------------------------------------------------------------------------
    # Coefficients D_n
    # -------------------------------------------------------------------------

    @property
    def D_0(self) -> complex:
        """Approximation for the coefficient D_0 from Eq (6.1)
        """
        return self._D_0.value

    def _compute_D_0(self) -> complex:
        out = self.G_1
        out += self.x_v ** 3 * (12 + self.x_v ** 2) * self._f(self.x_v)
        out *= - self.x ** 3 * self.G_0
        out += 2 * self.x ** 3 / 9
        out += self.x ** 3 / (3 * self.x_v ** 2)
        return out

    @property
    def D_1(self) -> complex:
        """Approximation for the coefficient D_1 from Eq (6.2)
        """
        return self._D_1.value

    def _compute_D_1(self):
        out = - 2 * (1 + 1j) * (9 + self.x_v ** 2)
        out *= self._f(self.x_v - 1j * self.x_v)
        out += 2 * self.G_3 * self._f(self.x_v)
        out += 1j * self.G_4 * self._f(-1j * self.x_v)
        out *= - self.x_v ** 3
        if abs(out.real + self.G_2.real) / abs(self.G_2.real) < 1e-6:
            RuntimeWarning(  # pragma: no cover
                'Possible precision loss detected. '
                'Consider using a limiting case solution.',
            )
        out += self.G_2
        out *= self.x ** 3 * self.G_0.conjugate() / (1 + self.x_v)
        out += self.x ** 3 / (3 * self.x_v ** 2)
        return out

    @staticmethod
    def _f(z):
        return xexpexp1(z)

    # -------------------------------------------------------------------------
    # Coefficients G_n
    # -------------------------------------------------------------------------

    @property
    def G_0(self) -> complex:
        """Approximation to value G_0 from Eq (6.3)
        """
        return self._G_0.value

    def _compute_G_0(self) -> complex:
        denominator = 9 * self.rho_t + 9 * self.rho_t * self.x_v
        denominator += (2 + self.rho_t) * self.x_v ** 2
        out = (1 - self.rho_t) / (72 * denominator)
        return out

    @property
    def G_1(self) -> complex:
        """Approximation to value G_1 from Eq (6.4)
        """
        return self._G_1.value

    def _compute_G_1(self) -> complex:
        out = 48 - 96 * self.x_v + 2 * self.x_v ** 2 - 14 * self.x_v ** 3
        out += self.x_v ** 4 - self.x_v ** 5
        return out

    @property
    def G_2(self) -> complex:
        """Approximation to value G_2 from Eq (6.5)
        """
        return self._G_2.value

    def _compute_G_2(self) -> complex:
        out = 48 + (48 + 192 * 1j / 5) * self.x_v
        out += (122 + 192 * 1j) * self.x_v ** 2 / 5
        out += 42 * (1 - 1j) * self.x_v ** 3 / 5
        out += (49 + 36 * 1j) * self.x_v ** 4 / 10
        out -= (31 - 17 * 1j) * self.x_v ** 5 / 10
        out += (6 + 31 * 1j) * self.x_v ** 6 / 30
        out += (1 + 6 * 1j) * self.x_v ** 7 / 30
        out += 1j * self.x_v ** 8 / 30
        return out

    @property
    def G_3(self) -> complex:
        """Approximation to value G_3 from Eq (6.6)
        """
        return self._G_3.value

    def _compute_G_3(self) -> complex:
        return 3 - 3 * 1j * self.x_v - self.x_v ** 2

    @property
    def G_4(self) -> complex:
        """Approximation to value G_4 from Eq (6.7)
        """
        return self._G_4.value

    def _compute_G_4(self) -> complex:
        out = 9 + 9 * self.x_v + 41 * self.x_v ** 2 / 10
        out += 11 * self.x_v ** 3 / 10 + self.x_v ** 4 / 5 + self.x_v ** 5 / 30
        return out

    # -------------------------------------------------------------------------
    # Exceptions
    # -------------------------------------------------------------------------

    @staticmethod
    def _check_small_particle_limit_value(value):
        if not value:
            raise NotImplementedError(
                'You are trying to use the general solution to the ARF '
                'for this model. However, so far just the limiting cases '
                'are implemented. Feel free to help us to extend this.',
            )

    # -------------------------------------------------------------------------
    # Getters and Setters
    # -------------------------------------------------------------------------

    @property
    def small_particle_limit(self) -> bool:
        """Use limiting case for ARF calculation

        :getter: returns if a small particle limit is used
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        :raises NotImplementedError: If value is set to False; because just the
            limiting cases for the ARF are implemented
        """
        return self._small_particle_limit.value

    @small_particle_limit.setter
    def small_particle_limit(self, value):
        self._check_small_particle_limit_value(value)
        self._small_particle_limit.value = value

    @property
    def small_viscous_boundary_layer(self) -> bool:
        """Use limiting case of a small viscous boundary layer :math:`\\delta`

        :getter: returns if a small viscous boundary layer case is used
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._small_viscous_boundary_layer.value

    @small_viscous_boundary_layer.setter
    def small_viscous_boundary_layer(self, value):
        self._small_viscous_boundary_layer.value = value

    @property
    def large_viscous_boundary_layer(self) -> bool:
        """Use limiting case of a large viscous boundary layer :math:`\\delta`

        :getter: returns if a large viscous boundary layer case is used
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._large_viscous_boundary_layer.value

    @large_viscous_boundary_layer.setter
    def large_viscous_boundary_layer(self, value):
        self._large_viscous_boundary_layer.value = value

    @property
    def fastened_sphere(self) -> bool:
        """Use limiting case of fastened sphere

        :getter: returns if fastened sphere limiting case is used
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._fastened_sphere.value

    @fastened_sphere.setter
    def fastened_sphere(self, value):
        self._fastened_sphere.value = value


if __name__ == '__main__':
    pass
