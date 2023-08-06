from typing import Optional, Union

from osaft import BackgroundField, ViscousFluid, WaveType
from osaft.core.basecomposite import BaseSphereFrequencyComposite
from osaft.core.frequency import Frequency
from osaft.core.geometries import Sphere
from osaft.core.variable import ActiveVariable


class BaseDoinikov1994(BaseSphereFrequencyComposite):
    """Base class for Doinikov solutions from 1994

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param eta_f: shear viscosity [Pa s]
    :param zeta_f: bulk viscosity [Pa s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param wave_type: Type of wave, traveling or standing
    :param position: Position in the standing wave field [rad]
    """

    def __init__(
        self,
        f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_f: float,
        c_f: float,
        eta_f: float,
        zeta_f: float,
        p_0: float,
        wave_type: Optional[WaveType] = WaveType.STANDING,
        position: Optional[float] = None,
    ) -> None:

        super().__init__(f, R_0)

        self.fluid = ViscousFluid(self.frequency, rho_f, c_f, eta_f, zeta_f)
        self.field = BackgroundField(self.fluid, p_0, wave_type, position)

        # Dependent Variables
        self._x = ActiveVariable(
            self._compute_x,
            'Dimensionless wavenumber',
        )
        self._x_0 = ActiveVariable(
            self._compute_x_0,
            'Real part of the dimensionless wavenumber ',
        )
        self._x_v = ActiveVariable(
            self._compute_x_v,
            'Dimensionless viscous wavenumber',
        )
        self._norm_delta = ActiveVariable(
            self._compute_norm_delta,
            'normalized boundary layer thickness',
        )
        self._x.is_computed_by(
            self.fluid._k_f, self.sphere._R_0,
        )
        self._x_0.is_computed_by(
            self._x,
        )
        self._x_v.is_computed_by(
            self.fluid._k_v, self.sphere._R_0,
        )
        self._norm_delta.is_computed_by(
            self.fluid._delta, self.sphere._R_0,
        )

    # -------------------------------------------------------------------------
    # Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def x(self) -> complex:
        """Product of :attr:`~.k_f` and :attr:`~.R_0`
        :math:`\\hat{x}=k_f R_0`
        """
        return self._x.value

    def _compute_x(self) -> complex:
        return self.k_f * self.R_0

    @property
    def x_v(self) -> complex:
        """Product of :attr:`~.k_v` and :attr:`~.R_0`
        :math:`x_v=k_v R_0`
        """
        return self._x_v.value

    def _compute_x_v(self) -> complex:
        return self.k_v * self.R_0

    @property
    def x_0(self) -> complex:
        """Real part of :math:`x`
        """
        return self._x_0.value

    def _compute_x_0(self) -> complex:
        return self.x.real

    @property
    def norm_delta(self) -> float:
        """ normalized viscous boundary thickness
        :math:`\\tilde{\\delta}=\\frac{\\delta}{R_0}`
        """
        return self._norm_delta.value

    def _compute_norm_delta(self):
        return self.delta / self.R_0

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
    # Wrappers for Independent Fluid Attributes
    # -------------------------------------------------------------------------

    @property
    def rho_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.ViscousFluid.rho_f`
        """
        return self.fluid.rho_f

    @rho_f.setter
    def rho_f(self, value: float) -> None:
        self.fluid.rho_f = value

    @property
    def c_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.ViscousFluid.c_f`
        """
        return self.fluid.c_f

    @c_f.setter
    def c_f(self, value: float) -> None:
        self.fluid.c_f = value

    @property
    def eta_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.ViscousFluid.eta_f`
        """
        return self.fluid.eta_f

    @eta_f.setter
    def eta_f(self, value: float) -> None:
        self.fluid.eta_f = value

    @property
    def zeta_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.ViscousFluid.zeta_f`
        """
        return self.fluid.zeta_f

    @zeta_f.setter
    def zeta_f(self, value: float) -> None:
        self.fluid.zeta_f = value
    # -------------------------------------------------------------------------
    # Wrappers for Dependent Attributes
    # -------------------------------------------------------------------------

    @property
    def rho_t(self) -> float:
        """ Returns the ratio of the densities
        :math:`\\tilde{\\rho}=\\frac{\\rho_f}{\\rho_s}`
        """
        return self._rho_t.value

    def _compute_rho_t(self) -> float:
        return self.rho_f / self.rho_s

    # -------------------------------------------------------------------------
    # Wrappers for Dependent Fluid Attributes
    # -------------------------------------------------------------------------

    @property
    def kappa_f(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.ViscousFluid.kappa_f`
        """
        return self.fluid.kappa_f

    @property
    def k_f(self) -> complex:
        """ Wraps to :attr:`osaft.core.fluids.ViscousFluid.k_f`
        """
        return self.fluid.k_f

    @property
    def k_v(self) -> complex:
        """ Wraps to :attr:`osaft.core.fluids.ViscousFluid.k_v`
        """
        return self.fluid.k_v

    @property
    def delta(self) -> float:
        """ Wraps to :attr:`osaft.core.fluids.ViscousFluid.delta`
        """
        return self.fluid.delta

    # -------------------------------------------------------------------------
    # Wrappers for Dependent Field Attributes
    # -------------------------------------------------------------------------

    @property
    def abs_pos(self) -> float:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.abs_pos`
        """
        return self.field.abs_pos

    def A_in(self, n) -> complex:
        """Wraps to
        :attr:`osaft.core.backgroundfields.BackgroundField.A_in`
        """
        return self.field.A_in(n)


if __name__ == '__main__':
    pass
