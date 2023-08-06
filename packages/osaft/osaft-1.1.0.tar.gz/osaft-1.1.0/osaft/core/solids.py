from typing import Union

from osaft import log
from osaft.core.basecomposite import BaseFrequencyComposite
from osaft.core.frequency import Frequency
from osaft.core.functions import sqrt
from osaft.core.variable import ActiveVariable, PassiveVariable


class RigidSolid(BaseFrequencyComposite):
    """RigidSolid class

    :param frequency: excitation frequency in [Hz]
    :param rho: density in [kg/m^3]
    """

    def __init__(
        self, frequency: Union[int, float, Frequency],
        rho: float,
    ) -> None:
        """Constructor method
        """

        # Calling parent class
        super().__init__(frequency)

        # Independent variables
        self._rho_s = PassiveVariable(rho, 'density rho')

        if type(self) is RigidSolid:
            log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return f'RigidSolid(f={self.f}, rho={self.rho_s})'

    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def rho_s(self) -> float:
        """Density of the solid :math:`\\rho_{s}`.

        :getter: returns the value for the density
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._rho_s.value

    @rho_s.setter
    def rho_s(self, value: float) -> None:
        self._rho_s.value = value


class ElasticSolid(RigidSolid):
    """ElasticSolid class

    :param frequency: excitation frequency in [Hz]
    :param E: Young's modulus in [Pa]
    :param nu: Poisson's ratio in [-]
    :param rho: density in [km m^-3]
    """

    def __init__(self, frequency, E, nu, rho) -> None:
        """Constructor method
        """

        super().__init__(frequency, rho)

        # Independent variables
        self._E_s = PassiveVariable(E, "Young's modulus E")
        self._nu_s = PassiveVariable(nu, "Poisson's ratio nu")

        # Dependent variables
        self._c_l = ActiveVariable(self._compute_c_l, 'primary wave speed c_l')
        self._k_l = ActiveVariable(
            self._compute_k_l,
            'wavenumber of primary wave k_l',
        )

        self._c_t = ActiveVariable(
            self._compute_c_t,
            'secondary wave speed c_t',
        )
        self._k_t = ActiveVariable(
            self._compute_k_t,
            'wavenumber of secondary wave k_t',
        )

        self._G = ActiveVariable(self._compute_G, 'shear modulus G')
        self._lambda = ActiveVariable(
            self._compute_lambda,
            'second Lame parameter lambda',
        )

        self._B_s = ActiveVariable(self._compute_B_s, 'bulk modulus B_s')
        self._kappa_s = ActiveVariable(
            self._compute_kappa_s,
            'compressibility kappa_s',
        )

        # Dependencies
        self._G.is_computed_by(self._E_s, self._nu_s)
        self._lambda.is_computed_by(self._E_s, self._nu_s)

        self._c_l.is_computed_by(self._E_s, self._nu_s, self._rho_s)
        self._k_l.is_computed_by(self._c_l, self.frequency._omega)

        self._c_t.is_computed_by(self._E_s, self._nu_s, self._rho_s)
        self._k_t.is_computed_by(self._c_t, self.frequency._omega)

        self._B_s.is_computed_by(self._E_s, self._nu_s)
        self._kappa_s.is_computed_by(self._B_s)

        # no if clause needed because last in inheritance diagram
        log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return (
            f'ElasticSolid(f={self.f}, rho={self.rho_s}, '
            f'E={self.E_s}, nu={self.nu_s})'
        )

    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def E_s(self) -> float:
        """Young's modulus of the solid :math:`E_{s}` [Pa].

        :getter: returns the value for the Young's modulus
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._E_s.value

    @E_s.setter
    def E_s(self, value: float) -> None:
        self._E_s.value = value

    @property
    def nu_s(self) -> float:
        """Poisson's ratio of the solid :math:`\\nu_{s}`.

        :getter: returns the value for the Poisson's ratio
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._nu_s.value

    @nu_s.setter
    def nu_s(self, value: float) -> None:
        self._nu_s.value = value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def G(self) -> float:
        """Returns the shear modulus :math:`G`.
        """
        return self._G.value

    @property
    def B_s(self) -> float:
        """Returns the bulk modulus of the solid :math:`B_{s}` [Pa]
        """
        return self._B_s.value

    @property
    def kappa_s(self) -> float:
        """Returns the compressibility of the solid :math:`\\kappa_{s}` [1/Pa]
        """
        return self._kappa_s.value

    @property
    def c_l(self) -> float:
        """Returns the longitudinal wave speed in the solid :math:`c_l` [m/s]
        """
        return self._c_l.value

    @property
    def c_t(self) -> float:
        """Return the transverse wave speed in the solid :math:`c_t` [m/s]
        """
        return self._c_t.value

    @property
    def k_l(self) -> float:
        """Returns the longitudinal wave number in the solid :math:`k_l` [1/m]
        """
        return self._k_l.value

    @property
    def k_t(self) -> float:
        """Returns the transverse wave number in the solid :math:`k_t` [1/m]
        """
        return self._k_t.value

    @property
    def lame_1(self) -> float:
        """Returns the first Lamé parameter :math:`\\lambda` [Pa]
        """
        return self._lambda.value

    @property
    def lame_2(self) -> float:
        """Returns the second Lamé parameter :math:`\\mu`"""
        return self.G

    # -------------------------------------------------------------------------
    # Dependent Variables Methods
    # -------------------------------------------------------------------------

    def _compute_G(self) -> float:
        return self.G_from_E_nu(self.E_s, self.nu_s)

    def _compute_lambda(self) -> float:
        return self.lambda_from_E_nu(self.E_s, self.nu_s)

    def _compute_B_s(self) -> float:
        return self.E_s / (1 - 2 * self.nu_s) / 3

    def _compute_kappa_s(self) -> float:
        return 1 / self.B_s

    def _compute_c_l(self) -> float:
        return self.c1_from_E_nu(self.E_s, self.nu_s, self.rho_s)

    def _compute_c_t(self) -> float:
        return self.c2_from_E_nu(self.E_s, self.nu_s, self.rho_s)

    def _compute_k_l(self) -> float:
        return self.omega / self.c_l

    def _compute_k_t(self) -> float:
        return self.omega / self.c_t

    # -------------------------------------------------------------------------
    # Conversion Methods
    # -------------------------------------------------------------------------

    @staticmethod
    def E_from_wave_speed(
            c_1: float, c_2: float, rho: float,
    ) -> float:
        """Computes the Young's modulus :math:`E` from the primary and the
        secondary wave speed :math:`c_1`, :math:`c_2` and the density
        :math:`\\rho`.

        :param c_1: primary wave speed [m/s]
        :param c_2: secondary wave speed [m/s]
        :param rho: density [kg/m^3]
        """
        return (
            rho * c_2 ** 2 * (3 * c_1 ** 2 - 4 * c_2 ** 2)
            / (c_1 ** 2 - c_2 ** 2)
        )

    @staticmethod
    def nu_from_wave_speed(
            c_1: float, c_2: float,
    ) -> float:
        """Computes the Poisson's ratio :math:`\\nu` from the primary and the
        secondary wave speed :math:`c_1`, :math:`c_2`, and the density
        :math:`\\rho`.

        :param c_1: primary wave speed [m/s]
        :param c_2: secondary wave speed [m/s]
        """
        return (1 - 2 * (c_2 / c_1) ** 2) / (2 - 2 * (c_2 / c_1) ** 2)

    @staticmethod
    def lambda_from_wave_speed(
            c_1: float, c_2: float, rho: float,
    ) -> float:
        """Computes the Lamé first parameter :math:`\\lambda` from the
        primary and the secondary wave speed :math:`c_1`, :math:`c_2` and the
        density :math:`\\rho`.

        :param c_1: primary wave speed [m/s]
        :param c_2: secondary wave speed [m/s]
        :param rho: density [kg/m^3]
        """
        G = c_2 ** 2 * rho
        return c_1 ** 2 * rho - 2 * G

    @staticmethod
    def G_from_wave_speed(
            c_2: float, rho: float,
    ) -> float:
        """Computes the second Lamé parameter :math:`G` from the secondary
        wave speed :math:`c_2` and the density :math:`\\rho`.

        :param c_2: secondary wave speed [m/s]
        :param rho: density [kg/m^3]
        """
        return c_2 ** 2 * rho

    @staticmethod
    def c1_from_E_nu(
            E: float, nu: float, rho: float,
    ) -> float:
        """Computes the primary wave speed :math:`c_1` from the Young's modulus
        :math:`E` and the Poisson's ratio :math:`\\nu`, and the density
        :math:`\\rho`.

        :param E: Young;s modulus [Pa]
        :param nu: Poisson's ratio [-]
        :param rho: density [kg/m^3]
        """
        return sqrt(E * (1 - nu) / (rho * (1 + nu) * (1 - 2 * nu)))

    @staticmethod
    def c2_from_E_nu(
            E: float, nu: float, rho: float,
    ) -> float:
        """Computes the secondary wave speed :math:`c_2` from the Young's
        modulus :math:`E` and the Poisson's ratio :math:`\\nu`, and the density
        :math:`\\rho`.

        :param E: Young;s modulus [Pa]
        :param nu: Poisson's ratio [-]
        :param rho: density [kg/m^3]
        """
        return sqrt(E / (2 * (1 + nu) * rho))

    @staticmethod
    def c1_from_Lame(
            lam: float, G: float, rho: float,
    ) -> float:
        """Computes the primary wave speed :math:`c_1` from the Lamé parameters
        :math:`\\lambda`, :math:`G`, and the density
        :math:`\\rho`.

        :param lam: first Lamé parameter [Pa]
        :param G: second Lamé parameter [Pa]
        :param rho: density [kg/m^3]
        """
        return sqrt((lam + 2 * G) / rho)

    @staticmethod
    def c2_from_Lame(
            G: float, rho: float,
    ) -> float:
        """Computes the secondary wave speed :math:`c_2` from the Lamé
        parameters :math:`\\lambda`, :math:`G`, and the density :math:`\\rho`.

        :param G: second Lamé parameter [Pa]
        :param rho: density [kg/m^3]
        """
        return sqrt(G / rho)

    @staticmethod
    def E_from_Lame(
            lam: float, G: float,
    ) -> float:
        """Computes the Young's modulus :math:`E` from the Lamé parameters
        :math:`\\lambda`, :math:`G`

        :param lam: first Lamé parameter [Pa]
        :param G: second Lamé parameter [Pa]
        """
        return G * (3 * lam + 2 * G) / (lam + G)

    @staticmethod
    def nu_from_Lame(
            lam: float, G: float,
    ) -> float:
        """Computes the the Poisson's ratio :math:`\\nu` from the Lamé
        parameters :math:`\\lambda`, :math:`G`.

        :param lam: first Lamé parameter [Pa]
        :param G: second Lamé parameter [Pa]
        """
        return lam / (2 * (lam + G))

    @classmethod
    def lambda_from_E_nu(cls, E: float, nu: float) -> float:
        """Computes the first Lamé parameters :math:`\\lambda` from the Young's
        modulus :math:`E` and the Poisson's ratio :math:`\\nu`.

        :param E: Young;s modulus [Pa]
        :param nu: Poisson's ratio [-]
        """
        G = cls.G_from_E_nu(E, nu)
        return 2 * G * nu / (1 - 2 * nu)

    @staticmethod
    def G_from_E_nu(
            E: float, nu: float,
    ) -> float:
        """Computes the second Lamé parameters :math:`G` from the Young's
        modulus :math:`E` and the Poisson's ratio :math:`\\nu`.

        :param E: Young;s modulus [Pa]
        :param nu: Poisson's ratio [-]
        """
        return E / (2 * (1 + nu))


if __name__ == '__main__':
    pass
