from __future__ import annotations

from typing import Optional, Union

from osaft.core.backgroundfields import BackgroundField, WaveType
from osaft.core.basecomposite import BaseSphereFrequencyComposite
from osaft.core.fluids import InviscidFluid
from osaft.core.frequency import Frequency
from osaft.core.geometries import Sphere
from osaft.core.variable import ActiveVariable
from osaft.solutions.base_solution import BaseSolution


class BaseYosioka(BaseSphereFrequencyComposite, BaseSolution):
    """Base class for Yosioka & Kawasima (1955)

    :param f: Frequency [Hz]
    :param R_0: Radius of the particle [m]
    :param rho_s: Density of the fluid-like sphere [kg/m^3]
    :param c_s: Speed of sound of the particle [m/s]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound in the fluid [m/s]
    :param p_0: Pressure amplitude of the incident field [Pa]
    :param position: Position in the standing wave field [rad]
    :param wave_type: Either in or progressive wave [-]
    """

    # Supported wave_type for the class
    supported_wavetypes = [WaveType.STANDING, WaveType.TRAVELLING]

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float, c_s: float,
        rho_f: float, c_f: float,
        p_0: float, wave_type: WaveType,
        position: Optional[float] = None,
    ) -> None:

        """Constructor method
        """
        # init of parent class
        BaseSphereFrequencyComposite.__init__(self, f, R_0)
        BaseSolution.__init__(self, 'Yosioka1955')

        # Initialize Components
        self.scatterer = InviscidFluid(self.frequency, rho_s, c_s)
        self.fluid = InviscidFluid(self.frequency, rho_f, c_f)
        self.field = BackgroundField(self.fluid, p_0, wave_type, position)

        # Dependent variables
        self._lambda_rho = ActiveVariable(
            self._compute_lambda_rho,
            'ratio of densities',
        )
        self._sigma = ActiveVariable(
            self._compute_sigma,
            'ratio of speed of sounds',
        )

        self._x_f = ActiveVariable(
            self._compute_x_f,
            'dimensionless fluid wavenumber',
        )
        self._x_s = ActiveVariable(
            self._compute_x_s,
            'dimensionless particle wavenumber',
        )

        # Dependencies
        self._lambda_rho.is_computed_by(
            self.scatterer._rho_f,
            self.fluid._rho_f,
        )
        self._sigma.is_computed_by(self.scatterer._c_f, self.fluid._c_f)
        self._x_f.is_computed_by(self.sphere._R_0, self.fluid._k_f)
        self._x_s.is_computed_by(self.sphere._R_0, self.scatterer._k_f)

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def sigma(self) -> float:
        """ratio of speeds of sound [-].
         """
        return self._sigma.value

    @property
    def lambda_rho(self) -> float:
        """ratio of densities [-]
         """
        return self._lambda_rho.value

    @property
    def x_f(self) -> float:
        """ dimensionless wavenumber in the fluid [-]
        """
        return self._x_f.value

    @property
    def x_s(self) -> float:
        """ dimensionless wavenumber in the particle
        """
        return self._x_s.value

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
        """Wraps to :attr:`osaft.core.backgroundfields.BackgroundField.p_0`
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
    # Wrappers for Independent Scatterer Attributes
    # -------------------------------------------------------------------------

    @property
    def rho_s(self) -> float:
        """Wraps to :attr:`osaft.core.fluids.InviscidFluid.rho_f`
        """
        return self.scatterer.rho_f

    @rho_s.setter
    def rho_s(self, value: float) -> None:
        self.scatterer.rho_f = value

    @property
    def c_s(self) -> float:
        """Wraps to :attr:`osaft.core.fluids.InviscidFluid.c_f`
        """
        return self.scatterer.c_f

    @c_s.setter
    def c_s(self, value: float) -> None:
        self.scatterer.c_f = value

    # -------------------------------------------------------------------------
    # Wrappers for Independent Fluid Attributes
    # -------------------------------------------------------------------------

    @property
    def rho_f(self) -> float:
        """Wraps to :attr:`osaft.core.fluids.InviscidFluid.rho_f`
        """
        return self.fluid.rho_f

    @rho_f.setter
    def rho_f(self, value: float) -> None:
        self.fluid.rho_f = value

    @property
    def c_f(self) -> float:
        """Wraps to :attr:`osaft.core.fluids.InviscidFluid.c_f`
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
        """Wraps to :attr:`osaft.core.fluids.InviscidFluid.kappa_f`
        """
        return self.fluid.kappa_f

    @property
    def k_f(self) -> float:
        """Wraps to :attr:`osaft.core.fluids.InviscidFluid.k_f`
        """
        return self.fluid.k_f

    # -------------------------------------------------------------------------
    # Wrappers for Dependent Scatterer Attributes
    # -------------------------------------------------------------------------

    @property
    def k_s(self) -> float:
        """Wraps to :attr:`osaft.core.fluids.InviscidFluid.k_f`
        """
        return self.scatterer.k_f

    # -------------------------------------------------------------------------
    # Wrappers for Dependent Field Attributes
    # -------------------------------------------------------------------------

    @property
    def I_ac(self) -> float:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.I_ac`
        """
        return self.field.I_ac

    @property
    def E_ac(self) -> float:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.E_ac`
        """
        return self.field.E_ac

    def A_in(self, n) -> complex:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.A_in`
        """
        return self.field.A_in(n)

    # -------------------------------------------------------------------------
    # Dependent Variables Methods
    # -------------------------------------------------------------------------

    def _compute_sigma(self) -> float:
        """Compute sigma (ratio of speed of sound)
        """
        return self.c_s / self.c_f

    def _compute_lambda_rho(self) -> float:
        """Compute lambda (ratio of densities)
        """
        return self.rho_s / self.rho_f

    def _compute_x_f(self) -> float:
        """Compute x_f
        """
        return self.R_0 * self.k_f

    def _compute_x_s(self) -> float:
        """Compute x_s
        """
        return self.R_0 * self.k_s


if __name__ == '__main__':
    pass
