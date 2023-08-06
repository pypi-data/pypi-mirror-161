from typing import Optional, Union

import numpy as np

from osaft.core.backgroundfields import WaveType
from osaft.core.frequency import Frequency
from osaft.core.functions import BesselFunctions as Bf
from osaft.core.geometries import Sphere
from osaft.core.variable import ActiveListVariable, ActiveVariable
from osaft.solutions.doinikov1994compressible.base import (
    BaseDoinikov1994Compressible,
)


class CoefficientMatrix(BaseDoinikov1994Compressible):
    """Coefficient Matrix Doinikov (viscous fluid-viscous sphere; 1994)

    :param f: Frequency [Hz]
    :param R_0: Radius of the sphere [m]
    :param rho_s: Density of the sphere [kg/m^3]
    :param c_s: Speed of sound of in the sphere [m/s]
    :param eta_s: shear viscosity of in the sphere  [Pa s]
    :param zeta_s: bulk viscosity of in the sphere [Pa s]
    :param rho_f: Density of the fluid [kg/m^3]
    :param c_f: Speed of sound of the fluid [m/s]
    :param eta_f: shear viscosity [Pa s]
    :param zeta_f: bulk viscosity [Pa s]
    :param p_0: Pressure amplitude of the field [Pa]
    :param position: Position within the standing wave field [m]
    :param wave_type: Type of wave, traveling or standing
    """

    def __init__(
        self, f: Union[Frequency, float, int],
        R_0: Union[Sphere, float, int],
        rho_s: float, c_s: float, eta_s: float, zeta_s: float,
        rho_f: float, c_f: float, eta_f: float, zeta_f: float,
        p_0: float, wave_type: WaveType, position: float,
    ) -> None:

        # init of parent method
        super().__init__(
            f=f, R_0=R_0,
            rho_s=rho_s, c_s=c_s, eta_s=eta_s, zeta_s=zeta_s,
            rho_f=rho_f, c_f=c_f, eta_f=eta_f, zeta_f=zeta_f,
            p_0=p_0, wave_type=wave_type, position=position,
        )

        # Dependent Variables
        self._x_hat = ActiveVariable(self._compute_x_hat, 'x_hat')
        self._x_hat_v = ActiveVariable(self._compute_x_hat_v, 'x_v hat')
        self._list_matrix_M_n = ActiveListVariable(
            self._compute_matrix_M_n,
            'Matrices M(n)',
        )
        self._list_vector_N_n = ActiveListVariable(
            self._compute_vector_N_n,
            'Vectors N(n)',
        )
        self._x_hat.is_computed_by(
            self.scatterer._k_f, self.sphere._R_0,
        )
        self._x_hat_v.is_computed_by(
            self.scatterer._k_v, self.sphere._R_0,
        )
        self._list_matrix_M_n.is_computed_by(
            self._x, self._x_v,
            self._x_hat, self._x_hat_v,
            self.frequency._omega,
            self.fluid._c_f, self.scatterer._c_f,
            self.fluid._rho_f, self.scatterer._rho_f,
            self.fluid._eta_f, self.scatterer._eta_f,
            self.fluid._zeta_f, self.scatterer._zeta_f,
        )
        self._list_vector_N_n.is_computed_by(
            self._x,
            self.frequency._omega,
            self.fluid._c_f, self.fluid._rho_f,
            self.fluid._eta_f, self.fluid._zeta_f,
        )

    def det_M_n(self, n: int, column: Optional[int] = None) -> complex:
        """Determinant of the matrix `M` for the mode `n`

        :param n: mode
        :param column: the `l`th coefficient is replaced with the vector `N`
        """
        matrix = self.M(n).copy()
        vector = self.N(n)
        if column is not None:
            matrix[:, column] = vector
        return np.linalg.det(matrix)

    def M(self, n: int) -> np.ndarray:
        """Matrix M of order `n`

        :param n: order
        """
        return self._list_matrix_M_n.item(n)

    def N(self, n: int) -> np.ndarray:
        """Vector `N`"""
        return self._list_vector_N_n.item(n)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def x_hat(self) -> complex:
        """Product of :attr:`~.k_s` and :attr:`~.R_0`
        :math:`\\hat{x}=k_s R_0`
        """
        return self._x_hat.value

    def _compute_x_hat(self) -> complex:
        return self.k_s * self.R_0

    @property
    def x_hat_v(self) -> complex:
        """Product of :attr:`~.k_vs` and :attr:`~.R_0`
        :math:`\\hat{x}_v=\\hat{k}_s R_0`
        """
        return self._x_hat_v.value

    def _compute_x_hat_v(self) -> complex:
        return self.k_vs * self.R_0

    # -------------------------------------------------------------------------
    # Vector N(n)
    # -------------------------------------------------------------------------

    def _compute_vector_N_n(self, n: int) -> np.ndarray:
        vector = np.zeros(4, dtype=complex)

        vector[0] = -self.x * Bf.d1_besselj(n, self.x)

        vector[1] = -Bf.besselj(n, self.x)
        vector[2] = 1j * self.rho_f * self.c_f**2 / self.omega
        vector[2] += self.zeta_f
        vector[2] -= 2 / 3 * self.eta_f
        vector[2] *= Bf.besselj(n, self.x)
        vector[2] -= 2 * self.eta_f * Bf.d2_besselj(n, self.x)
        vector[2] *= self.x**2
        vector[3] = Bf.besselj(n, self.x)
        vector[3] -= self.x * Bf.d1_besselj(n, self.x)
        vector[3] *= 2 * self.eta_f

        return vector

    # -----------------------------------------------------------------------
    # Matrix M(n)
    # -----------------------------------------------------------------------

    def _compute_matrix_M_n(self, n: int) -> np.ndarray:

        # Initialize matrix
        matrix = np.zeros((4, 4), dtype=complex)

        # First row
        matrix[0, 0] = self.x * Bf.d1_hankelh1(n, self.x)
        matrix[0, 1] = -n * (n + 1) * Bf.hankelh1(n, self.x_v)
        matrix[0, 2] = - self.x_hat * Bf.d1_besselj(n, self.x_hat)
        matrix[0, 3] = n * (n + 1) * Bf.besselj(n, self.x_hat_v)

        # Second Row
        matrix[1, 0] = Bf.hankelh1(n, self.x)
        matrix[1, 1] = -Bf.hankelh1(n, self.x_v)
        matrix[1, 1] -= self.x_v * Bf.d1_hankelh1(n, self.x_v)
        matrix[1, 2] = -Bf.besselj(n, self.x_hat)
        matrix[1, 3] = Bf.besselj(n, self.x_hat_v)
        matrix[1, 3] += self.x_hat_v * Bf.d1_besselj(n, self.x_hat_v)

        # Third row
        matrix[2, 0] = 1j * self.rho_f * self.c_f**2 / self.omega
        matrix[2, 0] += self.zeta_f
        matrix[2, 0] -= 2 / 3 * self.eta_f
        matrix[2, 0] *= -Bf.hankelh1(n, self.x)
        matrix[2, 0] += 2 * self.eta_f * Bf.d2_hankelh1(n, self.x)
        matrix[2, 0] *= self.x**2

        matrix[2, 1] = Bf.hankelh1(n, self.x_v)
        matrix[2, 1] -= self.x_v * Bf.d1_hankelh1(n, self.x_v)
        matrix[2, 1] *= 2 * n * (n + 1) * self.eta_f

        matrix[2, 2] = 1j * self.rho_s * self.c_s**2 / self.omega
        matrix[2, 2] += self.zeta_s
        matrix[2, 2] -= 2 / 3 * self.eta_s
        matrix[2, 2] *= Bf.besselj(n, self.x_hat)
        matrix[2, 2] -= 2 * self.eta_s * Bf.d2_besselj(n, self.x_hat)
        matrix[2, 2] *= self.x_hat**2

        matrix[2, 3] = self.x_hat_v * Bf.d1_besselj(n, self.x_hat_v)
        matrix[2, 3] -= Bf.besselj(n, self.x_hat_v)
        matrix[2, 3] *= 2 * n * (n + 1) * self.eta_s

        # Fourth row
        matrix[3, 0] = self.x * Bf.d1_hankelh1(n, self.x)
        matrix[3, 0] -= Bf.hankelh1(n, self.x)
        matrix[3, 0] *= 2 * self.eta_f
        matrix[3, 1] = self.x_v ** 2 * Bf.d2_hankelh1(n, self.x_v)
        matrix[3, 1] += (n**2 + n - 2) * Bf.hankelh1(n, self.x_v)
        matrix[3, 1] *= -self.eta_f
        matrix[3, 2] = Bf.besselj(n, self.x_hat)
        matrix[3, 2] -= self.x_hat * Bf.d1_besselj(n, self.x_hat)
        matrix[3, 2] *= 2 * self.eta_s

        matrix[3, 3] = self.x_hat_v ** 2 * Bf.d2_besselj(n, self.x_hat_v)
        matrix[3, 3] += (n**2 + n - 2) * Bf.besselj(n, self.x_hat_v)
        matrix[3, 3] *= self.eta_s
        return matrix


if __name__ == '__main__':
    pass
