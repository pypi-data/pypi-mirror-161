from __future__ import annotations

from typing import Optional, Union

from osaft import log
from osaft.core.backgroundfields import BackgroundField, WaveType
from osaft.core.basecomposite import BaseSphereFrequencyComposite
from osaft.core.fluids import InviscidFluid
from osaft.core.frequency import Frequency
from osaft.core.functions import pi, sin
from osaft.core.geometries import Sphere
from osaft.core.helper import StringFormatter as SF
from osaft.core.variable import ActiveVariable
from osaft.solutions.base_arf import BaseARF
from osaft.solutions.base_solution import BaseSolution


class ARF(BaseARF, BaseSphereFrequencyComposite, BaseSolution):
    """ARF class for Gor'kov (1962)

    The standing wave solution is based on equation (13) of the paper and the
    traveling wave solution on equation (10).

    .. note::
       This model is based on the following assumptions:

       - :math:`\\lambda\\gg R`
       - Inviscid fluid
       - Compressible (fluid-like) sphere

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
    :param c_s: Speed of sound of the fluid-like sphere [m/s]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: Type of incident wave (traveling/standing)
    :param position: Position in the standing wave field [rad]
    """

    # Supported wave_type for the class
    supported_wavetypes = [WaveType.STANDING, WaveType.TRAVELLING]

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float, c_s: float,
        rho_f: float, c_f: float,
        p_0: float,
        wave_type: WaveType,
        position: Optional[float] = None,
    ) -> None:
        """Constructor method
        """

        # init of parent class
        BaseSphereFrequencyComposite.__init__(self, f, R_0)
        BaseSolution.__init__(self, 'Gorkov1962')

        # Initialize Components
        self.scatterer = InviscidFluid(self.frequency, rho_s, c_s)
        self.fluid = InviscidFluid(self.frequency, rho_f, c_f)
        self.field = BackgroundField(self.fluid, p_0, wave_type, position)

        # Dependent variables
        self._f_1 = ActiveVariable(
            self._compute_f_1,
            'monopole scattering coefficient f_1',
        )
        self._f_2 = ActiveVariable(
            self._compute_f_2,
            'dipole scattering coefficient f_2',
        )
        self._Phi = ActiveVariable(
            self._compute_Phi,
            'acoustic contrast factor Phi',
        )

        # Dependencies
        self._f_1.is_computed_by(self.fluid._kappa_f, self.scatterer._kappa_f)
        self._f_2.is_computed_by(self.fluid._rho_f, self.scatterer._rho_f)
        self._Phi.is_computed_by(self._f_1, self._f_2)

        log.info(str(self))
        log.debug(repr(self))

    def __repr__(self):
        return (
            f'GorkovARF({self.f}, {self.R_0}, {self.rho_s}, '
            f'{self.c_s}, {self.rho_f}, {self.c_f}, '
            f'{self.wave_type}, {self.p_0}, {self.position})'
        )

    def __str__(self):
        out = 'Gorkov solution with following properties: \n'
        out += SF.get_str_text('Frequency', 'f', self.f, 'Hz')
        out += SF.get_str_text('Pressure', 'p_0', self.p_0, 'Pa')
        out += SF.get_str_text(
            'Position', 'd',
            self.position, 'rad',
        )
        out += SF.get_str_text(
            'Wave Type', '',
            self.wave_type, None,
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
        out += SF.get_str_text(
            'Speed of Sound', 'c_s',
            self.scatterer.c_f, 'm/s',
        )
        out += SF.get_str_text(
            'Compressibility', 'kappa_s',
            self.kappa_s, '1/Pa', False,
        )
        return out

    def compute_arf(self) -> float:
        """Computes the ARF and returns the force in Newton [N].

        Computes ARF according to Eq. (10) or (11)
        Checks before computation of assumption of theory small particle
        radius to pressure field wavelength is valid.

        :raises WrongWaveTypeError: if wrong :attr:`wave_type`
        """
        # Checking wave_type
        self.check_wave_type()

        # Checking particle size
        if 10 * self.R_0 > self.field.lambda_f:
            text = 'Wavelength is less than 10 times greater than specified '
            text += 'Radius. Theory might not be valid anymore.'
            log.info(text)

        # Case
        if self.wave_type == WaveType.STANDING:
            return self._standing_wave_solution()
        else:
            return self._traveling_wave_solution()

    def _standing_wave_solution(self) -> float:
        out = 4 * pi * self.E_ac * self.R_0 ** 3 * self.k_f
        out *= self.Phi * sin(2 * self.position)
        return out

    def _traveling_wave_solution(self) -> float:
        out = 4 * pi / (9 * self.c_f) * self.I_ac * self.k_f ** 4
        out *= self.R_0**6
        out *= (self.f_1**2 + self.f_1 * self.f_2 + 3 / 4 * self.f_2**2)
        return out

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def f_1(self) -> float:
        """Monopole scattering coefficient :math:`f_{1}` [-]
        """
        return self._f_1.value

    @property
    def f_2(self) -> float:
        """Dipole scattering coefficient :math:`f_{2}` [-]
        """
        return self._f_2.value

    @property
    def Phi(self) -> float:
        """Acoustic contrast factor :math:`\\Phi`  [-]
        """
        return self._Phi.value

    # -------------------------------------------------------------------------
    # Wrappers for Independent Field Attributes
    # -------------------------------------------------------------------------

    @property
    def position(self) -> float:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.position`
        """
        return self.field.position

    @position.setter
    def position(self, value: float) -> None:
        self.field.position = value

    @property
    def p_0(self) -> float:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.p_0`
        """
        return self.field.p_0

    @p_0.setter
    def p_0(self, value: float) -> None:
        self.field.p_0 = value

    @property
    def wave_type(self) -> WaveType:
        """ Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.wave_type`
        """
        return self.field.wave_type

    @wave_type.setter
    def wave_type(self, value: WaveType) -> None:
        self.field.wave_type = value

    # -------------------------------------------------------------------------
    # Wrappers for Independent Field Attributes
    # -------------------------------------------------------------------------

    @property
    def E_ac(self) -> float:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.E_ac`
        """
        return self.field.E_ac

    @property
    def I_ac(self) -> float:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.I_ac`
        """
        return self.field.I_ac

    # -------------------------------------------------------------------------
    # Wrappers for Independent Scatterer Attributes
    # -------------------------------------------------------------------------

    @property
    def rho_s(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.InviscidFluid.rho_f`
        """
        return self.scatterer.rho_f

    @rho_s.setter
    def rho_s(self, value: float) -> None:
        self.scatterer.rho_f = value

    @property
    def c_s(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.InviscidFluid.c_f`
        """
        return self.scatterer.c_f

    @c_s.setter
    def c_s(self, value: float) -> None:
        self.scatterer.c_f = value

    # -------------------------------------------------------------------------
    # Wrappers for Dependent Scatterer Attributes
    # -------------------------------------------------------------------------

    @property
    def kappa_s(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.InviscidFluid.kappa_f`
        """
        return self.scatterer.kappa_f

    # -------------------------------------------------------------------------
    # Wrappers for Independent Fluid Attributes
    # -------------------------------------------------------------------------

    @property
    def rho_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.InviscidFluid.rho_f`
        """
        return self.fluid.rho_f

    @rho_f.setter
    def rho_f(self, value: float) -> None:
        self.fluid.rho_f = value

    @property
    def c_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.InviscidFluid.c_f`
        """
        return self.fluid.c_f

    @c_f.setter
    def c_f(self, value: float) -> None:
        self.fluid.c_f = value

    # -------------------------------------------------------------------------
    # Wrappers for Dependent Fluid Attributes
    # -------------------------------------------------------------------------

    @property
    def kappa_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.InviscidFluid.kappa_f`
        """
        return self.fluid.kappa_f

    @property
    def k_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.InviscidFluid.k_f`
        """
        return self.field.k_f

    # -------------------------------------------------------------------------
    # Dependent Variables Methods
    # -------------------------------------------------------------------------

    def _compute_f_1(self) -> float:
        return 1 - self.kappa_s / self.kappa_f

    def _compute_f_2(self) -> float:
        rho_tilde = self.rho_s / self.rho_f
        return 2 * (rho_tilde - 1) / (2 * rho_tilde + 1)

    def _compute_Phi(self):
        return self.f_1 / 3 + self.f_2 / 2


if __name__ == '__main__':
    pass
