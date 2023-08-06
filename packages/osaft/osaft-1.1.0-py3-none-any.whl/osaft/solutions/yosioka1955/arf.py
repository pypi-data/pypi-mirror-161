from __future__ import annotations

from typing import Optional, Union

from osaft import log
from osaft.core.backgroundfields import WaveType, WrongWaveTypeError
from osaft.core.frequency import Frequency
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import conj, pi, sin
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import (
    ActiveListVariable,
    ActiveVariable,
    PassiveVariable,
)
from osaft.solutions.base_arf import BaseARF
from osaft.solutions.yosioka1955.scattering import ScatteringField


class ARF(ScatteringField, BaseARF):
    """ARF class for Yosioka & Kawasima (1955)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
    :param c_s: Speed of sound of the particle [m/s]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param position: Position in the standing wave field [rad]
    :param wave_type: either standing or progressive wave
    """

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float, c_s: float, rho_f: float, c_f: float,
        p_0: float, wave_type: WaveType,
        position: Optional[float] = None, N_max: int = 5,
        small_particle: bool = False, bubble_solution: bool = False,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        ScatteringField.__init__(
            self,
            f=f,
            R_0=R_0,
            rho_s=rho_s,
            c_s=c_s,
            rho_f=rho_f,
            c_f=c_f,
            p_0=p_0,
            position=position,
            wave_type=wave_type,
            N_max=N_max,
        )

        self._small_particle = PassiveVariable(
            small_particle,
            'Small Particle Limit',
        )
        self._bubble_solution = PassiveVariable(
            bubble_solution,
            'Bubble solution Limit',
        )

        self._F = ActiveVariable(
            self._compute_F,
            'density-compressibility factor',
        )
        self._K_n = ActiveListVariable(
            self._compute_K_n,
            'Coefficient K_n',
        )
        self._M_n = ActiveListVariable(
            self._compute_M_n,
            'Coefficient M_n',
        )

        self._F.is_computed_by(
            self._sigma,
            self._lambda_rho,
            self.field._wave_type,
            self.scatterer._k_f,
            self.sphere._R_0,
        )

        self._K_n.is_computed_by(
            self.scatterer._k_f,
            self.sphere._R_0,
            self._B_n,
            self.fluid._k_f,
        )

        self._M_n.is_computed_by(
            self.scatterer._k_f,
            self.sphere._R_0,
            self._B_n,
            self.fluid._k_f,
        )

        log.info(str(self))
        log.debug(repr(self))

    def __repr__(self):
        return (
            f'{type(self)}(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, '
            f'c_f={self.c_f}, c_s={self.c_s}'
            f'p_0={self.p_0}, position={self.position}, '
            f'wave_type={self.wave_type}, N_max={self.N_max}'
            f'small_particle={self.small_particle}, '
            f'bubble_solution={self.bubble_solution})'
        )

    def __str__(self):
        out = 'Yosioka\'s solution to the ARF field'
        out += ' with following properties: \n'
        out += SF.get_str_text('Wave type', '', self.wave_type, '')
        out += SF.get_str_text('Frequency', 'f', self.f, 'Hz')
        out += SF.get_str_text('Pressure', 'p_0', self.p_0, 'Pa')
        out += SF.get_str_text(
            'Position', 'd', self.position, 'rad',
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
        out += 'Limiting cases\n'
        out += SF.get_str_text(
            'Small Particle', 'small_particle',
            self.small_particle, None,
        )
        out += SF.get_str_text(
            'Bubble', 'bubble_solution',
            self.bubble_solution, None,
        )
        out += 'Other\n'
        out += SF.get_str_text(
            '#modes', 'N_max',
            self.N_max, None,
        )
        return out

    # -------------------------------------------------------------------------
    # User-faced functions
    # -------------------------------------------------------------------------

    def compute_arf(self) -> float:
        """
        Acoustic radiation force [N]

        Computes the ARF, based on the general solution (Eq. 44), or the
        approximation for either small particles (Eq. 59, 62) or small bubbles
        (Eq. 68, 73), if the respective options are selected.

        :raises WrongWaveTypeError: if wrong :attr:`wave_type`
        """

        # Checking wave_type
        self.check_wave_type()

        if self.small_particle and self.bubble_solution:
            return self._bubble_arf()
        elif not self.small_particle and self.bubble_solution:
            raise ValueError(
                'The bubble solution is only defined for small '
                'bubbles. Set small_particle to True.',
            )
        elif self.small_particle:
            return self._small_particle_arf()
        else:
            return self._compute_general_arf()

    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def small_particle(self) -> bool:
        """Small particle limit option.

        :getter: returns the setting for the small particle limit
        :rtype: bool
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        :type: bool
        """
        return self._small_particle.value

    @small_particle.setter
    def small_particle(self, value: bool) -> None:
        self._small_particle.value = value

    @property
    def bubble_solution(self) -> bool:
        """Bubble solution option.

        :getter: returns the setting for the bubble solution
        :rtype: bool
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        :type: bool
        """
        return self._bubble_solution.value

    @bubble_solution.setter
    def bubble_solution(self, value: bool) -> None:
        self._bubble_solution.value = value

    # -------------------------------------------------------------------------
    # General Solution
    # -------------------------------------------------------------------------

    def _compute_general_arf(self) -> float:
        """
        Computes general analytical solution for the ARF

        (Eq. 44)
        """

        out = 5 * [0]

        for n in range(self.N_max):
            # (45)
            s1 = (self.K_n(n) * conj(self.K_n(n + 1))).real
            s1 *= n + 1
            out[0] += s1

            # (46)
            s2 = (self.M_n(n) * conj(self.M_n(n + 1))).real
            s2 *= n * (n + 1) * (n + 2)
            out[1] += s2

            # (47)
            s3 = (self.K_n(n) * conj(self.M_n(n + 1))).real
            s3 *= (n + 1) * (n + 2)
            s4 = (self.M_n(n) * conj(self.K_n(n + 1))).real
            s4 *= n * (n + 1)
            out[2] += s3
            out[3] += s4

            # (48)
            s5 = (self.M_n(n) * conj(self.M_n(n + 1))).real
            s5 *= n + 1
            out[4] += s5

        out[0] *= -self.R_0 ** 2
        out[1] *= self.lambda_rho ** 2
        out[2] *= -self.R_0 * self.lambda_rho
        out[3] *= self.R_0 * self.lambda_rho
        out[4] *= - (self.k_f ** 2 * self.R_0 ** 2 * self.lambda_rho ** 2)

        # (Eq. 44)
        out = 2 * pi * self.rho_f * sum(out)

        # Needed because Yosioka has different definition for standing wave
        if self.wave_type == WaveType.STANDING:
            out *= -1

        return out

    # -------------------------------------------------------------------------
    # Small Particle Limit
    # -------------------------------------------------------------------------

    def _small_particle_arf(self) -> float:
        conditions = [
            (self.k_s * self.R_0) ** 2 > 0.1,
            (self.k_f * self.R_0) ** 2 > 0.1,
        ]
        for c in conditions:
            if c:
                text = 'Criteria for small particle might not be fulfilled.'
                text += 'Consider using another model approach'
                log.warning(text)
                break
        if self.wave_type == WaveType.STANDING:
            out = self._small_particle_standing_wave_solution()
        else:
            out = self._small_particle_traveling_wave_solution()
        return out

    def _small_particle_traveling_wave_solution(self) -> float:
        """
        Eq. (59)
        """

        out = (
            pi * self.R_0 ** 2 * 4 * (self.k_f * self.R_0) ** 4
            * self.I_ac / self.c_f
            * self.F
        )
        return out

    def _small_particle_standing_wave_solution(self) -> float:
        """
        Eq. (62)
        """

        out = (
            pi * self.R_0 ** 2 * 4 * self.k_f * self.R_0
            * self.E_ac
            * sin(2 * self.position)
            * self.F
        )
        return out

    # -------------------------------------------------------------------------
    # Bubble Limit
    # -------------------------------------------------------------------------

    def _bubble_arf(self) -> float:
        order_bubble = (self.k_f * self.R_0) ** 2
        conditions = [
            self.lambda_rho < 0.1 * order_bubble,
            self.lambda_rho > 10 * order_bubble,
            (self.k_s * self.R_0) ** 2 > 0.1,
            (self.k_f * self.R_0) ** 2 > 0.1,
        ]
        for c in conditions:
            if c:
                text = 'Criteria for small bubbles might not be fulfilled.'
                text += 'Consider using another model approach'
                log.info(text)
                break

        if self.wave_type == WaveType.STANDING:
            out = self._standing_wave_solution_bubble()
        else:
            out = self._bubble_traveling_wave_solution()
        return out

    def _bubble_traveling_wave_solution(self) -> float:
        """
        Eq. (68)
        :rtype: float
        """
        out = (
            4 * pi * self.R_0 ** 2
            * (self.k_s * self.R_0) ** 4
            * self.I_ac
        )
        out /= (
            self.c_f
            * (
                self.sigma ** 2 * (self.k_s * self.R_0) ** 6
                + (3 * self.lambda_rho - (self.k_s * self.R_0) ** 2) ** 2
            )
        )
        return out

    def _standing_wave_solution_bubble(self) -> float:
        """
        Eq. (74)
        """
        out = -4 * pi / self.k_f ** 2
        out *= self.E_ac
        out *= sin(2 * self.position)
        out *= self.F
        return out

    # -------------------------------------------------------------------------
    # Coefficients
    # -------------------------------------------------------------------------

    @property
    def F(self) -> float:
        """
        Density-compressibility factor :math:`F` [-]

        (Eq. 60, 63, 75)

        Acoustic contrast factor for small particle solutions. The error
        from the article in the factor for a bubble in standing wave has
        been corrected.
        :return: contrast factor [-]
        """
        return self._F.value

    def _compute_F(self) -> float:
        """
        Compute density-compressibility factor F
        """
        if self.wave_type == WaveType.STANDING:
            if self.bubble_solution:
                return self._compute_F_standing_bubble()
            else:
                return self._compute_F_standing()

        elif (
                self.wave_type == WaveType.TRAVELLING
                and not self.bubble_solution
        ):
            return self._compute_F_travelling()
        else:
            raise WrongWaveTypeError(
                'Factor F is only defined for particles travelling and '
                'standing waves and for bubbles in standing waves',
            )

    def _compute_F_travelling(self):
        # Eq. 60
        out = (- (1 + 2 * self.lambda_rho))
        out /= (3 * self.lambda_rho * self.sigma ** 2)
        out += self.lambda_rho
        out *= out
        out += (2 / 9) * ((1 - self.lambda_rho) ** 2)
        out /= (1 + 2 * self.lambda_rho) ** 2
        return out

    def _compute_F_standing(self):
        # Eq. 63
        out = self.lambda_rho + (2 * (self.lambda_rho - 1) / 3)
        out /= 1 + 2 * self.lambda_rho
        out -= 1 / (3 * self.lambda_rho * self.sigma ** 2)
        return out

    def _compute_F_standing_bubble(self):
        # Eq. 75 (corrected)
        resonance_term = (3 * self.lambda_rho - self.x_s ** 2)
        out = self.sigma * self.x_s ** 3 * resonance_term  # Wrong in paper
        out /= (self.sigma ** 2 * self.x_s ** 6 + resonance_term ** 2)
        return out

    def K_n(self, n: int) -> complex:
        """Coefficient :math:`K_n` [m^2/s]

        (Eq. 43)

        :param n: mode [-]
        :return: coefficient [m^2/s]
        """
        return self._K_n.item(n)

    def M_n(self, n: int) -> complex:
        """Coefficient :math:`M_n` [m^2/s]

        (Eq. 42)

        :param n: mode [-]
        :return: coefficient [m^2/s]
        """
        return self._M_n.item(n)

    def _compute_K_n(self, n: int) -> complex:
        """
        Compute K_n according to Eq. (43)
        """
        out = (-1) ** n / (2 * n + 1)
        out *= self.k_s * self.B_n(n)
        out *= Bf.d1_besselj(n, self.k_s * self.R_0)
        return out

    def _compute_M_n(self, n: int) -> complex:
        """
        Compute M_n according to Eq. (42)
        """
        out = (-1) ** n / (2 * n + 1)
        out *= self.B_n(n)
        out *= Bf.besselj(n, self.k_s * self.R_0)
        return out


if __name__ == '__main__':
    pass
