from abc import ABC, abstractmethod
from typing import Optional, Union

import numpy as np

from osaft.core.functions import exp, pi
from osaft.core.functions import spherical_2_cartesian_coordinates as s2c_coord
from osaft.core.variable import ActiveVariable, PassiveVariable
from osaft.plotting.datacontainers.base_velocity_datacontainer import (
    VelocityFieldData,
)
from osaft.solutions.base_scattering import BaseScattering


class ScatteringFieldData(VelocityFieldData, ABC):
    """Container for plotting data for the scattering field

    :param sol: solution
    :param r_min: start point for radial plotting range
    :param r_max: end point for tangential plotting range
    :param theta_min: start point for tangential plotting range
    :param theta_max: end point for tangential plotting range
    :param res: resolution, if tuple (radial resolution, tangential resolution)
    """

    def __init__(
        self,
        sol: BaseScattering,
        r_min: float,
        r_max: float,
        theta_min: float = 0,
        theta_max: float = pi,
        res: Union[int, tuple[int, int]] = 100,
    ) -> None:
        """Constructor method"""

        VelocityFieldData.__init__(
            self, sol, r_min, r_max, theta_min,
            theta_max, res,
        )

        # Velocities for the scattering field (complex valued)
        self._u = ActiveVariable(self._reset_complex_array, 'x coordinate')
        self._w = ActiveVariable(self._reset_complex_array, 'z coordinate')

        self._u.is_computed_by(self._sol, self._grid, self._mode)
        self._w.is_computed_by(self._sol, self._grid, self._mode)
    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def get_velocity_magnitude(
            self,
            instantaneous: bool = True,
            phase: float = 0,
            mode: Optional[int] = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the velocity magnitudes

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the magnitude of the velocity field at
        these points

        :param instantaneous: if `True` the instant magnitude is returned
        :param phase: phase angle
        :param mode: mode of oscillation, if `None` superposition
        """
        self._mode.value = mode
        if instantaneous:
            return self.x, self.z, self._velocity_norm_inst(phase)
        else:
            return self.x, self.z, self.u_norm

    def get_displacement_magnitude(
            self,
            instantaneous: bool = True,
            phase: float = 0,
            mode: Optional[int] = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the displacement magnitudes

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the magnitude of the displacement field at
        these points

        :param instantaneous: if `True` the instant magnitude is returned
        :param phase: phase angle
        :param mode: mode of oscillation, if `None` superposition
        """
        self._mode.value = mode
        if instantaneous:
            return self.x, self.z, self._disp_norm_inst(phase)
        else:
            return self.x, self.z, self.u_norm / self.sol.omega

    def get_velocity_vector(
            self,
            phase: float = 0,
            mode: Optional[int] = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Returns the velocity vectors

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the velocity field vectors at
        these points

        :param phase: phase angle
        :param mode: mode of oscillation, if `None` superposition
        """
        self._mode.value = mode
        if phase == 0:
            return self.x, self.z, self.u.real, self.w.real
        else:
            u = self.u * np.exp(- 1j * phase)
            w = self.w * np.exp(- 1j * phase)
            return self.x, self.w, u.real, w.real

    def get_displacement_vector(
            self,
            phase: float = 0,
            mode: Optional[int] = None,
    ) -> tuple[
        np.ndarray, np.ndarray,
        np.ndarray, np.ndarray,
    ]:
        """Returns the displacement vectors

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the displacement field vectors at
        these points

        :param phase: phase angle
        :param mode: mode of oscillation, if `None` superposition
        """
        self._mode.value = mode
        if phase == 0:
            u = 1j * self.u / self.sol.omega
            w = 1j * self.w / self.sol.omega
        else:
            u = self.u * np.exp(- 1j * phase) / self.sol.omega
            w = self.w * np.exp(- 1j * phase) / self.sol.omega
        return self.x, self.w, u.real, w.real

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------

    def _velocity_norm_inst(
            self,
            phase: float,
    ) -> np.ndarray:
        """Instantaneous velocity magnitude

        :param phase: phase angle
        """
        if phase == 0:
            return np.hypot(self.u.real, self.w.real)
        else:
            u = self.u * exp(-1j * phase)
            w = self.w * exp(-1j * phase)
            return np.hypot(u.real, w.real)

    def _disp_norm_inst(
        self,
        phase: float,
    ) -> np.ndarray:
        """Instantaneous displacement magnitude

        :param phase: phase angle
        """
        u = 1j * self.u * exp(-1j * phase) / self.sol.omega
        w = 1j * self.w * exp(-1j * phase) / self.sol.omega
        norm = np.hypot(u.real, w.real)
        return norm

    def _compute_data(self) -> None:
        """Compute the velocity data and store them in respective attributes

        Scattering velocity field is computed on the polar grid and transformed
        to Cartesian coordinates for plotting.
        """
        arr_r = self.grid.arr_r
        arr_theta = self.grid.arr_theta

        for index, theta in enumerate(arr_theta):

            # Indexing
            min_index = index * self.resolution
            max_index = min_index + self.resolution

            # Coordinates
            xs, zs = s2c_coord(self.grid.arr_r, theta)
            self._x.value[min_index:max_index] = xs
            self._z.value[min_index:max_index] = zs

            # Displacements Velocities
            u, w = self._compute_velocities(arr_r, theta)
            self._u.value[min_index:max_index] = u
            self._w.value[min_index:max_index] = w
            self._u_norm.value[min_index:max_index] = np.hypot(
                np.abs(u),
                np.abs(w),
            )

    @abstractmethod
    def _compute_velocities(
        self,
        arr_r: np.ndarray,
        theta: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute the velocity data and return it

        :param arr_r: array of r-coordinates
        :param theta: polar angle
        """
        pass  # pragma: no cover

# -----------------------------------------------------------------------------
# ParticleScatteringData
# -----------------------------------------------------------------------------


class ParticleScatteringData(ScatteringFieldData):
    """Container for plotting data for the displacement field in the particle

    :param sol: solution
    :param theta_min: start point for tangential plotting range
    :param theta_max: end point for tangential plotting range
    :param res: resolution, if tuple (radial resolution, tangential resolution)
    """

    def __init__(
        self,
        sol: BaseScattering,
        theta_min: float = 0,
        theta_max: float = pi,
        res: Union[int, tuple[int, int]] = 100,
    ) -> None:
        """Constructor method"""

        r_min = 1e-30
        r_max = sol.R_0
        super().__init__(
            sol, r_min, r_max, theta_min, theta_max, res,
        )

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------

    def _compute_velocities(
        self,
        arr_r: np.ndarray,
        theta: float,
    ):
        """Compute the velocity data and return it

        :param arr_r: array of r-coordinates
        :param theta: polar angle
        """
        u = self.sol.radial_particle_velocity(arr_r, theta, 0, self.mode)
        w = self.sol.tangential_particle_velocity(arr_r, theta, 0, self.mode)
        return u, w

# -----------------------------------------------------------------------------
# FluidScatteringData
# -----------------------------------------------------------------------------


class FluidScatteringData(ScatteringFieldData):
    """Container for plotting data for the scattering field in the fluid

    :param sol: solution
    :param r_max: end point for tangential plotting range
    :param theta_min: start point for tangential plotting range
    :param theta_max: end point for tangential plotting range
    :param res: resolution, if tuple (radial resolution, tangential resolution)
    """
    def __init__(
        self,
        sol: BaseScattering,
        r_max: float,
        theta_min: float = 0,
        theta_max: float = pi,
        scattering: bool = True,
        incident: bool = True,
        res: Union[int, tuple[int, int]] = 100,
    ) -> None:
        """Constructor method"""

        r_min = sol.R_0
        super().__init__(
            sol, r_min, r_max, theta_min, theta_max, res,
        )

        self._scattered = PassiveVariable(
            scattering, 'option: plot '
            'scattering field',
        )
        self._incident = PassiveVariable(
            incident, 'option: plot '
            'incident field',
        )

        # Set links
        self._u.is_computed_by(self._scattered, self._incident)
        self._w.is_computed_by(self._scattered, self._incident)
    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def get_velocity_magnitude(
            self,
            instantaneous: bool = True,
            phase: float = 0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the velocity magnitudes

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the magnitude of the velocity field at
        these points

        :param instantaneous: option if instantaneous or average magnitude
        :param phase: phase angle
        :param mode: mode of oscillation, if `None` superposition
        :param scattered: option if scattering field is plotted
        :param incident: option if incident field is plotted
        """
        self.scattered = scattered
        self.incident = incident
        return super().get_velocity_magnitude(instantaneous, phase, mode)

    def get_velocity_vector(
            self,
            phase: float = 0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
    ) -> tuple[
        np.ndarray, np.ndarray,
        np.ndarray, np.ndarray,
    ]:
        """Returns the velocity vectors

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the velocity field vectors at
        these points

        :param phase: phase angle
        :param mode: mode of oscillation, if `None` superposition
        :param scattered: option if scattering field is plotted
        :param incident: option if incident field is plotted
        """
        self.scattered = scattered
        self.incident = incident
        return super().get_velocity_vector(phase, mode)

    def get_displacement_vector(
            self,
            phase: float = 0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Returns the displacement vectors

        returns the coordinates of the points of the plotting grid `x`,
        `y` and the displacement field vectors at
        these points

        :param phase: phase angle
        :param mode: mode of oscillation, if `None` superposition
        :param scattered: option if scattering field is plotted
        :param incident: option if incident field is plotted
        """
        self.scattered = scattered
        self.incident = incident
        return super().get_displacement_vector(phase, mode)

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def scattered(self) -> bool:
        """Option if scattering field is plotted

        :getter: returns True (plot field) or False (do not plot field)
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._scattered.value

    @scattered.setter
    def scattered(self, value: bool) -> None:
        self._scattered.value = value

    @property
    def incident(self) -> bool:
        """Option if incident field is plotted

        :getter: returns True (plot field) or False (do not plot field)
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._incident.value

    @incident.setter
    def incident(self, value: bool) -> None:
        self._incident.value = value

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------

    def _compute_velocities(
            self,
            arr_r: np.ndarray,
            theta: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute the velocity data and return it

        :param arr_r: array of r-coordinates
        :param theta: polar angle
        """
        u = self.sol.radial_acoustic_fluid_velocity(
            arr_r, theta, 0,
            self.scattered,
            self.incident,
            self.mode,
        )
        w = self.sol.tangential_acoustic_fluid_velocity(
            arr_r, theta, 0,
            self.scattered,
            self.incident,
            self.mode,
        )
        return u, w


if __name__ == '__main__':
    pass
