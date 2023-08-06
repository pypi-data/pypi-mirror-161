from collections.abc import Sequence
from dataclasses import dataclass
from typing import Union

import numpy as np

from osaft import log
from osaft.core.functions import exp, pi
from osaft.core.functions import spherical_2_cartesian_coordinates as s2c_coord
from osaft.core.functions import spherical_2_cartesian_vector as s2c_vector
from osaft.core.variable import ActiveVariable, PassiveVariable
from osaft.solutions.base_scattering import BaseScattering

# -----------------------------------------------------------------------------
# ParticleWireFrameData
# -----------------------------------------------------------------------------


@dataclass
class DeformedLine:
    """Class for storing and retrieving the reference configuration and the
    deformed configuration of a deformed line

    :param x: x-coordinate of the reference configuration
    :param y: y-coordinate of the reference configuration
    :param u: displacement in x-direction
    :param y: displacement in y-direction
    """
    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
    ) -> None:
        """Constructor method"""
        self.x = x
        self.y = y
        self.u = u
        self.v = v

    def get_deformed(self, phase) -> tuple[np.ndarray, np.ndarray]:
        """Returns the deformed line"""
        x_deformed = (
            self.x
            + (self.u * exp(1j * phase)).real
        )
        y_deformed = (
            self.y
            + (self.v * exp(1j * phase)).real
        )
        return x_deformed, y_deformed

    def get_reference(self) -> tuple[np.ndarray, np.ndarray]:
        return self.x, self.y


class ParticleWireframeData:
    """Data container for wireframe plot of the particle

    :param sol: solution to be plotted
    :param nbr_r_levels: number of circles shown in the wireframe
    :param nbr_theta_levels: number of radii shown in the wireframe
    :param resolution: resolution, if tuple `(radial res, tangential res)`
    :param scale_factor: ratio between shown displacement and radius
    :param symmetric: if `True` plot is expected to be symmetric.
    """
    def __init__(
        self,
        sol: BaseScattering,
        nbr_r_levels: int,
        nbr_theta_levels: int,
        resolution: Union[int, tuple[int, int]] = (100, 100),
        scale_factor: float = 0.1,
        symmetric: bool = True,
    ) -> None:
        """Constructor method
        """
        # Solution
        self._sol = PassiveVariable(sol, 'Solution for plotting')
        self._mode = PassiveVariable(None, 'mode')

        # Resolution
        unpacked_resolution = self._unpack_resolution(resolution)
        self._resolution = PassiveVariable(unpacked_resolution)

        # Scaling factor
        self._rel_scale_factor = PassiveVariable(
            scale_factor,
            'Relative scale factor',
        )
        self._scale_factor = ActiveVariable(
            self._compute_scale_factor, 'Absolute scale factor',
        )
        self._scale_factor.is_computed_by(
            self._sol, self._rel_scale_factor,
            self._mode,
        )

        # Symmetry
        self._symmetric = PassiveVariable(symmetric, 'symmetric')

        # Coordinate Grid
        self._arr_r = ActiveVariable(
            self._compute_arr_r,
            'Coordinate grid in radial direction',
        )
        self._arr_theta = ActiveVariable(
            self._compute_arr_theta,
            'Coordinate grid in radial direction',
        )
        self._arr_r.is_computed_by(self._resolution, self._sol)
        self._arr_theta.is_computed_by(
            self._resolution, self._symmetric,
            self._sol,
        )

        # Number of Levels
        self._nbr_r_lvl = PassiveVariable(
            nbr_r_levels,
            'Number of radial wireframe '
            'levels',
        )
        even_nbr_theta_levels = self._test_nbr_t_lvl(nbr_theta_levels)
        self._nbr_t_lvl = PassiveVariable(
            even_nbr_theta_levels,
            'Number of tangential wireframe '
            'levels',
        )

        # Levels
        self._r_levels = ActiveVariable(
            self._compute_r_levels,
            'Radii of wireframe circles',
        )
        self._theta_levels = ActiveVariable(
            self._compute_theta_levels,
            'Angles of wireframe radii',
        )
        self._r_levels.is_computed_by(self._sol, self._nbr_r_lvl)
        self._theta_levels.is_computed_by(
            self._sol, self._nbr_t_lvl,
            self._symmetric,
        )

        # Solution containers
        self._deformed_radii = ActiveVariable(
            self._reset_list,
            'List of deformed radii',
        )
        self._deformed_circles = ActiveVariable(
            self._reset_list,
            'List of deformed circles',
        )
        self._deformed_radii.is_computed_by(
            self._sol, self._scale_factor,
            self._arr_r, self._theta_levels,
        )
        self._deformed_circles.is_computed_by(
            self._sol, self._scale_factor,
            self._arr_theta, self._r_levels,
        )

    # -------------------------------------------------------------------------
    # __init__ helper methods
    # -------------------------------------------------------------------------

    def _test_nbr_t_lvl(self, nbr_t_lvl: int) -> int:
        nbr_t_lvl = int(nbr_t_lvl)
        if nbr_t_lvl % 2 and self.symmetric:
            log.warning(
                'nbr_theta_levels has to be even. nbr_theta_levels is set '
                f'to {nbr_t_lvl} + 1 = {nbr_t_lvl + 1} ',
            )
            return nbr_t_lvl + 1
        else:
            return int(nbr_t_lvl)

    @staticmethod
    def _unpack_resolution(
        res: Union[int, tuple[int, int]],
    ) -> tuple[int, int]:
        """ Unpacks resolution tuple if needed

        if `res` is an `int` a tuple `(res, res)` is
        returned. If `res` is a tuple with two values, `res` is passed through.
        :param res: res of the grid
        """
        if isinstance(res, Sequence):
            if len(res) == 1:
                return res[0], res[0]
            elif len(res) == 2:
                return res
            else:
                raise ValueError(
                    'Resolution needs to be either one value for both '
                    'radial and tangential direction',
                )
        else:
            return res, res

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def get_displacements(self) -> tuple[list, list]:
        """Returns the wireframe

        The wireframe is return as a tuple of two list.
        `(deformed_radii, deformed_circle)`. Each element of the list is of
        type :class:`osaft.plotting.wireframe_datacontainer.DeformedLine`.
        """
        return self.deformed_radii, self.deformed_circles

    # -------------------------------------------------------------------------
    # Getters and Setters for Independent Variables
    # -------------------------------------------------------------------------

    @property
    def sol(self) -> BaseScattering:
        """Solution for plotting

        :getter: returns the solution for plotting
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._sol.value

    @sol.setter
    def sol(self, value: BaseScattering) -> None:
        self._sol.value = value

    @property
    def resolution(self) -> tuple[int, int]:
        """Plotting resolution

        The plotting resolution of the form
        `(radial_resolution, tangential_resolution)`

        :getter: returns the plotting resolution
        :setter: unpacks resolution and automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._resolution.value

    @resolution.setter
    def resolution(self, value: Union[int, tuple[int, int]]) -> None:
        unpacked_value = self._unpack_resolution(value)
        self._resolution.value = unpacked_value

    @property
    def rel_scale_factor(self) -> float:
        """Relative scale factor

        Ratio between max shown displacement and particle radius.
        :getter: returns the relative scale factor
        :setter: unpacks resolution and automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._rel_scale_factor.value

    @rel_scale_factor.setter
    def rel_scale_factor(self, value: float) -> None:
        self._rel_scale_factor.value = value

    @property
    def mode(self) -> int:
        """Mode that is plotted. If `None` all modes up to `sol.N_max`
        are superimposed.

        :getter: returns the mode
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._mode.value

    @mode.setter
    def mode(self, value: int) -> None:
        self._mode.value = value

    @property
    def nbr_r_levels(self) -> int:
        """Number of radial levels in the wireframe plot

        :getter: returns the number of radial plotting levels
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._nbr_r_lvl.value

    @nbr_r_levels.setter
    def nbr_r_levels(self, value: int) -> None:
        self._nbr_r_lvl.value = value

    @property
    def nbr_theta_levels(self) -> int:
        """Number of tangential levels in the wireframe plot

        :getter: returns the number of tangential plotting levels
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._nbr_t_lvl.value

    @nbr_theta_levels.setter
    def nbr_theta_levels(self, value: int) -> None:
        even_number_theta_levels = self._test_nbr_t_lvl(value)
        self._nbr_t_lvl.value = even_number_theta_levels

    @property
    def symmetric(self):
        """Option if the plot is symmetric

        If `True` only have of the data is stored.

        :getter: returns the symmetry bool
        :setter: automatically invokes
            :meth:`osaft.core.variable.BaseVariable.notify`
        """
        return self._symmetric.value

    @symmetric.setter
    def symmetric(self, value: bool):
        self._symmetric.value = value

    # -------------------------------------------------------------------------
    # Getters for Dependent Variables
    # -------------------------------------------------------------------------

    @property
    def scale_factor(self) -> float:
        """Returns the scale factor for the deformation of the wire frame
        plot"""
        return self._scale_factor.value

    @property
    def r_levels(self) -> np.ndarray:
        """Radial levels of the wireframe plot"""
        return self._r_levels.value

    @property
    def theta_levels(self) -> np.ndarray:
        """Radial levels of the wireframe plot"""
        return self._theta_levels.value

    @property
    def deformed_radii(self) -> list[DeformedLine]:
        """List of deformed radii of the wireframe plot
        """
        if not self._deformed_radii.value:
            self._compute_data()
        return self._deformed_radii.value

    @property
    def deformed_circles(self) -> list[DeformedLine]:
        """List of deformed circles of the wireframe plot
        """
        if not self._deformed_circles.value:
            self._compute_data()
        return self._deformed_circles.value

    @property
    def arr_r(self) -> np.ndarray:
        """Radial coordinate grid
        """
        return self._arr_r.value

    @property
    def arr_theta(self) -> np.ndarray:
        """Tangential coordinate grid
        """
        return self._arr_theta.value
    # -------------------------------------------------------------------------
    # Methods for dependent variables
    # -------------------------------------------------------------------------

    @staticmethod
    def _reset_list() -> list:
        """Resets ActiveVariable to an empty list"""
        return []

    def _compute_scale_factor(
        self,
    ) -> float:
        """Computes the scaling factor for the wireframe plot

        Compute an appropriate scaling factor for the wireframe plot.
        """
        max_r_displacement = np.nanmax(
            np.abs(
                self.sol.radial_particle_displacement(
                    self.arr_r, self.arr_theta, t=0, mode=self.mode,
                ),
            ),
        )
        max_theta_displacement = np.nanmax(
            np.abs(
                self.sol.tangential_particle_displacement(
                    self.arr_r, self.arr_theta, t=0, mode=self.mode,
                ),
            ),
        )
        max_disp = max(max_r_displacement, max_theta_displacement)
        scale_factor = self.rel_scale_factor * self.sol.R_0 / max_disp
        return scale_factor

    def _compute_r_levels(self) -> np.ndarray:
        """ Compute radial levels
        """
        dr = self.sol.R_0 / self.nbr_r_levels
        return np.linspace(dr, self.sol.R_0, self.nbr_r_levels)

    def _compute_theta_levels(self) -> np.ndarray:
        """ Compute tangential levels
        """
        if self.symmetric:
            return np.linspace(0, pi, int(self.nbr_theta_levels / 2))
        else:
            return np.linspace(0, 2 * pi, int(self.nbr_theta_levels))

    def _compute_arr_r(self) -> np.ndarray:
        return np.linspace(1e-30, self.sol.R_0, self.resolution[0])

    def _compute_arr_theta(self) -> np.ndarray:
        if self.symmetric:
            return np.linspace(0, pi, self.resolution[1])
        else:
            return np.linspace(0, 2 * pi, self.resolution[1])

    # -------------------------------------------------------------------------
    # Compute data
    # -------------------------------------------------------------------------

    def _compute_data(self) -> None:
        self._compute_deformed_radii()
        self._compute_deformed_circles()

    def _compute_deformed_radii(self) -> None:
        for theta in self.theta_levels:
            deformed = self._compute_deformed_radius(theta)
            self._deformed_radii.value.append(deformed)

    def _compute_deformed_circles(self) -> None:
        for r in self.r_levels:
            self._deformed_circles.value.append(
                self._compute_deformed_circle(r),
            )

    def _compute_deformed_radius(self, Theta) -> DeformedLine:
        # Transform coordinates
        x, y = s2c_coord(self.arr_r, Theta)
        # Displacements
        u_r = self.sol.radial_particle_displacement(
            r=self.arr_r, theta=Theta, t=0, mode=self.mode,
        )
        u_theta = self.sol.tangential_particle_displacement(
            r=self.arr_r, theta=Theta, t=0, mode=self.mode,
        )
        # Transform displacements
        u, v = s2c_vector(u_r, u_theta, Theta)
        u_scaled, v_scaled = u * self.scale_factor, v * self.scale_factor
        return DeformedLine(x, y, u_scaled, v_scaled)

    def _compute_deformed_circle(
        self,
        R: float,
    ) -> DeformedLine:
        """Compute the deformed circle for radius `R`
        :param R: radius of the deformed circle
        """
        # Transform coordinates
        x, y = s2c_coord(R, self.arr_theta)
        u_r = self.sol.radial_particle_displacement(
            r=R, theta=self.arr_theta, t=0, mode=self.mode,
        )
        u_theta = self.sol.tangential_particle_displacement(
            r=R, theta=self.arr_theta, t=0, mode=self.mode,
        )
        # Transform displacements
        u, v = s2c_vector(u_r, u_theta, self.arr_theta)
        u_scaled, v_scaled = u * self.scale_factor, v * self.scale_factor
        return DeformedLine(x, y, u_scaled, v_scaled)


if __name__ == '__main__':
    pass
