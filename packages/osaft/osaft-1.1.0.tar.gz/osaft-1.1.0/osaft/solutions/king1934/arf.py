from __future__ import annotations

from typing import Optional, Union

from osaft import log
from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.functions import pi, sin
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import (
    ActiveListVariable,
    ActiveVariable,
    PassiveVariable,
)
from osaft.solutions.base_arf import BaseARF
from osaft.solutions.king1934.scattering import ScatteringField


class ARF(ScatteringField, BaseARF):
    """ARF class for King (1934)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: Type of incident wave (traveling/standing)
    :param position: Position in the standing wave field [rad]
    :param N_max: Highest order mode
    :param small_particle_limit: compute ARF based on small particle limit
    """

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float,
        rho_f: float, c_f: float,
        p_0: float, wave_type: WaveType, position: Optional[float] = None,
        N_max: int = 5,
        small_particle_limit: bool = False,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        ScatteringField.__init__(
            self, f, R_0, rho_s, rho_f, c_f,
            p_0, wave_type, position, N_max,
        )

        # Passive Variable
        self._small_particle_limit = PassiveVariable(
            small_particle_limit,
            'small particle limit',
        )

        # Active variables
        self._f_2 = ActiveVariable(
            self._compute_f_2,
            'dipole scattering coefficient f_2',
        )
        self._Phi = ActiveVariable(
            self._compute_Phi,
            'acoustic contrast factor Phi',
        )

        self._f_2.is_computed_by(self.scatterer._rho_s, self.fluid._rho_f)
        self._Phi.is_computed_by(
            self._f_2, self.field._wave_type,
            self._rho_tilde,
        )

        self._FFGG = ActiveListVariable(self._compute_FFGG, 'FFGG(n)')
        self._FGFG = ActiveListVariable(self._compute_FGFG, 'FGFG(n)')
        self._HH = ActiveListVariable(self._compute_HH, 'HH(n)')

        self._FFGG.is_computed_by(self._alpha, self._rho_tilde)
        self._FGFG .is_computed_by(self._alpha, self._rho_tilde)
        self._HH.is_computed_by(self._alpha, self._rho_tilde, self._FFGG)

        log.info(str(self))
        log.debug(repr(self))

    def __repr__(self):
        return (
            f'{type(self)}(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, c_f={self.c_f}, '
            f'p_0={self.p_0}, position={self.position}, '
            f'small_particle_limit={self.small_particle_limit}, '
            f'wave_type={self.wave_type}, N_max={self.N_max})'
        )

    def __str__(self):
        out = 'King\'s solution to the ARF with following properties: \n'
        out += SF.get_str_text(
            'Small Particle Limit', '',
            self.small_particle_limit, '',
        )
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

    def compute_arf(self) -> float:
        """Acoustic radiation fore in [N]

        :raises WrongWaveTypeError: if wrong :attr:`wave_type`
        """
        # Checking wave_type
        self.check_wave_type()

        # Cases
        if self.small_particle_limit:
            return self._compute_small_particle_limit_arf()
        elif self.wave_type == WaveType.STANDING:
            return self._compute_arf_standing()
        else:
            return self._compute_arf_traveling()

    # -------------------------------------------------------------------------
    # Getters and Setters for Independent Variables
    # -------------------------------------------------------------------------
    @property
    def f_2(self) -> float:
        """Dipole scatting coefficient :math:`f_2` [-]
        """
        return self._f_2.value

    @property
    def Phi(self) -> float:
        r"""Acoustic contrast factor :math:`\Phi` [-]
        """
        return self._Phi.value

    @property
    def small_particle_limit(self) -> bool:
        """ ARF for the small particle limit

        :getter: returns if small particle limit is computed
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._small_particle_limit.value

    @small_particle_limit.setter
    def small_particle_limit(self, value: bool) -> None:
        self._small_particle_limit.value = value

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def _compute_f_2(self) -> float:
        return 2 * (self.rho_tilde - 1) / (2 * self.rho_tilde + 1)

    def _compute_Phi(self):
        if self.wave_type == WaveType.STANDING:
            return 1 / 3 + self.f_2 / 2
        else:
            out = (1 + 2 / 9 * (1 - 1 / self.rho_tilde) ** 2)
            out /= (2 + 1 / self.rho_tilde) ** 2
            return out

    def _compute_arf_traveling(self) -> float:
        """Computes acoustic radiation force according to King's paper
        for a plane, progressive wave

        Equation (65) in the paper "On the Acoustic
        Radiation Pressure on Spheres"
        """
        first = 1 / self.HH(0)
        second = 2 / self.HH(1)
        second *= (self.alpha ** 2 - 3 * (1 - 1 / self.rho_tilde)) ** 2
        second /= self.alpha ** 8

        def higher():
            def term(order):
                out = (order + 1) / self.HH(order)
                out *= (self.alpha ** 2 - order * (order + 2)) ** 2
                out /= self.alpha ** (4 * order + 4)
                return out

            term_out = 0.0
            if self.N_max >= 2:
                for n in range(2, self.N_max + 1):
                    term_out += term(n)
            return term_out

        out = 2 * pi * self.rho_f * self.field.abs_A_squared
        out *= (first + second + higher())
        out /= self.alpha ** 2

        return out

    def _compute_arf_standing(self) -> float:
        """Computes acoustic radiation force according to King's
        paper for a plane standing wave

        Equation (74) in the paper "On the Acoustic
        Radiation Pressure on Spheres"
        """
        first = self.FFGG(0) / (self.alpha * self.HH(0))
        second = - 2 / self.alpha ** 5 * self.FFGG(1) / self.HH(1)
        second *= self.alpha ** 2 - 3 * (1 - 1 / self.rho_tilde)

        def higher():
            def term(order):
                out = (- 1) ** order * (order + 1)
                out /= self.alpha ** (2 * order + 3)
                out *= self.FFGG(order) / self.HH(order)
                out *= self.alpha ** 2 - order * (order + 2)
                return out

            term_out = 0.0
            if self.N_max >= 2:
                for n in range(2, self.N_max + 1):
                    term_out += term(n)
            return term_out

        out = pi * self.rho_f * self.field.abs_A_squared
        out *= sin(2 * self.position)
        out *= (first + second + higher())

        return out

    def _compute_small_particle_limit_arf(self) -> float:
        """Computes acoustic radiation force according to King's
        paper for small particles.

        Equation (76) (standing wave) and equation (66) (traveling wave)
        in the paper "On the Acoustic Radiation Pressure on Spheres"
        """
        if 10 * self.R_0 > self.field.lambda_f:
            text = 'Wavelength is less than 10 times greater than specified '
            text += 'Radius. Theory might not be valid anymore.'
            log.info(text)

        if self.wave_type == WaveType.STANDING:
            out = pi * self.rho_f * self.field.abs_A_squared
            out *= (self.k_f * self.R_0) ** 3
            out *= self.Phi * sin(2 * self.position)
            return out
        else:
            out = 2 * pi * self.rho_f * self.field.abs_A_squared
            out *= self.Phi * (self.k_f * self.R_0) ** 6
            return out

    # -------------------------------------------------------------------------
    # Coefficients
    # -------------------------------------------------------------------------

    def FFGG(self, n: int) -> complex:
        """Returns the coefficient :math:`F_{n+1}F_{n}+G_{n+1}G_{n}` for `n`.

        :param n: order
        """
        return self._FFGG.item(n)

    def _compute_FFGG(self, n: int) -> complex:
        out = self.F_n(n, self.alpha) * self.F_n(n + 1, self.alpha)
        out += self.G_n(n, self.alpha) * self.G_n(n + 1, self.alpha)
        return out

    def FGFG(self, n: int) -> complex:
        """Returns the coefficient :math:`F_{n+1}G_{n}-G_{n+1}F_{n}` for `n`.

        :param n: order
        """
        return self._FGFG.item(n)

    def _compute_FGFG(self, n: int) -> complex:
        out = self.F_n(n + 1, self.alpha) * self.G_n(n, self.alpha)
        out -= self.G_n(n + 1, self.alpha) * self.F_n(n, self.alpha)
        return out

    def HH(self, n: int) -> float:
        """Returns the coefficient :math:`H_{n}^2(n)H_{n}^2(n+1)` for `n` of
        (56) and (57).

        :param n: order
        """
        # King equations (56) and (57)
        # H_n(n) ** 2 * H_n(n + 1) ** 2
        return self._HH.item(n)

    def _compute_HH(self, n: int) -> complex:
        if n == 1:
            out = (self.alpha ** 2 - 3 * (1 - 1 / self.rho_tilde)) ** 2
            out /= self.alpha ** 10
            out += self.FFGG(n) ** 2
            return out
        else:
            out = (self.alpha ** 2 - n * (n + 2)) ** 2
            out /= self.alpha ** (4 * n + 6)
            out += self.FFGG(n) ** 2
            return out


if __name__ == '__main__':
    pass
