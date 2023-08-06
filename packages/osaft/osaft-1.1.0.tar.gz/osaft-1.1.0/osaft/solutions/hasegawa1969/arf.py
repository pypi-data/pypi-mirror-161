from __future__ import annotations

from typing import Optional, Union

import osaft
from osaft import log
from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import ActiveListVariable
from osaft.solutions.base_arf import BaseARF
from osaft.solutions.hasegawa1969.scattering import ScatteringField


class ARF(ScatteringField, BaseARF):
    """ARF class for Hasegawa & Yosioka (1969)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the solid sphere [kg/m^3]
    :param E_s: Young's modulus [Pa]
    :param nu_s: Poisson's ratio of the solid sphere [-]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param position: Position in the standing wave field [rad]
    :param wave_type: Either standing or progressive wave
    """

    def __init__(
            self, f: Union[Frequency, float, int],
            R_0: Union[Sphere, float, int],
            rho_s: float, E_s: float, nu_s: float, rho_f: float, c_f: float,
            p_0: float, wave_type: WaveType,
            position: Optional[float] = None, N_max: int = 5,
    ) -> None:
        """Constructor method
        """

        ScatteringField.__init__(
            self,
            f=f,
            R_0=R_0,
            rho_s=rho_s,
            E_s=E_s,
            nu_s=nu_s,
            rho_f=rho_f,
            c_f=c_f,
            p_0=p_0,
            position=position,
            wave_type=wave_type,
            N_max=N_max,
        )

        self._U_n = ActiveListVariable(
            self._compute_U_n,
            'Coefficient U_n',
        )
        self._V_n = ActiveListVariable(
            self._compute_V_n,
            'Coefficient V_n',
        )
        self._d_U_n = ActiveListVariable(
            self._compute_d_U_n,
            'Derivative of Coefficient U_n',
        )
        self._V_n_d1 = ActiveListVariable(
            self._compute_d_V_n,
            'Derivative of Coefficient V_n',
        )

        self._V_n.is_computed_by(
            self.sphere._R_0,
            self._c_n,
            self.fluid._k_f,
        )
        self._U_n.is_computed_by(
            self.sphere._R_0,
            self._c_n,
            self.fluid._k_f,
        )
        self._V_n_d1.is_computed_by(
            self.sphere._R_0,
            self._c_n,
            self.fluid._k_f,
        )
        self._d_U_n.is_computed_by(
            self.sphere._R_0,
            self._c_n,
            self.fluid._k_f,
        )

        log.info(str(self))
        log.debug(repr(self))

    def __repr__(self):
        return (
            f'{type(self)}(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, rho_f={self.rho_f}, '
            f'c_f={self.c_f}, E={self.E_s}, nu = {self.nu_s}, '
            f'p_0={self.p_0}, position={self.position}, '
            f'wave_type={self.wave_type}, N_max={self.N_max}'
        )

    def __str__(self):
        out = 'Hasegawa\'s solution to the ARF field'
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
            'Young\'s Modulus', 'E',
            self.E_s, 'Pa',
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

        Computes the ARF, based on the general solution (Eq. 13)

        :raises WrongWaveTypeError: if wrong :attr:`wave_type`
        """

        # Checking wave_type
        self.check_wave_type()
        if self.wave_type == WaveType.STANDING:
            return self._compute_arf_standing()
        else:
            return self._compute_arf_travelling()

    # -------------------------------------------------------------------------
    # General Solution
    # -------------------------------------------------------------------------

    def _compute_arf_travelling(self) -> float:
        """
        Computes general analytical solution for the ARF in the propagating
        wave case

        (Eq. 13)
        """

        out = 5 * [0]

        for n in range(self.N_max):
            # (Eq. 23)
            s1 = (self.d_U_n(n) * self.d_V_n(n + 1))
            s1 -= (self.d_V_n(n) * self.d_U_n(n + 1))
            s1 *= n + 1
            out[0] += s1

            # (Eq. 24)
            s2 = (self.U_n(n) * self.V_n(n + 1))
            s2 -= (self.V_n(n) * self.U_n(n + 1))
            s2 *= n * (n + 1) * (n + 2)
            out[1] += s2

            # (Eq. 25)
            s3 = (self.U_n(n) * self.d_V_n(n + 1))
            s3 -= (self.V_n(n) * self.d_U_n(n + 1))
            s3 *= n * (n + 1)
            s4 = (self.d_U_n(n) * self.V_n(n + 1))
            s4 -= (self.d_V_n(n) * self.U_n(n + 1))
            s4 *= (n + 1) * (n + 2)
            out[2] += s3
            out[3] += s4

            # (Eq. 26)
            s5 = (self.U_n(n) * self.V_n(n + 1))
            s5 -= (self.V_n(n) * self.U_n(n + 1))
            s5 *= n + 1
            out[4] += s5

        out[0] *= - self.x_f ** 2
        out[1] *= 1
        out[2] *= self.x_f
        out[3] *= - self.x_f
        out[4] *= - self.x_f ** 2

        # (Eq. 13)
        out = 2 * osaft.pi * self.rho_f * sum(out) * abs(self.field.A) ** 2
        return out

    def _compute_arf_standing(self) -> float:
        """
        Computes general analytical solution for the ARF. This is from the
        Hasegawa1979 paper.

        (Eq. 10)
        """

        out = 5 * [0]

        for n in range(self.N_max):
            # (Eq. 15, rows 1 and 2)
            s1 = (self.d_U_n(n) * self.d_U_n(n + 1))
            s1 += (self.d_V_n(n) * self.d_V_n(n + 1))
            s1 *= (n + 1) * (-1) ** (n + 1)
            out[0] += s1
            # check

            # (Eq. 15, rows 3 and 4)
            s2 = (self.U_n(n) * self.U_n(n + 1))
            s2 += (self.V_n(n) * self.V_n(n + 1))
            s2 *= n * (n + 1) * (n + 2) * (-1) ** (n + 1)
            out[1] += s2

            # (Eq. 15, rows 5 and 6)
            s3 = (self.U_n(n) * self.d_U_n(n + 1))
            s3 += (self.V_n(n) * self.d_V_n(n + 1))
            s3 *= n * (n + 1) * (-1) ** (n + 1)
            # (Eq. 15, row 6)
            s4 = (self.d_U_n(n) * self.U_n(n + 1))
            s4 += (self.d_V_n(n) * self.V_n(n + 1))
            s4 *= (n + 1) * (n + 2) * (-1) ** (n + 1)
            out[2] += s3
            out[3] += s4

            # (Eq. 15, row 7)
            s5 = (self.U_n(n) * self.U_n(n + 1))
            s5 += (self.V_n(n) * self.V_n(n + 1))
            s5 *= (n + 1) * (-1) ** (n + 1)
            out[4] += s5

        common_coeff = (
            1 * osaft.pi * self.rho_f * self.field.A ** 2
            * osaft.core.functions.sin(
                2 * self.position / self.k_f.real * self.k_f,
            )
        )

        out[0] *= - self.x_f ** 2 * common_coeff
        out[1] *= common_coeff
        out[2] *= self.x_f * common_coeff
        out[3] *= - self.x_f * common_coeff
        out[4] *= - self.x_f ** 2 * common_coeff

        # (Eq. 13)
        out = -sum(out)

        return out.real

    # -------------------------------------------------------------------------
    # Coefficients
    # -------------------------------------------------------------------------

    def U_n(self, n: int) -> complex:
        """Coefficient :math:`U_n` [-]

        (Eq. 19)

        :param n: mode [-]
        :return: coefficient [m^2/s]
        """
        return self._U_n.item(n)

    def V_n(self, n: int) -> complex:
        """Coefficient :math:`V_n` [-]

        (Eq. 19)

        :param n: mode [-]
        :return: coefficient [m^2/s]
        """
        return self._V_n.item(n)

    def d_U_n(self, n: int) -> complex:
        """Coefficient :math:`U_n'` [-]

        (Eq. 19)

        :param n: mode [-]
        :return: coefficient [m^2/s]
        """
        return self._d_U_n.item(n)

    def d_V_n(self, n: int) -> complex:
        """Coefficient :math:`V_n'` [-]

        (Eq. 19)

        :param n: mode [-]
        :return: coefficient [m^2/s]
        """
        return self._V_n_d1.item(n)

    def _compute_U_n(self, n: int) -> complex:
        """
        Compute U_n according to Eq. (19)
        """
        c_n = self.c_n(n)
        out = (
            (1 + c_n.real) * Bf.besselj(n, self.k_f * self.R_0)
            + c_n.imag * Bf.bessely(n, self.k_f * self.R_0)
        )
        return out

    def _compute_V_n(self, n: int) -> complex:
        """
        Compute V_n according to Eq. (19)
        """
        c_n = self.c_n(n)
        out = (
            c_n.imag * Bf.besselj(n, self.k_f * self.R_0)
            - c_n.real * Bf.bessely(n, self.k_f * self.R_0)
        )
        return out

    def _compute_d_U_n(self, n: int) -> complex:
        """
        Compute first derivative of U_n according to Eq. (19)
        """
        c_n = self.c_n(n)
        out = (
            (1 + c_n.real) * Bf.d1_besselj(n, self.k_f * self.R_0)
            + c_n.imag * Bf.d1_bessely(n, self.k_f * self.R_0)
        )
        return out

    def _compute_d_V_n(self, n: int) -> complex:
        """
        Compute first derivative of V_n according to Eq. (19)
        """
        c_n = self.c_n(n)
        out = (
            c_n.imag * Bf.d1_besselj(n, self.k_f * self.R_0)
            - c_n.real * Bf.d1_bessely(n, self.k_f * self.R_0)
        )
        return out


if __name__ == '__main__':
    pass
