from __future__ import annotations

from typing import Optional, Union

from osaft import log
from osaft.core.backgroundfields import WaveType, WrongWaveTypeError
from osaft.core.frequency import Frequency
from osaft.core.functions import pi, sin, sqrt
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import ActiveVariable, PassiveVariable
from osaft.solutions.base_arf import BaseARF
from osaft.solutions.doinikov1994compressible.scattering import ScatteringField


class ARF(ScatteringField, BaseARF):
    """Base class for Doinikov (viscous fluid-viscous sphere; 1994)

    .. note::
       For all implemented solution the small particle limit
       :math:`|x| \\ll 1` is assumed.

       If :attr:`small_viscous_boundary_layer` the ARF is computed for the
       limiting case :math:`|x| \\ll 1 \\ll |x_v|`. If
       :attr:`large_viscous_boundary_layer` is set to `True`
       then the ARF is computed for the limiting case
       :math:`|x| \\ll |x_v| \\ll 1`. Setting both option to `False` will
       lead to error since the solution for an arbitrary boundary layer
       thickness is implemented.

       Both values will be logged in the `info.log` when calling
       :meth:`compute_arf()`. These conditions will not be
       checked at runtime.


    :param f: Frequency [Hz]
    :param R_0: Radius of the solid [m]
    :param rho_s: Density of the fluid-like solid [kg/m^3]
    :param c_s: Speed of sound of the solid [m/s]
    :param eta_s: shear viscosity of the solid [Pa s]
    :param zeta_s: bulk viscosity of the solid [Pa s]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param eta_f: shear viscosity fluid [Pa s]
    :param zeta_f: bulk viscosity fluid [Pa s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: Type of wave, traveling or standing
    :param position: Position within the standing wave field [m]
    :param small_viscous_boundary_layer: :math:`x_v \\gg 1`
    :param large_viscous_boundary_layer: :math:`x_v \\ll 1`
    :param small_particle_limit: using the limiting cases for the ARF
    :param N_max: Highest order mode
    """

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float, c_s: float,
        eta_s: float, zeta_s: float,
        rho_f: float, c_f: float,
        eta_f: float, zeta_f: float,
        p_0: float,
        wave_type: WaveType,
        position: Optional[float] = None,
        small_viscous_boundary_layer: bool = False,
        large_viscous_boundary_layer: bool = False,
        small_particle_limit: bool = True,
        N_max: int = 5,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        super().__init__(
            f=f, R_0=R_0,
            rho_s=rho_s, c_s=c_s, eta_s=eta_s, zeta_s=zeta_s,
            rho_f=rho_f, c_f=c_f, eta_f=eta_f, zeta_f=zeta_f,
            p_0=p_0, wave_type=wave_type, position=position, N_max=N_max,
        )

        # independent variables
        self._check_small_particle_limit_value(small_particle_limit)
        self._small_particle_limit = PassiveVariable(
            small_particle_limit,
            'small particle limit',
        )
        self._check_boundary_layer(
            small_viscous_boundary_layer,
            large_viscous_boundary_layer,
        )
        self._small_viscous_boundary_layer = PassiveVariable(
            small_viscous_boundary_layer,
            'small viscous boundary layer limit',
        )
        self._large_viscous_boundary_layer = PassiveVariable(
            large_viscous_boundary_layer,
            'large viscous boundary layer limit',
        )

        # Dependent variables
        self._mu = ActiveVariable(
            self._compute_mu,
            '(density * viscosity) ratio',
        )
        self._kappa_t = ActiveVariable(
            self._compute_kappa_t,
            'compressibility ratio',
        )
        self._eta_t = ActiveVariable(
            self._compute_eta_t, 'dynamic viscosity ratio',
        )
        self._zeta_t = ActiveVariable(
            self._compute_zeta_t, 'bulk viscosity ratio',
        )
        self._f1 = ActiveVariable(self._compute_f1, 'f1 ARF factor; B.2.1')
        self._f2 = ActiveVariable(self._compute_f2, 'f2 ARF factor; B.2.1')
        self._f3 = ActiveVariable(self._compute_f3, 'f3 ARF factor; B.2.1')
        self._G = ActiveVariable(self._compute_G, 'G ARF factor; eq. 7.9')
        self._S1 = ActiveVariable(self._compute_S1, 'S1 ARF factor; eq. 7.10')
        self._S2 = ActiveVariable(self._compute_S2, 'S2 ARF factor; eq. 7.11')
        self._S3 = ActiveVariable(self._compute_S3, 'S3 ARF factor; eq. 7.12')
        self._f4 = ActiveVariable(self._compute_f4, 'f4 ARF factor; B.2.1')
        self._g1 = ActiveVariable(self._compute_g1, 'g1 ARF factor; B.2.1')
        self._g2 = ActiveVariable(self._compute_g2, 'g2 ARF factor; B.2.1')
        self._g3 = ActiveVariable(self._compute_g3, 'g3 ARF factor; B.2.1')
        self._g4 = ActiveVariable(self._compute_g4, 'g4 ARF factor; B.2.1')
        self._g5 = ActiveVariable(self._compute_g5, 'g5 ARF factor; B.2.1')
        self._g6 = ActiveVariable(self._compute_g6, 'g6 ARF factor; B.2.1')
        self._g7 = ActiveVariable(self._compute_g7, 'g7 ARF factor; B.2.1')

        # Dependencies
        self._G.is_computed_by(self._S1, self._S2, self._S3)
        self._S1.is_computed_by(
            self._kappa_t, self.fluid._rho_f, self.scatterer._rho_f,
        )
        self._S2.is_computed_by(self._f1, self._f2, self._f4)
        self._S3.is_computed_by(
            self._f1, self._f3, self._f4, self.fluid._rho_f,
            self.scatterer._rho_f, self._kappa_t, self._eta_t,
        )
        self._eta_t.is_computed_by(self.scatterer._eta_f, self.fluid._eta_f)
        self._zeta_t.is_computed_by(self.scatterer._zeta_f, self.fluid._zeta_f)
        self._f1.is_computed_by(self._g1, self._g7)
        self._f2.is_computed_by(self._g1, self._g2, self._g5)
        self._f3.is_computed_by(self._g3, self._g6, self._g7)
        self._f4.is_computed_by(self._g4, self._g6, self._g7)
        self._g1.is_computed_by(self._g5, self._g6)
        self._g2.is_computed_by(self._eta_t, self._zeta_t)
        self._g3.is_computed_by(self._eta_t, self._zeta_t)
        self._g4.is_computed_by(self._eta_t, self._zeta_t)
        self._g5.is_computed_by(self._eta_t)
        self._g6.is_computed_by(self._eta_t)
        self._g7.is_computed_by(self._g6)
        self._kappa_t.is_computed_by(
            self.fluid._rho_f, self.fluid._c_f, self.scatterer._rho_f,
            self.scatterer._c_f,
        )
        self._mu.is_computed_by(
            self.fluid._rho_f, self.fluid._eta_f, self.scatterer._rho_f,
            self.scatterer._eta_f,
        )

        # logging
        log.debug(repr(self))
        log.info(str(self))

    def __repr__(self):
        return (
            f'Donikov1994Rigid.ARF(f={self.f}, R_0={self.R_0}, '
            f'rho_s={self.rho_s}, c_s={self.c_s}, '
            f'eta_s={self.eta_s}, zeta_s={self.zeta_s}, '
            f'rho_f={self.rho_f}, c_f={self.c_f}, '
            f'eta_f={self.eta_f}, zeta_f={self.zeta_f}, '
            f'p_0={self.p_0}, position={self.position}, {self.wave_type}, '
            f'small_viscous_boundary_layer='
            f'{self.small_viscous_boundary_layer}, '
            f'large_viscous_boundary_layer='
            f'{self.large_viscous_boundary_layer}, '
            f'small_particle_limit={self.small_particle_limit}, '
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
        out += 'Backgroundfield\n'
        out += SF.get_str_text('Frequency', 'f', self.f, 'Hz')
        out += SF.get_str_text('Pressure', 'p_0', self.p_0, 'Pa')
        out += SF.get_str_text('Wavetype', 'wave_type', self.wave_type, None)
        out += SF.get_str_text(
            'Position', 'd',
            self.position, '',
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
        out += SF.get_str_text(
            'Sound Speed', 'c_0',
            self.c_s, 'm/s',
        )
        out += SF.get_str_text(
            'Compressibility', 'kappa_s',
            self.kappa_s, '1/Pa',
        )
        out += SF.get_str_text(
            'Shear viscosity', 'eta_s',
            self.eta_s, '1/Pa',
        )
        out += SF.get_str_text(
            'Bulk viscosity', 'zeta_s',
            self.zeta_s, '1/Pa',
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

        # Check boundary layer
        self._check_boundary_layer(
            self.small_viscous_boundary_layer,
            self.large_viscous_boundary_layer,
        )

        # Checking Wave Type
        self.check_wave_type()
        # Cases
        if self.small_viscous_boundary_layer:
            return self._arf_small_particle_small_delta()
        else:
            return self._arf_small_particle_large_delta()

    # -------------------------------------------------------------------------
    # Acoustic radiation force
    # -------------------------------------------------------------------------

    def _arf_small_particle_large_delta(self) -> float:
        """ Eq. 7.1 for WaveType.TRAVELLING; Eq. 7.8 for WaveType.STANDING
        """
        log.info(
            f'kappa_t << 1 : {self.kappa_t:.3e} << 1\n'
            f'rho_f << rho_s : {self.rho_s:.3e} << {self.rho_s:.3e}\n',
        )

        if self.wave_type == WaveType.TRAVELLING:
            out = 5 - 2 * self.kappa_t - 8 * self.f1

            out *= 1 / 6 * self.norm_delta ** 2
        else:
            out = self.G * self._standing_wave_contribution()
        out *= pi * self.field.abs_A_squared * self.rho_f * self.x_0**3
        return out

    def _arf_small_particle_small_delta(self) -> float:
        """ Eq. 6.1 for WaveType.TRAVELLING
        """
        log.info(
            f'kappa_t << 1 : {self.kappa_t:.3e} << 1\n'
            f'mu << 1 : {self.mu:.3e} << 1\n',
        )
        if self.wave_type == WaveType.TRAVELLING:
            out = (self.rho_s - self.rho_f) ** 2
            out /= (2 * self.rho_s + self.rho_f)**2 * (1 + self.mu)

            out *= self.x_0**3 * self.norm_delta

            out *= 6 * pi * self.rho_f * self.field.abs_A_squared
        else:
            raise WrongWaveTypeError(
                'This solution is not implemented because Doinikov says '
                'in 6.1.2 of the publication that this solution is '
                'the same as Yosioka already computed.\n If you are '
                'interested in this value us the Yosioka class.',
            )
        return out

    def _standing_wave_contribution(self) -> float:
        return sin(2 * self.k_f.real * self.position)

    # -------------------------------------------------------------------------
    # User input checks
    # -------------------------------------------------------------------------

    @staticmethod
    def _check_boundary_layer(small_delta, large_delta) -> None:
        if small_delta and large_delta:
            raise ValueError(
                'small_viscous_boundary_layer and '
                'large_viscous_boundary_layer can\'t both be True',
            )
        if not small_delta and not large_delta:
            raise NotImplementedError(
                'You are trying to use the solution for an arbitrary '
                'boundary layer thickness. However, so far this solution '
                'has not implemented. Feel free to help us to extend this.',
            )

    @staticmethod
    def _check_small_particle_limit_value(value) -> None:
        if not value:
            raise NotImplementedError(
                'You are trying to use the general solution to the ARF '
                'for this model. However, so far just the limiting cases '
                'are implemented. Feel free to help us to extend this.',
            )

    # -------------------------------------------------------------------------
    # Getters and Setters for dependent variables
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
            :func:`osaft.core.variable.BaseVariable.notify`
        """
        return self._large_viscous_boundary_layer.value

    @large_viscous_boundary_layer.setter
    def large_viscous_boundary_layer(self, value):
        self._large_viscous_boundary_layer.value = value

    # -------------------------------------------------------------------------
    # Dependent variables
    # -------------------------------------------------------------------------

    @property
    def eta_t(self):
        """By fluid normalized dynamic viscosity
        """
        return self._eta_t.value

    def _compute_eta_t(self):
        return self.scatterer.eta_f / self.fluid.eta_f

    @property
    def zeta_t(self):
        """By fluid normalized bulk viscosity
        """
        return self._zeta_t.value

    def _compute_zeta_t(self):
        return self.scatterer.zeta_f / self.fluid.zeta_f

    @property
    def f1(self):
        """f1 factor of Appendix B
        """
        return self._f1.value

    def _compute_f1(self):
        return self.g1 / self.g7

    @property
    def f2(self):
        """f2 factor of Appendix B
        """
        return self._f2.value

    def _compute_f2(self):
        if self.g1 == 0:  # pragma: no cover
            return 0
        return self.g2 * self.g5 / self.g1 / 2

    @property
    def f3(self):
        """f3 factor of Appendix B
        """
        return self._f3.value

    def _compute_f3(self):
        return self.g3 * self.g6 / self.g7 / 10

    @property
    def f4(self):
        """f4 factor of Appendix B
        """
        return self._f4.value

    def _compute_f4(self):
        return self.g4 * self.g6 / self.g7 / 2

    @property
    def G(self):
        """G factor Eq (7.9)
        """
        return self._G.value

    def _compute_G(self):
        return (self.S1 + self.S2 + self.S3) / 3

    @property
    def S1(self):
        """S_1 factor Eq (7.10)
        """
        return self._S1.value

    def _compute_S1(self):
        return 1 - self.kappa_t + 0.9 * (1 - self.rho_s / self.rho_f)

    @property
    def S2(self):
        """S_2 factor Eq (7.11)
        """
        return self._S2.value

    def _compute_S2(self):
        out = 2 * self.f2 - 1
        out *= 2 * self.f1

        out -= 4 * self.f4
        return out

    @property
    def S3(self):
        """S_3 factor Eq (7.12)
        """
        return self._S3.value

    def _compute_S3(self):
        out = 3 - 1 / self.eta_t
        out *= -120 * (self.f3 - self.f4)

        out += 50 * self.f1 + 43 - 10 * self.kappa_t

        out *= self.rho_s - self.rho_f
        out /= 30 * self.rho_f * (3 + 2 / self.eta_t)

        return out

    @property
    def g1(self):
        """g1 factor of Appendix B
        """
        return self._g1.value

    def _compute_g1(self):
        return self.g5 * self.g6

    @property
    def g2(self):
        """g2 factor of Appendix B
        """
        return self._g2.value

    def _compute_g2(self):
        out = 209 + 148 * self.eta_t + 48 / self.eta_t
        out *= -1 / 9 / self.zeta_t

        out += 19 + 38 * self.eta_t - 12 / self.eta_t
        return out

    @property
    def g3(self):
        """g3 factor of Appendix B
        """
        return self._g3.value

    def _compute_g3(self):
        out = 25 + 370 * self.eta_t - 80 / self.eta_t
        out *= 1 / 9 / self.zeta_t

        out -= (12 + 19 * self.eta_t + 4 / self.eta_t)
        return out

    @property
    def g4(self):
        """g4 factor of Appendix B
        """
        return self._g4.value

    def _compute_g4(self):
        out = 5 + 74 * self.eta_t - 16 / self.eta_t
        out *= 1 / 9 / self.zeta_t

        out -= (3 + 4 / self.eta_t)
        return out

    @property
    def g5(self):
        """g5 factor of Appendix B
        """
        return self._g5.value

    def _compute_g5(self):
        out = (1 - self.eta_t)
        out *= 19 + 16 / self.eta_t
        return out

    @property
    def g6(self):
        """g6 factor of Appendix B
        """
        return self._g6.value

    def _compute_g6(self):
        return 89 + 48 / self.eta_t + 38 * self.eta_t

    @property
    def g7(self):
        """g7 factor of Appendix B
        """
        return self._g7.value

    def _compute_g7(self):
        return self.g6**2

    @property
    def mu(self) -> float:
        """ (density x viscosity) ratio
        :math:`\\tilde{\\mu}=\\frac{\\rho_f\\eta_f}{\\rho_s\\eta_s}`
        """
        return self._mu.value

    def _compute_mu(self):
        out = self.rho_f * self.eta_f
        out /= self.rho_s * self.eta_s
        return sqrt(out)

    @property
    def kappa_t(self) -> float:
        """ compressibility ratio
        :math:`\\tilde{\\kappa}=\\frac{\\kappa_s}{\\kappa_f}`
        """
        return self._kappa_t.value

    def _compute_kappa_t(self):
        return self.kappa_s / self.kappa_f


if __name__ == '__main__':
    pass
