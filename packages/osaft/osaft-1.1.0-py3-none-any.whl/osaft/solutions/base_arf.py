from abc import ABC, abstractmethod


class BaseARF(ABC):
    """ Base class for the Acoustic Radiation Force that defines the common
    interface.
    """

    @abstractmethod
    def compute_arf(self) -> float:
        """ Returns the value for the ARF in Newton [N].
        This method must be implemented by every theory to have a common
        interface for other modules.
        """
        pass


if __name__ == '__main__':
    pass
