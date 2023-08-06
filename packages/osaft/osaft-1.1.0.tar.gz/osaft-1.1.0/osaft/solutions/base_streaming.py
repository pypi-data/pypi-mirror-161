from abc import ABC, abstractmethod


class BaseStreaming(ABC):
    """ Base class for the Streaming Field that defines the common
    interface.

    This base class is used for axisymmetrical models.
    """

    @abstractmethod
    def radial_Euler_streaming(
        self, r: float, theta: float, t: float,
    ) -> float:
        """ Returns the value for the radial Euler streaming velocity in [m/s].

        This method must be implemented by every theory to have a common
        interface for other modules.

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        """
        pass

    @abstractmethod
    def tangential_Euler_streaming(
        self, r: float, theta: float, t: float,
    ) -> float:
        """ Returns the value for the tangential Euler streaming velocity in
        [m/s].

        This method must be implemented by every theory to have a common
        interface for other modules.

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        """
        pass

    @abstractmethod
    def radial_Lagrange_streaming(
        self, r: float, theta: float, t: float,
    ) -> float:
        """ Returns the value for the radial Lagrange streaming velocity in
        [m/s].

        This method must be implemented by every theory to have a common
        interface for other modules.

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        """
        pass

    @abstractmethod
    def tangential_Lagrange_streaming(
        self, r: float, theta: float,
        t: float,
    ) -> float:
        """ Returns the value for the tangential Lagrange streaming velocity
        in [m/s].

        This method must be implemented by every theory to have a common
        interface for other modules.

        :param r: radial coordinate [m]
        :param theta: tangential coordinate [rad]
        :param t: time [s]
        """
        pass


if __name__ == '__main__':
    pass
