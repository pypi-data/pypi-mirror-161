from osaft import log
from osaft.core.functions import pi
from osaft.core.variable import ActiveVariable, PassiveVariable


class Sphere:
    """Sphere class

    :param radius: radius in [m]
    """

    def __init__(self, radius: float) -> None:
        """Constructor method
        """

        # Independent variables
        self._R_0 = PassiveVariable(radius, 'radius R_0')

        # Dependent variables
        self._A = ActiveVariable(
            self._compute_surface_area,
            'surface area A',
        )
        self._V = ActiveVariable(
            self._compute_volume,
            'volume V',
        )

        # Dependencies
        self._A.is_computed_by(self._R_0)
        self._V.is_computed_by(self._R_0)

        log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return f'Sphere(R={self.R_0})'

    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def R_0(self) -> float:
        """Radius of the sphere [m]

        :getter: returns the value for the radius
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._R_0.value

    @R_0.setter
    def R_0(self, value: float) -> None:
        self._R_0.value = value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def area(self) -> float:
        """Returns the surface area of the sphere [m^2]
        """
        return self._A.value

    @property
    def volume(self) -> float:
        """Returns the volume of the sphere [m^3]
        """
        return self._V.value

    # -------------------------------------------------------------------------
    # Methods for Dependent Variables Methods
    # -------------------------------------------------------------------------

    def _compute_surface_area(self) -> float:
        return 4 * pi * self.R_0 ** 2

    def _compute_volume(self) -> float:
        return 4 / 3 * pi * self.R_0 ** 3


if __name__ == '__main__':
    pass
