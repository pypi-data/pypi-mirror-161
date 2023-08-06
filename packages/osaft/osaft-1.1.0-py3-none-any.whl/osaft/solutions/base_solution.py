from __future__ import annotations

import copy
from abc import ABC, abstractmethod

from osaft.core.backgroundfields import WaveType, WrongWaveTypeError


class BaseSolution(ABC):
    """ Base class for all solutions

    :param name: name of the solution
    """

    # supported wave types of the solution
    supported_wavetypes = []

    def __init__(self, name: str):
        self.name = name

    def copy(self) -> BaseSolution:
        """Returns a copy of the object

        :rtype: BaseSolution
        """
        return copy.copy(self)

    @property
    @abstractmethod
    def wave_type(self) -> WaveType:
        """returns the wave type of the solution"""
        pass

    def check_wave_type(self) -> None:
        """Checks if :attr:`wave_type` is in :attr:`supported_wavetypes`

        :raises WrongWaveTypeError: If :attr:`wave_type` is not supported
        """
        if self.wave_type not in self.supported_wavetypes:
            raise WrongWaveTypeError(
                'Solution does not exist for '
                f'wave_type = {self.wave_type} \n',
                f'supported: {self.supported_wavetypes}',
            )

    def __copy__(self) -> BaseSolution:
        """ Overriding the default copy dunder

        The reason for that is, that we need to create a new object by calling
        the __init__(self, ...) method because otherwise the links to the
        various PassiveVariable and ActiveVariable would be wrong.

        This is circumvent by creating a dictionary with all the possible
        PassiveVariable objects and then calling the __init__(...) method.

        :rtype: BaseSolution
        """
        passive_variables = self.input_variables()
        init_dict = {}
        for name in passive_variables:
            init_dict[name] = getattr(self, name)

        result = self.__class__(**init_dict)
        result.name = f'copy_{self.name}'

        return result


if __name__ == '__main__':
    pass
