from typing import Union

from osaft import log
from osaft.core.basecomposite import BaseFrequencyComposite
from osaft.core.frequency import Frequency
from osaft.core.functions import pi, sqrt
from osaft.core.variable import ActiveVariable, PassiveVariable


class InviscidFluid(BaseFrequencyComposite):
    """Class for an inviscid fluid

    :param frequency: frequency in [Hz]
    :param rho: density in [km/m^3]
    :param c: speed of sound [m/s]
    """

    def __init__(
        self, frequency: Union[int, float, Frequency],
        rho: float, c: float,
    ) -> None:
        """Constructor method
        """

        super().__init__(frequency)

        # Independent Variables
        self._rho_f = PassiveVariable(rho, 'density rho')
        self._c_f = PassiveVariable(c, 'speed of sound c')

        # Dependent variables
        self._k_f = ActiveVariable(self._compute_k_f, 'wavenumber k_f')
        self._kappa_f = ActiveVariable(
            self._compute_kappa_f,
            'compressibility kappa_f',
        )
        self._lambda_f = ActiveVariable(
            self._compute_lambda_f,
            'wavelength lambda_f',
        )

        # Dependencies
        self._k_f.is_computed_by(self._c_f, self.frequency._omega)
        self._lambda_f.is_computed_by(self._c_f, self.frequency._f)
        self._kappa_f.is_computed_by(self._c_f, self._rho_f)

        if type(self) is InviscidFluid:
            log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return (
            'InviscidFluid('
            f'frequency={self.frequency}, '
            f'rho={self.rho_f}, '
            f'c={self.c_f}'
            ')'
        )

    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------
    @property
    def c_f(self) -> float:
        r"""Speed of sound in the fluid :math:`c_f` [m\s].

        :getter: returns the value for the frequency
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._c_f.value

    @c_f.setter
    def c_f(self, value: float) -> None:
        self._c_f.value = value

    @property
    def rho_f(self) -> float:
        """Density of the fluid :math:`\\rho_f` [kg/m^3].

        :getter: returns the value for the density
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._rho_f.value

    @rho_f.setter
    def rho_f(self, value: float) -> None:
        self._rho_f.value = value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def kappa_f(self) -> float:
        r"""Returns the compressibility of the fluid :math:`\kappa_f` [1/Pa]
        """
        return self._kappa_f.value

    @property
    def k_f(self) -> float:
        """Returns the wave number :math:`k_f` [rad s^-1]
        """
        return self._k_f.value

    @property
    def lambda_f(self) -> float:
        """Returns the wavelength  :math:`\\lambda_f` [m]
        """
        return self._lambda_f.value

    # -------------------------------------------------------------------------
    # Dependent Variables Methods
    # -------------------------------------------------------------------------

    def _compute_k_f(self) -> float:
        return self.omega / self.c_f

    def _compute_kappa_f(self) -> float:
        return 1 / self.c_f**2 / self.rho_f

    def _compute_lambda_f(self) -> float:
        return self.c_f / self.f


class ViscousFluid(InviscidFluid):
    """Class for a viscous fluid

    :param frequency: frequency in [Hz]
    :param rho: density in [km/m^3]
    :param c: speed of sound [m/s]
    :param eta_f: shear viscosity [Pa s]
    :param zeta_f: bulk viscosity [Pa s]
        """

    def __init__(
        self, frequency: Union[int, float, Frequency], rho: float,
        c: float, eta_f: float,
        zeta_f: float,
    ):
        """Constructor method
        """

        super().__init__(frequency, rho, c)

        # Independent Variables
        self._eta_f = PassiveVariable(eta_f, 'shear viscosity eta_f')
        self._zeta_f = PassiveVariable(zeta_f, 'bulk viscosity zeta_f')

        # Dependent Variables
        self._k_v = ActiveVariable(self._compute_k_v, 'viscous wavenumber k_v')
        self._delta = ActiveVariable(
            self._compute_delta,
            'boundary layer thickness delta',
        )
        self._lambda_v = ActiveVariable(
            self._compute_lambda_v,
            'viscous wavelength lambda_v',
        )

        # Dependencies
        self._k_v.is_computed_by(
            self.frequency._omega, self._rho_f,
            self._eta_f,
        )

        self._k_f.is_computed_by(self._rho_f, self._eta_f, self._zeta_f)

        self._lambda_v.is_computed_by(self._k_v)
        self._delta.is_computed_by(self._k_v)

        if type(self) is ViscousFluid:
            log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return(
            'ViscousFluid('
            f'frequency={self.frequency}, '
            f'rho={self.rho_f}, '
            f'c={self.c_f}, '
            f'eta_f={self.eta_f}, '
            f'zeta_f={self.zeta_f}'
            ')'
        )
    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def eta_f(self) -> float:
        """Shear viscosity of the fluid :math:`\\eta_f` [Pa s].

        :getter: returns the shear viscosity
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._eta_f.value

    @eta_f.setter
    def eta_f(self, value: float) -> None:
        self._eta_f.value = value

    @property
    def zeta_f(self) -> float:
        """Bulk viscosity of the fluid :math:`\\zeta_f` [Pa s].

        :getter: returns the bulk viscosity
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._zeta_f.value

    @zeta_f.setter
    def zeta_f(self, value: float) -> None:
        self._zeta_f.value = value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def k_f(self) -> complex:
        """Returns the wave number in the fluid :math:`k_f` [1/m]
        """
        return self._k_f.value

    @property
    def k_v(self) -> complex:
        """Returns the viscous wave number in the fluid :math:`k_v` [1/m]
        """
        return self._k_v.value

    @property
    def delta(self) -> float:
        """Returns the boundary layer thickness :math:`\\delta` [m]
        """
        return self._delta.value

    @property
    def lambda_v(self) -> float:
        """Returns the viscous wave length :math:`\\lambda_v` [m]
        """
        return self._lambda_v.value

    # -------------------------------------------------------------------------
    # Dependent Variables Methods
    # -------------------------------------------------------------------------

    def _compute_k_f(self) -> complex:
        out = -1j * self.omega / (self.rho_f * self.c_f ** 2)
        out *= self.zeta_f + 4 * self.eta_f / 3
        out += 1

        return self.omega / self.c_f / sqrt(out)

    def _compute_k_v(self) -> complex:
        if self.eta_f != 0:
            return (1 + 1j) * sqrt(self.rho_f * self.omega / (2 * self.eta_f))
        else:
            return 0

    def _compute_delta(self) -> float:
        if self.k_v != 0:
            return 1 / self.k_v.imag
        else:
            return 0

    def _compute_lambda_v(self) -> float:
        if self.k_v != 0:
            return 2 * pi / self.k_v.real
        else:
            return 0


class ViscoelasticFluid(ViscousFluid):
    """Class for a viscoelastic fluid

    :param frequency: frequency in [Hz]
    :param rho: density in [km/m^3]
    :param c: speed of sound [m/s]
    :param eta_f: shear viscosity of fluid component [Pa s]
    :param zeta_f: bulk viscosity of fluid component [Pa s]
    :param eta_p: shear viscosity of polymer component [Pa s]
    :param zeta_p: bulk viscosity of polymer component [Pa s]
    :param zeta_p: relaxation time [s]
    :param lambda_M: relaxation time of fluid [s]
        """

    def __init__(
        self, frequency: Union[int, float, Frequency],
        rho: float, c: float,
        eta_f: float, eta_p: float, zeta_f: float, zeta_p: float,
        lambda_M: float,
    ):
        """Constructor method
        """

        super().__init__(frequency, rho, c, eta_f, zeta_f)

        # Independent Variables
        self._eta_p = PassiveVariable(
            eta_p,
            'shear viscosity of polymer component '
            'eta_p',
        )
        self._zeta_p = PassiveVariable(
            zeta_p,
            'shear viscosity of polymer component '
            'zeta_p',
        )
        self._lambda_M = PassiveVariable(
            lambda_M,
            'relaxation time lambda_M',
        )

        # Dependent variables
        self._eta_c = ActiveVariable(self._compute_eta_c)
        self._zeta_c = ActiveVariable(self._compute_zeta_c)

        # Dependencies
        self._k_f.is_computed_by(
            self.frequency._omega,
            self._c_f, self._rho_f,
            self._eta_c, self._zeta_c,
        )

        self._k_v.is_computed_by(self._eta_c, self._zeta_c)

        self._eta_c.is_computed_by(
            self.frequency._omega, self._eta_f,
            self._eta_p, self._lambda_M,
        )

        self._zeta_c.is_computed_by(
            self.frequency._omega,
            self._zeta_f, self._zeta_p,
            self._lambda_M,
        )

        # no if clause needed because last in inheritance
        log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return(
            'ViscoelasticFluid('
            f'frequency={self.frequency}, '
            f'rho={self.rho_f}, '
            f'c={self.c_f}, '
            f'eta_f={self.eta_f}, '
            f'eta_p={self.eta_p}, '
            f'zeta_f={self.zeta_f}, '
            f'zeta_p={self.zeta_p}, '
            f'lambda_M={self.lambda_M} '
            ')'
        )
    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def eta_p(self) -> float:
        """Polymer component shear viscosity :math:`\\eta_p` [Pa s]

        :getter: Returns the polymer component shear viscosity
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._eta_p.value

    @eta_p.setter
    def eta_p(self, value: float) -> None:
        self._eta_p.value = value

    @property
    def zeta_p(self) -> float:
        """Polymer component bulk viscosity :math:`\\zeta_p` [Pa s]

        :getter: Returns the polymer component bulk viscosity
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._zeta_p.value

    @zeta_p.setter
    def zeta_p(self, value: float) -> None:
        self._zeta_p.value = value

    @property
    def lambda_M(self) -> float:
        """Relaxation time of the fluid :math:`\\lambda_M` [s]

        :getter: Returns the relaxation time of the fluid
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._lambda_M.value

    @lambda_M.setter
    def lambda_M(self, value: float) -> None:
        self._lambda_M.value = value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def eta_c(self) -> complex:
        """Complex acoustic shear viscosity of the fluid :math:`\\eta_c` [Pa s]
        """
        return self._eta_c.value

    @property
    def zeta_c(self) -> complex:
        """Complex acoustic bulk viscosity of the fluid :math:`\\zeta_c` [Pa s]
        """
        return self._zeta_c.value

    @property
    def k_f(self) -> complex:
        """Returns the wave number in the fluid :math:`k_f` [1/m]
        """
        return self._k_f.value

    @property
    def k_v(self) -> complex:
        """Returns the viscous wave number in the fluid :math:`k_v` [1/m]
        """
        return self._k_v.value

    # -------------------------------------------------------------------------
    # Dependent Variables Methods
    # -------------------------------------------------------------------------

    def _compute_eta_c(self) -> complex:
        return self.eta_f + self.eta_p / (1 - 1j * self.omega * self.lambda_M)

    def _compute_zeta_c(self) -> complex:
        return self.zeta_f + self.zeta_p / (
            1 - 1j * self.omega *
            self.lambda_M
        )

    def _compute_k_f(self) -> complex:
        return (
            self.omega / self.c_f
            / sqrt(
                1 - 1j * self.omega / (self.rho_f * self.c_f ** 2)
                * (self.zeta_c + 4 * self.eta_c / 3),
            )
        )

    def _compute_k_v(self) -> complex:
        if self.eta_c != 0:
            return (1 + 1j) * sqrt(self.rho_f * self.omega / (2 * self.eta_c))
        else:
            return 0


if __name__ == '__main__':
    pass
