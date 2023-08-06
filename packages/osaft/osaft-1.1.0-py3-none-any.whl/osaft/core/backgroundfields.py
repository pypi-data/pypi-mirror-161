from __future__ import annotations

from enum import Enum
from typing import Optional

from numpy import absolute

from osaft import log
from osaft.core.fluids import InviscidFluid
from osaft.core.functions import exp
from osaft.core.variable import (
    ActiveListVariable,
    ActiveVariable,
    PassiveVariable,
)


class DocEnum(Enum):
    def __new__(cls, value, doc=None):
        self = object.__new__(cls)
        self._value_ = value
        self.__doc__ = doc
        return self


class WaveType(DocEnum):
    """Supported Wavetypes for the acoustic background field
    """

    STANDING = 0, 'Plane standing wave'
    TRAVELLING = 1, 'Plane travelling wave'


class WrongWaveTypeError(Exception):
    """ Exception for using the wrong Wave type
    """

    def __init__(self, msg=None, *args, **kwargs):
        if msg is None:
            msg = (
                'Wavetype needs to be of type:'
                f' {[t.name for t in WaveType]}'
            )
        super().__init__(msg, *args, **kwargs)


class BackgroundField:
    """BackgroundField class which is a base class for all background field
    classes

    :param fluid: fluid for to be used for the background field
    :param p_0: pressure amplitude in [Pa]
    :param wave_type: wave type: either standing or traveling / travelling
    :param position: position of the scatterer in the standing wave in [rad]
    """

    def __init__(
        self, fluid: InviscidFluid,
        p_0: float,
        wave_type: WaveType = WaveType.STANDING,
        position: Optional[float] = None,
    ) -> None:
        """Constructor Method
        """

        self.fluid = fluid

        # Check position variable
        if position is None and wave_type == WaveType.STANDING:
            raise ValueError(
                'Argument position needs to be given for a '
                'standing wave.',
            )

        # Independent Variables
        self._p_0 = PassiveVariable(p_0, 'pressure amplitude p_0')
        self._wave_type = PassiveVariable(wave_type, 'wave type')
        self._position = PassiveVariable(position, 'scatterer position d')

        # Dependent variables
        self._abs_pos = ActiveVariable(
            self._compute_abs_pos,
            'absolute position in the standing wave',
        )

        self._A = ActiveVariable(
            self._compute_A,
            'velocity potential amplitude A',
        )
        self._abs_A_squared = ActiveVariable(
            self._compute_abs_A_squared,
            'squared absolute amplitude A',
        )
        self._A_in = ActiveListVariable(
            self._compute_A_in,
            'velocity potential amplitude A_n',
        )
        self._E = ActiveVariable(
            self._compute_E,
            'acoustic energy density E',
        )
        self._I = ActiveVariable(
            self._compute_I,
            'acoustic intensity I',
        )
        # Dependencies
        self._abs_pos.is_computed_by(self.fluid._k_f, self._position)

        self._A.is_computed_by(
            self.fluid.frequency._omega,
            self.fluid._rho_f,
            self._p_0,
        )

        self._abs_A_squared.is_computed_by(self._A)

        self._A_in.is_computed_by(
            self._abs_pos,
            self._A,
            self._wave_type,
        )

        self._E.is_computed_by(
            self._A,
            self.fluid._rho_f,
            self.fluid._k_f,
        )

        self._I.is_computed_by(
            self._A,
            self.fluid._rho_f,
            self.fluid._k_f,
            self.fluid._c_f,
        )

        log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return (
            f'BackgroundField(fluid={self.fluid}, p_0={self.p_0} '
            f'wave_type={self.wave_type}, position={self.position})'
        )

    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def p_0(self) -> float:
        """Background pressure amplitude of the acoustic field [Pa]

        :getter: returns the value for the pressure amplitude
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._p_0.value

    @p_0.setter
    def p_0(self, value: float) -> None:
        self._p_0.value = value

    @property
    def wave_type(self) -> WaveType:
        """Wave type of the acoustic background field

        :getter: returns the wave type
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._wave_type.value

    @wave_type.setter
    def wave_type(self, value: WaveType) -> None:
        self._wave_type.value = value

    @property
    def position(self) -> float:
        """Position of the particle in an acoustic standing wave field [rad]

        :getter: returns the wave type
        :setter: automatically invokes
           :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._position.value

    @position.setter
    def position(self, value: float) -> None:
        self._position.value = value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def abs_pos(self) -> float:
        """Absolute position of the scatterer in the standing wave in [m] """
        return self._abs_pos.value

    @property
    def A(self) -> complex:
        """Amplitude of the pressure wave [Pa]
        """
        return self._A.value

    @property
    def abs_A_squared(self) -> float:
        """:math:`A\\,\\text{conj}(A) = |A|^2` [Pa^2]
        """
        return self._abs_A_squared.value

    @property
    def E_ac(self) -> float:
        """Mean acoustic energy density [J/m^3]
        """
        if not isinstance(self.wave_type, WaveType):
            raise WrongWaveTypeError

        return self._E.value

    @property
    def I_ac(self) -> float:
        """Acoustic intensity / energy flux density [W/m^2]
        """
        if self.wave_type != WaveType.TRAVELLING:
            raise WrongWaveTypeError(
                'The acoustic intensity is only '
                'defined for: '
                f'{WaveType.TRAVELLING}',
            )
        return self._I.value

    # -------------------------------------------------------------------------
    # Method for Dependent Variables
    # -------------------------------------------------------------------------

    def _compute_A(self) -> complex:
        return self.p_0 / (1j * self.omega * self.rho_f)

    def _compute_abs_A_squared(self) -> complex:
        return absolute(self.A)**2

    # -------------------------------------------------------------------------
    # Wrapper Methods for Frequency
    # -------------------------------------------------------------------------

    @property
    def f(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.InviscidFluid.f`
        """
        return self.fluid.f

    @f.setter
    def f(self, value) -> None:
        self.fluid.f = value

    @property
    def omega(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.InviscidFluid.omega`
        """
        return self.fluid.omega

    # -------------------------------------------------------------------------
    # Wrapper Methods for Independent Fluid Attributes
    # -------------------------------------------------------------------------

    @property
    def c_f(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.InviscidFluid.c_f`
        """
        return self.fluid.c_f

    @c_f.setter
    def c_f(self, value) -> None:
        self.fluid.c_f = value

    @property
    def rho_f(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.InviscidFluid.rho_f`
        """
        return self.fluid.rho_f

    @rho_f.setter
    def rho_f(self, value) -> None:
        self.fluid.rho_f = value

    @property
    def eta_f(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.ViscousFluid.eta_f`
        """
        try:
            return self.fluid.eta_f
        except AttributeError:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute eta_f',
            )
            return 0

    @eta_f.setter
    def eta_f(self, value) -> None:
        if hasattr(self.fluid, 'eta_f'):
            self.fluid.eta_f = value
        else:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute eta_f',
            )

    @property
    def zeta_f(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.ViscousFluid.zeta_f`
        """
        try:
            return self.fluid.zeta_f
        except AttributeError:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute zeta_f',
            )
            return 0

    @zeta_f.setter
    def zeta_f(self, value) -> None:
        if hasattr(self.fluid, 'zeta_f'):
            self.fluid.zeta_f = value
        else:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute zeta_f',
            )

    @property
    def eta_p(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.ViscoelasticFluid.eta_p`
        """
        try:
            return self.fluid.eta_p
        except AttributeError:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute eta_p',
            )
            return 0

    @eta_p.setter
    def eta_p(self, value) -> None:
        if hasattr(self.fluid, 'eta_p'):
            self.fluid.eta_p = value
        else:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute eta_p',
            )

    @property
    def zeta_p(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.ViscoelasticFluid.zeta_p`
        """
        try:
            return self.fluid.zeta_p
        except AttributeError:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute zeta_p',
            )
            return 0

    @zeta_p.setter
    def zeta_p(self, value) -> None:
        if hasattr(self.fluid, 'zeta_p'):
            self.fluid.zeta_p = value
        else:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute zeta_p',
            )

    @property
    def lambda_M(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.ViscoelasticFluid.lambda_M`
        """
        try:
            return self.fluid.lambda_M
        except AttributeError:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute lambda_M',
            )
            return 0

    @lambda_M.setter
    def lambda_M(self, value) -> None:
        if hasattr(self.fluid, 'lambda_M'):
            self.fluid.lambda_M = value
        else:
            log.warning(
                'underlying fluid class of BackgroundField doesn\'t '
                'have attribute lambda_M',
            )

    # -------------------------------------------------------------------------
    # Wrapper Methods for Dependent Fluid Attributes
    # -------------------------------------------------------------------------

    @property
    def lambda_f(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.InviscidFluid.lambda_f`
        """
        return self.fluid.lambda_f

    @property
    def k_f(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.InviscidFluid.k_f`
        """
        return self.fluid.k_f

    @property
    def k_v(self) -> complex:
        """ wrapper for :attr:`osaft.core.fluids.ViscousFluid.k_v`
        """
        return self.fluid.k_v

    @property
    def kappa_f(self) -> float:
        """ wrapper for :attr:`osaft.core.fluids.ViscousFluid.kappa_f`
        """
        return self.fluid.kappa_f

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def _compute_abs_pos(self) -> float:
        return self.position / self.k_f.real

    def _compute_A_in(self, n: int) -> complex:
        if not isinstance(self.wave_type, WaveType):
            raise WrongWaveTypeError

        if self.wave_type == WaveType.TRAVELLING:
            return self._compute_A_in_travelling(n)
        else:
            return self._compute_A_in_standing(n)

    def _compute_A_in_travelling(self, n: int) -> complex:
        return self.A * (2 * n + 1) * 1j ** n

    def _compute_A_in_standing(self, n: int) -> complex:
        out = exp(1j * self.abs_pos * self.k_f)
        out += (-1) ** n * exp(-1j * self.abs_pos * self.k_f)

        out *= self.A / 2 * (2 * n + 1) * 1j ** n
        return out

    def A_in(self, n: int) -> complex:
        """Incident amplitude at order n [Pa]

        :param n: order
        """
        return self._A_in.item(n)

    def _compute_E(self) -> float:
        return (self.fluid.kappa_f * self.p_0**2) / 4

    def _compute_I(self) -> float:
        out = self.abs_A_squared * self.rho_f * self.fluid.c_f
        out *= (self.fluid.k_f ** 2) / 2
        return out


if __name__ == '__main__':
    pass
