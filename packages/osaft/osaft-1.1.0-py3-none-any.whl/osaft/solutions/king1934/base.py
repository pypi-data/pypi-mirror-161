from typing import Union

from osaft.core.backgroundfields import BackgroundField, WaveType
from osaft.core.basecomposite import BaseSphereFrequencyComposite
from osaft.core.fluids import InviscidFluid
from osaft.core.frequency import Frequency
from osaft.core.geometries import Sphere
from osaft.core.solids import RigidSolid
from osaft.core.variable import ActiveVariable
from osaft.solutions.base_solution import BaseSolution


class BaseKing(BaseSphereFrequencyComposite, BaseSolution):
    """Base class for King (1934)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
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
        rho_s: float,
        rho_f: float, c_f: float,
        p_0: float, wave_type: WaveType, position: Union[None, float],
    ) -> None:
        """Constructor method
        """

        # init of parent class
        BaseSphereFrequencyComposite.__init__(self, f, R_0)
        BaseSolution.__init__(self, 'King1934')

        # Initialize Components
        self.scatterer = RigidSolid(self.frequency, rho_s)
        self.fluid = InviscidFluid(self.frequency, rho_f, c_f)
        self.field = BackgroundField(self.fluid, p_0, wave_type, position)

        self._alpha = ActiveVariable(
            self._compute_alpha,
            'wave number times radius of sphere',
        )
        self._rho_tilde = ActiveVariable(
            self._compute_rho_tilde,
            'rho_s over rho_f',
        )

        # Dependencies
        self._alpha.is_computed_by(self.fluid._k_f, self.sphere._R_0)
        self._rho_tilde.is_computed_by(
            self.fluid._rho_f,
            self.scatterer._rho_s,
        )

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def alpha(self):
        """Wave number times radius of the particle (:math:`kR`) [-]
        """
        return self._alpha.value

    @property
    def rho_tilde(self) -> float:
        """Density ratio :attr:`~.rho_s`/ :attr:`~.rho_f` [-]
        """
        return self._rho_tilde.value

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

    def A_in(self, n: int) -> complex:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.A_in`
        """
        return self.field.A_in(n)

    # -------------------------------------------------------------------------
    # Wrappers for Independent Scatterer Attributes
    # -------------------------------------------------------------------------

    @property
    def rho_s(self) -> float:
        """ Wraps to :attr:`osaft.core.solids.RigidSolid.rho_s`
        """
        return self.scatterer.rho_s

    @rho_s.setter
    def rho_s(self, value: float) -> None:
        self.scatterer.rho_s = value

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

    def _compute_alpha(self) -> float:
        return self.k_f * self.R_0

    def _compute_rho_tilde(self) -> float:
        return self.rho_s / self.rho_f


if __name__ == '__main__':
    pass
