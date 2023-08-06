import concurrent.futures
from typing import Any, Union

import numpy as np

from osaft.solutions.base_arf import BaseARF


class ARFData:
    """Container for plotting data for ARF plots

    :param sol: solution
    """

    _instances = 0
    _line_styles = [
        '-',
        '--',
        ':',
        '-.',
        (0, (5, 10)),
        (0, (3, 1, 1, 1)),
        (0, (1, 2)),
        (0, (8, 10)),
        (0, (5, 5)),
        (0, (5, 1)),
        (0, (3, 10, 1, 10)),
        (0, (3, 5, 1, 5)),
        (0, (3, 1, 1, 1)),
        (0, (3, 10, 1, 10, 1, 10)),
        (0, (3, 5, 1, 5, 1, 5)),
        (0, (3, 1, 1, 1, 1, 1)),
    ]

    def __init__(self, sol: BaseARF, multicore: bool = False) -> None:

        self.sol = sol
        self.multicore = multicore

        self._plotting = None
        self._arf = None
        self._norm_arf = None
        self._instance = ARFData._instances
        ARFData._instances += 1

    def compute_arf(self, attr_name: str, values: np.ndarray) -> None:

        if self.multicore:
            self._arf = self._compute_arf_multi_process(attr_name, values)
        else:
            self._arf = self._compute_arf_single_process(attr_name, values)
        self._plotting = self._arf

    def _compute_arf_single_process(
        self, attr_name: str, values: np.ndarray,
    ) -> np.ndarray:
        arf = []
        for val in values:
            arf.append(
                self._change_attr_and_compute_arf(
                    self.sol,
                    attr_name, val,
                ),
            )
        return np.asarray(arf)

    def _compute_arf_multi_process(
        self, attr_name: str, values: np.ndarray,
    ) -> np.ndarray:
        """Computes the ARF using multiple processes

        The ARF is computes using the `ProcessPoolExecutor` which will
        automatically dispatch the processes.
        """
        sols = [self.sol] * len(values)
        attr_names = [attr_name] * len(values)

        with concurrent.futures.ProcessPoolExecutor() as executor:
            arf = np.fromiter(
                executor.map(
                    self._change_attr_and_compute_arf,
                    sols, attr_names, values,
                ),
                dtype=float,
            )
        return arf

    @staticmethod
    def _change_attr_and_compute_arf(
        sol: BaseARF, attr_name: str, val: Any,
    ) -> float:
        """Changes the attribute `attr_name` to value `val`

        The attribute is change using `setattr`. Note that the solution has
        to be passed explicit because the method is also used in the
        multiprocessing.

        :attr_name: name of the attribute to be changed
        :attr_name: new value of the attribute
        """
        setattr(sol, attr_name, val)
        return sol.compute_arf()

    def normalize_arf(self, norm: np.ndarray) -> None:
        self._norm_arf = self._arf / norm
        self._plotting = self._norm_arf

    @property
    def line_style(self) -> Union[str, tuple[int, tuple[int]]]:

        L = len(ARFData._line_styles)
        return ARFData._line_styles[self._instance % L]

    @property
    def arf(self) -> np.ndarray:
        return self._arf

    @property
    def plotting(self) -> np.ndarray:
        return self._plotting

    @property
    def name(self) -> str:
        return self.sol.name


if __name__ == '__main__':
    pass
