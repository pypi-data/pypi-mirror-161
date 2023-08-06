from collections.abc import Sequence
from typing import Union

import numpy as np

from osaft.core.functions import pi


class Grid:
    """Data grid class for plotting

    Creates a data grid in spherical coordinates between `r_min` and `r_max`,
    and `theta_min` and `theta_max`. If `outside` `True` the grid is adjusted
    for plotting the fluid field in a square box with side `r_max`.
    Therefore, the grid goes from `r_min` to `sqrt(2) * r_max`


    :param r_min: start point for radial plotting range in [m]
    :param r_max: end point for tangential plotting range  in [m]
    :param theta_min: start point for tangential plotting range in [rad]
    :param theta_max: end point for tangential plotting range in [rad]
    :param res: resolution, if tuple (radial resolution, tangential resolution)
    """
    def __init__(
        self,
        r_min: float,
        r_max: float,
        theta_min: float = 0,
        theta_max: float = pi,
        res: Union[int, tuple[int, int]] = 100,
    ) -> None:
        """Constructor method"""
        self.r_min = r_min
        self.r_max = r_max
        self.theta_min = theta_min
        self.theta_max = theta_max
        self.r_res, self.theta_res = self._unpack_resolution(res)

    # -------------------------------------------------------------------------
    # Init Helper Methods
    # -------------------------------------------------------------------------

    @staticmethod
    def _unpack_resolution(res: Union[int, tuple[int, int]]):
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
    # Properties
    # -------------------------------------------------------------------------

    @property
    def dr(self):
        """Step size in radial direction"""
        return (self.r_max - self.r_min) / self.r_res

    @property
    def dtheta(self):
        """Step size in tangential direction"""
        return (self.theta_max - self.theta_min) / self.theta_res

    @property
    def arr_r(self):
        """Linearly spaced array in radial direction"""
        return np.linspace(self.r_min, self.r_max, self.r_res)

    @property
    def arr_theta(self):
        """Linearly spaced array in tangential direction"""
        return np.linspace(self.theta_min, self.theta_max, self.theta_res)


if __name__ == '__main__':
    pass
