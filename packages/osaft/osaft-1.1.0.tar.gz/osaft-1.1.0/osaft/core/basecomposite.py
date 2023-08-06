from numbers import Number
from typing import Union

from osaft import log
from osaft.core.frequency import Frequency
from osaft.core.geometries import Sphere


class BaseFrequencyComposite:
    """ Base class for all composite classes with
    :class:`~osaft.core.frequency.Frequency`

    :param frequency: excitation frequency in [Hz]

    This class has two purposes:

        #. Provides an `__init__` methods that handles the `frequency` argument
           correctly to make sure that all components and the composite have
           the same instance of :class:`~osaft.core.frequency.Frequency`.
        #. Provides wrappers for setters and getters of f and omega
    """

    def __init__(self, frequency: Union[int, float, Frequency]) -> None:
        """Constructor method
        """

        if isinstance(frequency, Number):
            log.debug(
                f'Passed frequency of type {type(frequency)}.'
                f'New Frequency object is created.',
            )
            self.frequency = Frequency(frequency)
        elif isinstance(frequency, Frequency):
            log.debug(
                f'Passed frequency of type {type(frequency)}.'
                f'No new Frequency object is created',
            )
            self.frequency = frequency
        else:
            raise TypeError(
                f'Expected type of frequency argument to be '
                f'int, float, or Frequency.'
                f'got {type(frequency)}.',
            )

        if type(self) is BaseFrequencyComposite:
            log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        """ Repr string for debugging

        """
        return f'BaseFrequencyComposite(f={self.f})'

    @classmethod
    def input_variables(cls) -> list[str]:
        """Returns all properties that are settable.

        Returns a list of the names of all properties that are settable,
        i.e. all properties that wrap a PassiveVariable.
        """
        list_input_vars = []

        for parent in cls.mro():
            for attr, val in vars(parent).items():
                if isinstance(val, property) and val.fset is not None:
                    list_input_vars.append(attr)
        return list_input_vars

    # -------------------------------------------------------------------------
    # Attribute Wrappers
    # -------------------------------------------------------------------------

    @property
    def f(self) -> float:
        """ wrapper for :attr:`osaft.core.frequency.Frequency.f`
        """
        return self.frequency.f

    @f.setter
    def f(self, value) -> None:
        self.frequency.f = value

    @property
    def omega(self) -> float:
        """ wrapper for :attr:`osaft.core.frequency.Frequency.omega`
        """
        return self.frequency.omega


class BaseSphereFrequencyComposite(BaseFrequencyComposite):
    """ Composite class with :class:`~osaft.core.frequency.Frequency` and
    :class:`~osaft.core.geometries.Sphere`

    This class has two purposes:

        #. Provides an `__init__` methods that handles the `frequency`
           argument and the `radius` argument correctly to make sure that all
           components and the composite have the same instance of
           :class:`~osaft.core.frequency.Frequency`
           and :class:`~osaft.core.geometries.Sphere`.
        #. Provides wrappers for setters and getters.

    :param frequency: excitation frequency in [Hz]
    :param radius: sphere radius in [m]
    """

    def __init__(
        self, frequency: Union[int, float, Frequency],
        radius: Union[int, float, Sphere],
    ) -> None:
        """Constructor method
        """

        super().__init__(frequency)

        if isinstance(radius, Number):
            log.debug(
                f'Passed frequency of type {type(radius)}.'
                f'New Frequency object is created.',
            )
            self.sphere = Sphere(radius)
        elif isinstance(radius, Sphere):
            log.debug(
                f'Passed sphere of type {type(radius)}.'
                f'No new Sphere object is created',
            )
            self.sphere = radius
        else:
            raise TypeError(
                f'Expected type of radius argument to be'
                f'int, float, or Sphere.'
                f'got {type(radius)}.',
            )

        if type(self) is BaseSphereFrequencyComposite:
            log.debug(f'Creating {self}')

    def __repr__(self) -> str:
        return (
            f'BaseSphereFrequencyComposite(f={self.f}, '
            f'r={self.R_0})'
        )

    # -------------------------------------------------------------------------
    # Attribute Wrappers
    # -------------------------------------------------------------------------

    @property
    def R_0(self) -> float:
        """ Wrapper for :attr:`osaft.core.geometries.Sphere.R_0`
        """
        return self.sphere.R_0

    @R_0.setter
    def R_0(self, value) -> None:
        self.sphere.R_0 = value

    @property
    def area(self) -> float:
        """ Wrapper for :attr:`osaft.core.geometries.Sphere.area`
        """
        return self.sphere.area

    @property
    def volume(self) -> float:
        """ Wrapper for :attr:`osaft.core.geometries.Sphere.volume`
        """
        return self.sphere.volume


if __name__ == '__main__':
    pass
