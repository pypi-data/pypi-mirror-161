from collections.abc import Sequence
from enum import Enum
from numbers import Number
from typing import Optional, Union

import numpy as np

from osaft.core.functions import pi


class StringFormatter:
    """ Consistent Formatting for __str__ and __repr__ methods
    """

    @staticmethod
    def get_str_text(
        description: str, variable: str,
        value: Union[float, int, str, Enum], unit: Optional[str] = None,
        linebreak: bool = True,
    ) -> str:
        """
        Returns a constant formatting for the `__str__` method of the ARF
        classes

        :param description: Physical name for the variable
        :param variable: symbol/name of the variable
        :param value: value of the variable
        :param unit: unit of the variable
        :param linebreak: Appends a linebreak to the end of the text
        """
        out = f'{description:<20s}:\t'
        out += f'{variable:>8s} = '
        if isinstance(value, bool) or value is None:
            out += str(value)
        elif isinstance(value, Enum):
            out += f'{value.name:8s}'
        else:
            out += f'{value:5.2e}'
        if unit is not None and unit != '':
            out += f' [{unit:s}]'
        if linebreak:
            out += '\n'

        return out


class InputHandler:
    """ Handles inputs for velocity field methods

    Tests if inputs r, theta, t passed to methods that compute the velocity
    field are valid inputs and converts the inputs to numpy.ndarray.
    """

    @staticmethod
    def _test_array(
        array: np.ndarray,
        low: Optional[float] = None,
        high: Optional[float] = None,
    ):

        if low is not None and np.any(array < low):
            msg = f'at least one value is smaller than {low}'
            raise ValueError(msg)
        if high is not None and np.any(array > high):
            msg = f'at least one value is greater than {high}'
            raise ValueError(msg)

    @classmethod
    def handle_input(
        cls, r: Union[Number, Sequence],
        theta: Union[Number, Sequence],
        t: Union[Number, Sequence],
        R_0: Union[Number, Sequence],
        inside_sphere: bool,
    ):
        """Tests if inputs r, theta, t passed to methods that compute the
        velocity field are valid inputs and converts the
        inputs to numpy.ndarray.

        :param r: radial coordinate
        :param theta: tangential coordinate
        :param t: time
        :param R_0: radius of the sphere
        :param inside_sphere: if `True`/`False` tests if `r` is inside/outside
        """

        # Convert to numpy array if necessary
        arr_r = np.asarray(r)
        arr_theta = np.asarray(theta)
        arr_t = np.asarray(t)

        # Test radius
        if inside_sphere:
            cls._test_array(arr_r, low=0, high=R_0)
        else:
            cls._test_array(arr_r, low=R_0)

        # Test theta
        cls._test_array(arr_theta, 0, pi)

        return arr_r, arr_theta, arr_t


if __name__ == '__main__':
    pass
