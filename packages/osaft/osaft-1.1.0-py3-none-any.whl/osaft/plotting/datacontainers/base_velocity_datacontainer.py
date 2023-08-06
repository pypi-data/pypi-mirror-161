from abc import ABC, abstractmethod
from typing import Union

import numpy as np

from osaft.core.functions import pi
from osaft.core.variable import ActiveVariable, PassiveVariable
from osaft.plotting.grid import Grid
from osaft.solutions.base_scattering import BaseScattering
from osaft.solutions.base_streaming import BaseStreaming


class VelocityFieldData(ABC):
    """Container for plotting data for scattering and streaming plots

    :param sol: solution
    :param r_min: start point for radial plotting range in [m]
    :param r_max: end point for tangential plotting range  in [m]
    :param theta_min: start point for tangential plotting range in [rad]
    :param theta_max: end point for tangential plotting range in [rad]
    :param res: resolution, if tuple (radial resolution, tangential resolution)
    """

    def __init__(
            self,
            sol: Union[BaseScattering, BaseStreaming],
            r_min: float,
            r_max: float,
            theta_min: float = 0,
            theta_max: float = pi,
            res: Union[int, tuple[int, int]] = 100,
    ) -> None:
        """Constructor method"""

        # Parameters for the coordinate grid
        self._r_min = PassiveVariable(r_min, 'r min')
        self._r_max = PassiveVariable(r_max, 'r max')
        self._theta_min = PassiveVariable(theta_min, 'theta min')
        self._theta_max = PassiveVariable(theta_max, 'r min')
        self._resolution = PassiveVariable(res, 'plotting resolution')

        # Solution to be plotted
        self._sol = PassiveVariable(sol, 'solution for plotting')
        self._mode = PassiveVariable(None, 'mode')

        # Dependent Variables: Data containers
        self._x = ActiveVariable(self._reset_real_array, 'x coordinate')
        self._z = ActiveVariable(self._reset_real_array, 'z coordinate')
        self._u = ActiveVariable(
            self._reset_complex_array, 'velocity/displacement '
            'in x-direction',
        )
        self._w = ActiveVariable(
            self._reset_complex_array, 'velocity/displacement '
            'in y-direction',
        )
        self._u_norm = ActiveVariable(
            self._reset_real_array, 'norm of the '
            'velocity / '
            'displacement',
        )
        # Dependent Variables: Coordinate grid
        self._grid = ActiveVariable(self._get_grid)

        # Setting links
        self._grid.is_computed_by(
            self._r_min, self._r_max, self._theta_min,
            self._theta_max, self._resolution,
        )
        self._x.is_computed_by(self._grid)
        self._w.is_computed_by(self._grid)
        self._u.is_computed_by(self._sol, self._grid, self._mode)
        self._w.is_computed_by(self._sol, self._grid, self._mode)
        self._u_norm.is_computed_by(self._sol, self._grid, self._mode)

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def get_velocity_magnitude(
        self,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the velocity magnitudes

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the magnitude of the velocity field at
        these points
        """
        return self.x, self.z, self.u_norm  # pragma: no cover

    def get_velocity_vector(self) -> tuple[
        np.ndarray, np.ndarray,
        np.ndarray, np.ndarray,
    ]:
        """Returns the velocity vectors

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the velocity field vectors at
        these points
        """
        return self.x, self.z, self.u, self.w  # pragma: no cover

    # -------------------------------------------------------------------------
    # Getters and Setters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def sol(self) -> Union[BaseScattering, BaseStreaming]:
        """Solution for plotting

        :getter: returns the end point for radial plotting range
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._sol.value

    @sol.setter
    def sol(self, value: Union[BaseScattering, BaseStreaming]) -> None:
        self._sol.value = value

    @property
    def r_min(self) -> float:
        """Endpoint for radial plotting range [m]

        :getter: returns the end point for radial plotting range
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._r_min.value

    @r_min.setter
    def r_min(self, value: float) -> None:
        self._r_min.value = value

    @property
    def r_max(self) -> float:
        """Start point for radial plotting range [m]

        :getter: returns the start point for radial plotting range
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._r_max.value

    @r_max.setter
    def r_max(self, value: float) -> None:
        self._r_max.value = value

    @property
    def theta_min(self) -> float:
        """Start point for tangential plotting range [rad]

        :getter: returns the start point for tangential plotting range
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._theta_min.value

    @theta_min.setter
    def theta_min(self, value: float) -> None:
        self._theta_min.value = value

    @property
    def theta_max(self) -> float:
        """Endpoint for tangential plotting range [rad]

        :getter: returns the end point for tangential plotting range
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._theta_max.value

    @theta_max.setter
    def theta_max(self, value: float) -> None:
        self._theta_max.value = value

    @property
    def resolution(self) -> Union[int, tuple[int, int]]:
        """Resolution for scattering / streaming plots

        `resolution` can be an `int` when the resolution in radial and
        tangential direction is the same, or a `tuple` of two `int`
        for independent resolutions (radial resolution, tangential_resolution)
        :getter: returns plotting resolution
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._resolution.value

    @resolution.setter
    def resolution(self, value: Union[int, tuple[int, int]]) -> None:
        self._resolution.value = value

    @property
    def mode(self) -> int:
        """Mode that is plotted. If `None` all modes up to `sol.N_max`
        are superimposed.
        :getter: returns the mode
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._mode.value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def grid(self) -> Grid:
        """Plotting grid
        """
        return self._grid.value

    @property
    def x(self) -> np.ndarray:
        """x-coordinates of the plotting grid in [m]
        """
        if np.all(self._x.value == 0):
            self._compute_data()
        return self._x.value

    @property
    def z(self) -> np.ndarray:
        """z-coordinates of the plotting grid in [m]
        """
        if np.all(self._z.value == 0):
            self._compute_data()  # pragma: no cover
        return self._z.value

    @property
    def u(self) -> np.ndarray:
        """Velocity / displacement in x-direction in [m/s]
        """
        if np.all(self._u.value == 0):
            self._compute_data()
        return self._u.value

    @property
    def w(self) -> np.ndarray:
        """Velocity / displacement in z-direction in [m/s]
        """
        if np.all(self._w.value == 0):
            self._compute_data()  # pragma: no cover
        return self._w.value

    @property
    def u_norm(self) -> np.ndarray:
        """Norm of the velocity / displacement in z-direction in [m/s]

        norm = abs(u) ** 2 + abs(w) ** 2
        """
        if np.all(self._u_norm.value == 0):
            self._compute_data()
        return self._u_norm.value

    # -------------------------------------------------------------------------
    # Methods for dependent variables
    # -------------------------------------------------------------------------

    def _reset_real_array(self):
        """Resets real arrays for coordinates and norm"""
        return np.zeros(
            self.grid.r_res * self.grid.theta_res,
            dtype=np.float64,
        )

    def _reset_complex_array(self):
        """Resets complex arrays for complex velocities and norm"""
        return np.zeros(
            self.grid.r_res * self.grid.theta_res,
            dtype=np.complex128,
        )

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------

    def _get_grid(self) -> Grid:
        """Returns a new coordinate grid"""
        return Grid(
            self.r_min, self.r_max,
            self.theta_min, self.theta_max,
            self.resolution,
        )

    @abstractmethod
    def _compute_data(
            self,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute the velocity data and store it in the respective attributes
        """
        pass  # pragma: no cover


if __name__ == '__main__':
    pass
