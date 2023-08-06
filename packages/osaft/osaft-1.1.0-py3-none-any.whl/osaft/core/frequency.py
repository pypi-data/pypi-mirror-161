from osaft import log
from osaft.core.functions import pi
from osaft.core.variable import ActiveVariable, PassiveVariable


class Frequency:
    """Frequency class

    :param frequency: frequency [Hz]
    """

    # -------------------------------------------------------------------------
    # Magic Methods
    # -------------------------------------------------------------------------

    def __init__(self, frequency: float) -> None:
        """Constructor method
        """

        # Independent variables
        self._f = PassiveVariable(frequency, 'frequency f')

        # Initialize dependent variables
        self._omega = ActiveVariable(
            self._compute_omega,
            'angular frequency omega',
        )

        # Dependencies
        self._omega.is_computed_by(self._f)

        log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return f'Frequency(f={self.f})'

    # -------------------------------------------------------------------------
    # Setters and Getters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def f(self) -> float:
        """Excitation frequency [Hz].

        :getter: returns the value for the frequency
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._f.value

    @f.setter
    def f(self, value: float) -> None:
        self._f.value = value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def omega(self) -> float:
        """Returns the angular frequency :math:`\\omega` [rad/s].
        """
        return self._omega.value

    # -------------------------------------------------------------------------
    # Methods Dependent Variables Methods
    # -------------------------------------------------------------------------

    def _compute_omega(self) -> float:
        return self.f * 2 * pi


if __name__ == '__main__':
    pass
