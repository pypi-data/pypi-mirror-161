from __future__ import annotations

from typing import Optional, Union

from osaft.core.backgroundfields import BackgroundField, WaveType
from osaft.core.basecomposite import BaseSphereFrequencyComposite
from osaft.core.fluids import InviscidFluid
from osaft.core.frequency import Frequency
from osaft.core.geometries import Sphere
from osaft.core.solids import ElasticSolid
from osaft.core.variable import ActiveVariable
from osaft.solutions.base_solution import BaseSolution


class BaseHasegawa(BaseSphereFrequencyComposite, BaseSolution):
    """Base class for Hasegawa & Yosioka (1969)

    :param f: Frequency [Hz]
    :param R_0: Radius of the particle [m]
    :param rho_s: Density of the solid scattering particle [kg/m^3]
    :param E_s: Young's modulus of the solid scattering particle [N/m^2]
    :param nu_s: Poisson's ratio of the solid scattering particle [-]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound in the fluid [m/s]
    :param p_0: Pressure amplitude of the incident field [Pa]
    :param position: Position in the standing wave field [rad]
    :param wave_type: Progressive wave [-]
    """

    # Supported wave_type for the class
    supported_wavetypes = [WaveType.TRAVELLING, WaveType.STANDING]

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float, E_s: float, nu_s: float,
        rho_f: float, c_f: float,
        p_0: float, wave_type: WaveType,
        position: Optional[float] = None,
    ) -> None:

        """Constructor method
        """
        BaseSphereFrequencyComposite.__init__(self, f, R_0)
        BaseSolution.__init__(self, 'Hasegawa1969')

#       Initialize Components
        self.scatterer = ElasticSolid(self.frequency, E_s, nu_s, rho_s)
        self.fluid = InviscidFluid(self.frequency, rho_f, c_f)
        self.field = BackgroundField(self.fluid, p_0, wave_type, position)

#       Dependent variables
        self._lambda_rho = ActiveVariable(
            self._compute_lambda_rho,
            'ratio of densities',
        )
        self._x_f = ActiveVariable(
            self._compute_x_f,
            'dimensionless fluid wavenumber',
        )
        self._x_s_l = ActiveVariable(
            self._compute_x_s_l,
            'dimensionless particle wavenumber, longitudinal direction',
        )
        self._x_s_t = ActiveVariable(
            self._compute_x_s_t,
            'dimensionless particle wavenumber, transversal direction',
        )

#       Dependencies
        self._lambda_rho.is_computed_by(
            self.scatterer._rho_s,
            self.fluid._rho_f,
        )
        self._x_f.is_computed_by(self.sphere._R_0, self.fluid._k_f)
        self._x_s_l.is_computed_by(self.sphere._R_0, self.scatterer._k_l)
        self._x_s_t.is_computed_by(self.sphere._R_0, self.scatterer._k_t)

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def x_f(self) -> float:
        """ dimensionless wave number in the fluid [-]
        """
        return self._x_f.value

    @property
    def x_s_l(self) -> float:
        """ dimensionless wave number in the particle,
        longitudinal direction [-]
        """
        return self._x_s_l.value

    @property
    def x_s_t(self) -> float:
        """ dimensionless wave number in the particle,
        transversal direction [-]
        """
        return self._x_s_t.value

    @property
    def lambda_rho(self) -> float:
        """ratio of densities [-]
         """
        return self._lambda_rho.value

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
        """Wraps to :attr:`osaft.core.solids.ElasticSolid.rho_s`
        """
        return self.scatterer.rho_s

    @rho_s.setter
    def rho_s(self, value: float) -> None:
        self.scatterer.rho_s = value

    @property
    def E_s(self) -> float:
        """Wraps to :attr:`osaft.core.solids.ElasticSolid.E_s`
        """
        return self.scatterer.E_s

    @E_s.setter
    def E_s(self, value: float) -> None:
        self.scatterer.E_s = value

    @property
    def nu_s(self) -> float:
        """Wraps to :attr:`osaft.core.solids.ElasticSolid.nu_s`
        """
        return self.scatterer.nu_s

    @nu_s.setter
    def nu_s(self, value: float) -> None:
        self.scatterer.nu_s = value

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
    # Wrappers for Dependent Scatterer Attributes
    # -------------------------------------------------------------------------

    @property
    def k_s_l(self) -> float:
        """Wraps to :attr:`osaft.core.solids.ElasticSolid.k_l`
        """
        return self.scatterer.k_l

    @property
    def k_s_t(self) -> float:
        """Wraps to :attr:`osaft.core.solids.ElasticSolid.k_t`
        """
        return self.scatterer.k_t

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
    # Wrappers for Dependent Field Attributes
    # -------------------------------------------------------------------------

    def A_in(self, n) -> complex:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.A_in`
        """
        return self.field.A_in(n)

    # -------------------------------------------------------------------------
    # Dependent Variables Methods
    # -------------------------------------------------------------------------
    def _compute_lambda_rho(self) -> float:
        """Compute lambda (ratio of densities)
        """
        return self.rho_s / self.rho_f

    def _compute_x_f(self) -> float:
        """Compute x_f
        """
        return self.R_0 * self.k_f

    def _compute_x_s_l(self) -> float:
        """Compute x_s_l
        """
        return self.R_0 * self.k_s_l

    def _compute_x_s_t(self) -> float:
        """Compute x_s_t
        """
        return self.R_0 * self.k_s_t


if __name__ == '__main__':
    pass
