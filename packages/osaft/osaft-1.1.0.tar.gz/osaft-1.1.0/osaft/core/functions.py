from collections.abc import Callable, Iterable
from typing import Optional

import numpy as np
from scipy import special
from scipy.integrate import quad
from scipy.special import exp1, factorial, lpmv

from osaft import log

# Often used NumPy and SciPy Functions and Classes
conj = np.conj
exp = np.exp
real = np.real
imag = np.imag
sqrt = np.sqrt
sin = np.sin
cos = np.cos
pi = np.pi


def full_range(*args: int) -> Iterable:
    """Returns the range including the end point.

    :param args: end point, start point (optional)
    :raises: ValueError if more than 2 arguments are passed    """
    if len(args) == 1:
        return range(args[0] + 1)
    elif len(args) == 2:
        return range(args[0], args[1] + 1)
    else:
        raise ValueError('full_range takes one or two arguments.')


def cartesian_2_spherical_coordinates(
    x: float, z: float,
) -> tuple[float, float]:
    """Transforms Cartesian coordinates `(x  z)` of an axisymmetric model into
    spherical coordinates `(r, theta)`. See `here
    <https://gitlab.ethz.ch/goeringc/src-git/-/wikis/Definition-of-the-Coordinate-System>`__
    for the definition of the coordinate system.

    :param x: x coordinate
    :param z: z coordinate
    """
    r = np.hypot(x, z)
    theta = np.arctan2(x, z)
    return r, theta


def spherical_2_cartesian_coordinates(
    r: float, theta: float,
) -> tuple[float, float]:
    """Transforms spherical coordinates `(r  theta)` of an axisymmetric model
    into Cartesian coordinates `(x, z)`. See `here
    <https://gitlab.ethz.ch/goeringc/src-git/-/wikis/Definition-of-the-Coordinate-System>`__
    for the definition of the coordinate system.

    :param r: x radial coordinate
    :param theta: polar angle
    """
    x = r * sin(theta)
    z = r * cos(theta)
    return x, z


def transform_vector(v_x: float, v_y: float, theta: float) -> [float, float]:
    """Transforms the coordinates of a vector in the xy-plane from the
    reference system to a coordinate system rotated by `theta`

    :param v_x: first coordinate of the vector
    :param v_y: second coordinate of the vector
    :param theta: rotation angle
    """
    v_xt = sin(theta) * v_x + cos(theta) * v_y
    v_yt = cos(theta) * v_x - sin(theta) * v_y
    return v_xt, v_yt


def spherical_2_cartesian_vector(
    v_r: float,
    v_theta: float,
    theta: float,
) -> tuple[float, float]:
    """Transforms velocities in the Spherical coordinate system
    `(v_r, v_theta)` of an axisymmetric model to the Cartesian system
    `(v_x, v_z)`. See `here
    <https://gitlab.ethz.ch/goeringc/src-git/-/wikis/Definition-of-the-Coordinate-System>`__
    for the definition of the coordinate system.

    :param v_r: velocity in radial direction
    :param v_theta: velocity in tangential direction
    :param theta: polar angle
    """
    return transform_vector(v_r, v_theta, theta)


def cartesian_2_spherical_vector(
    v_x: float,
    v_z: float,
    theta: float,
) -> tuple[float, float]:
    """Transforms velocities in the a Spherical coordinate system
    `(v_r, v_theta)` of an axisymmetric model to the Cartesian system
    `(v_x, v_z)`. See `here
    <https://gitlab.ethz.ch/goeringc/src-git/-/wikis/Definition-of-the-Coordinate-System>`__
    for the definition of the coordinate system.

    :param v_x: velocity in radial direction
    :param v_z: velocity in tangential direction
    :param theta: polar angle
    """
    return transform_vector(v_x, v_z, theta)


def clebsch_gordan_coefficient(
    j1: int, m1: int,
    j2: int, m2: int,
    j: int, m: int,
) -> float:
    """ Clebsch-Gordan coefficient for integer valued arguments.

    :param j:
    :param m:
    :param j1:
    :param m1:
    :param j2:
    :param m2:
    """

    for arg in [j1, m1, j2, m2, j, m]:
        if not isinstance(arg, int):
            raise ValueError('Arguments need to be integer valued.')

    if (m1 + m2) != m:
        return 0
    elif j1 + j2 < j or abs(j1 - j2) > j:
        return 0
    else:
        c = 0.0
        z = 0
        a = (
            factorial(j1 + j2 - j) * factorial(j1 - j2 + j)
            * factorial(-j1 + j2 + j) / factorial(j1 + j2 + j + 1.0)
        )**0.5
        b = (
            factorial(j1 + m1) * factorial(j1 - m1) * factorial(j2 + m2)
            * factorial(j2 - m2) * factorial(j + m) * factorial(j - m)
        )**0.5
        while z < (j1 - m1 + 3):
            denominator = (
                factorial(z) * factorial(j1 + j2 - j - z)
                * factorial(j1 - m1 - z)
                * factorial(j2 + m2 - z)
                * factorial(j - j2 + m1 + z)
                * factorial(j - j1 - m2 + z)
            )
            numerator = (-1)**float(z + j1 - j2 + m)
            if denominator != 0:
                c += numerator / denominator
            z += 1
        return (-1.0)**(j1 - j2 + m) * (2.0 * j + 1.0)**0.5 * a * b * c


def integrate(
    func: Callable[[float], float], lower: float, upper: float,
    rel_eps: float = 1e-6,
) -> tuple[float, float]:
    """ Integrates :attr:`func` between :attr:`lower` and :attr:`upper`
    Scipy's QUADPACK implementation `quad()
    <https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate
    .quad.html>`__ .

    :param func: function to be integrated.
    :param lower: lower integration limit
    :param upper: upper integration limit
    :param rel_eps: estimated relative error of integration
    """

    # Logging
    log.debug(
        'Relative precision goal for integration has been passed.'
        'Adaptive integration scheme is chosen.',
    )
    # Integration
    integral, abs_err = quad(
        func, lower, upper, epsabs=0,
        epsrel=rel_eps, limit=200,
    )
    log.debug(
        f'Integral = {integral},'
        f'absolute error estimation = {abs_err}\n',
    )
    return integral, abs_err


def integrate_osc(
    func: Callable[[float], float], lower: float, upper: float,
    boundary_layer: float,
    viscous_wavelength: Optional[float] = None,
    resolution: int = 4,
    roi_factor: int = 5,
    rel_eps: float = 1e-6,
) -> tuple[float, float]:
    """ Special purpose integrator for oscillating integrals that
    integrates :attr:`func` between :attr:`lower` and  :attr:`upper`. This
    method employs Scipy's QUADPACK implementation `quad()
    <https://docs.scipy.org/doc/scipy/reference/generated/
    scipy.integrate.quad.html>`__. Used primarily for boundary layer
    integration for elastic fluids. The method creates a list of
    uniformly distributes points in a region of interest where local
    difficulties are expected.
    The density of points per viscous wavelength is given by
    :attr:`resolution`, the region of interest is given by
    [:attr:`lower`, :attr:`lower` + :attr:`roi_factor` :math:`*`
    :attr:`boundary_layer`].
    Function returns the integral and an error estimate.

    :param func: function to be integrated. If no rel_eps is passed the
        function needs to be vectorized.
    :param lower: lower integration limit
    :param upper: upper integration limit
    :param viscous_wavelength: viscous wavelength in the fluid [m]
    :param boundary_layer: boundary layer thickness in the fluid [m]
    :param resolution: number of integration points per wavelength passed
    :param roi_factor: multiplier to compute ROI  (see above)
    :param rel_eps: estimated relative error of integration
    """

    if viscous_wavelength is None:
        viscous_wavelength = 2 * pi * boundary_layer

    # Generate points
    dx = viscous_wavelength / resolution
    region_of_interest = roi_factor * boundary_layer
    n = int(region_of_interest / dx)
    points = np.linspace(lower, lower + region_of_interest, n)

    # Test if subdivision limit is large enough
    limit = 10 * n if 10 * n > 50 else 50

    # Integrate
    integral, abs_err = quad(
        func, lower, upper, epsabs=0, epsrel=rel_eps,
        points=points, limit=limit,
    )

    log.debug(
        f'Integral = {integral},'
        f'absolute error estimation = {abs_err}\n',
    )
    return integral, abs_err


def xexpexp1(z: complex, N: int = 20) -> complex:
    """Computes :math:`z\\exp(z)E_1(z)`

    The function is meant to return accurate values also if
    :math:`\\mathrm{Re}(z)` is large. If :math:`\\mathrm{Re}(z)` is large
    then the divergent series is used

    :param z: argument
    :param N: number of terms to be considered
    """
    if z.real > 20:
        s = 0
        for n in range(N, 0, -1):
            s = (s + (-1) ** n) * n / z
        return s + 1
    else:
        return z * exp(z) * exp1(z)


class LegendreFunctions:
    """ This class gathers all reoccurring Legendre Functions necessary for
     the osaft package. """

    @staticmethod
    def cos_poly(theta: float, coefficients: np.array) -> np.ndarray:
        """ Sum of Legendre polynomial with a cosine function as an argument

        :param theta: angle
        :param coefficients: coefficients of the polynomial
        """
        return np.polynomial.legendre.legval(
            cos(theta), coefficients,
            tensor=False,
        )

    @staticmethod
    def cos_monomial(degree: int, theta: float, coefficient: complex) -> float:
        """ Returns a single term of Legendre Cosine series

        :param degree: degree of the polynomial to be returned
        :param theta:  angle
        :param coefficient: coefficients of the polynomial
        """
        return coefficient * lpmv(0, degree, cos(theta))

    @staticmethod
    def first_cos_poly(theta: float, coefficients: np.array) -> np.ndarray:
        """ Sum of associate Legendre Polynomial of order one with a cosine
        as input variable

        :param theta: angle
        :param coefficients: coefficients of the polynomial
        """
        degrees = len(coefficients)
        return np.sum(
            [
                coefficients[n] * lpmv(1, n, cos(theta))
                for n in range(degrees)
            ],
            axis=0,
        )

    @staticmethod
    def first_cos_monomial(
        degree: int, theta: float,
        coefficient: complex,
    ) -> float:
        """ Returns a single term of associate Legendre Cosine series of the
        first order

        :param degree: degree of the term
        :param theta:  angle
        :param coefficient: coefficient of the polynomial
        """
        return coefficient * lpmv(1, degree, cos(theta))


class BesselFunctions:
    """ This class gathers all reoccurring spherical hankel and bessel
    functions necessary for the osaft package. """

    @staticmethod
    def _a0_d2(n: int, z: complex) -> complex:
        return (n**2 - n - z**2) / z**2

    @staticmethod
    def _a1_d2(n: int, z: complex) -> complex:
        return 2 / z

    @staticmethod
    def _a0_d3(n: int, z: complex) -> complex:
        return (n**3 - 3 * n**2 + 2 * n) / z**3 + (2 - n) / z

    @staticmethod
    def _a1_d3(n: int, z: complex) -> complex:
        return (-n**2 - n - 6) / z**2 + 1

    @staticmethod
    def _a0_d4(n: int, z: complex) -> complex:
        return (
            n * (n - 1) * (6 + n * (n - 5)) / z ** 4
            + (-2 * n * (n - 1) - 8) / z ** 2 + 1
        )

    @staticmethod
    def _a1_d4(n: int, z: complex) -> complex:
        return 8 * (3 + n + n**2) / z**3 - 4 / z

    @staticmethod
    def _a0_d5(n: int, z: complex) -> complex:
        return (
            (-4 + n) * (-3 + n) * (-2 + n) * (-1 + n) * n
            - 2 * (-20 + n * (2 + (-7 + n) * n)) * z**2
            + (-4 + n) * z**4
        ) / z**5

    @staticmethod
    def _a1_d5(n: int, z: complex) -> complex:
        return -(
            (
                n * (1 + n) * (58 + n + n**2) - 2 * n * (1 + n) * z**2 + z**4
                - 20 * (-6 + z**2)
            ) / z**4
        )

    @staticmethod
    def besselj(n: int, z: complex) -> complex:
        """Spherical Bessel function of the first kind of order `n`

        :param n: Order
        :param z: argument
        """
        return special.spherical_jn(n, z)

    @classmethod
    def d1_besselj(cls, n: int, z: complex) -> complex:
        """First derivative of the spherical Bessel function of the first kind
        of order `n`

        :param n: order
        :param z: argument
        """
        return special.spherical_jn(n, z, derivative=True)

    @classmethod
    def d2_besselj(cls, n: int, z: complex) -> complex:
        """Second derivative of the spherical Bessel function of the first kind
        of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d2(n, z) * cls.besselj(n, z)
            + cls._a1_d2(n, z) * cls.besselj(n + 1, z)
        )

    @classmethod
    def d3_besselj(cls, n: int, z: complex) -> complex:
        """Third derivative of the spherical Bessel function of the first kind
        of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d3(n, z) * cls.besselj(n, z)
            + cls._a1_d3(n, z) * cls.besselj(n + 1, z)
        )

    @classmethod
    def d4_besselj(cls, n: int, z: complex) -> complex:
        """Fourth derivative of the spherical Bessel function of the first kind
        of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d4(n, z) * cls.besselj(n, z)
            + cls._a1_d4(n, z) * cls.besselj(n + 1, z)
        )

    @staticmethod
    def bessely(n: int, z: complex) -> complex:
        """Spherical Bessel function of the second kind of order `n`

        :param n: order
        :param z: argument
        """
        return special.spherical_yn(n, z)

    @classmethod
    def d1_bessely(cls, n: int, z: complex) -> complex:
        """First derivative of the spherical Bessel function of the second
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return special.spherical_yn(n, z, True)

    @classmethod
    def d2_bessely(cls, n: int, z: complex) -> complex:
        """Second derivative of the spherical Bessel function of the second
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d2(n, z) * cls.bessely(n, z)
            + cls._a1_d2(n, z) * cls.bessely(n + 1, z)
        )

    @classmethod
    def d3_bessely(cls, n: int, z: complex) -> complex:
        """Third derivative of the spherical Bessel function of the second
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d3(n, z) * cls.bessely(n, z)
            + cls._a1_d3(n, z) * cls.bessely(n + 1, z)
        )

    @classmethod
    def d4_bessely(cls, n: int, z: complex) -> complex:
        """Fourth derivative of the spherical Bessel function of the second
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d4(n, z) * cls.bessely(n, z)
            + cls._a1_d4(n, z) * cls.bessely(n + 1, z)
        )

    @staticmethod
    def hankelh1(n: int, z: complex) -> complex:
        """Spherical Hankel function of the first kind of order `n`

        :param n: order
        :param z: argument
        """
        return sqrt(pi / (2 * z)) * special.hankel1(n + 0.5, z)

    @classmethod
    def d1_hankelh1(cls, n: int, z: complex) -> complex:
        """First derivative of the spherical Hankel function of the first
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return -cls.hankelh1(n + 1, z) + (n / z) * cls.hankelh1(n, z)

    @classmethod
    def d2_hankelh1(cls, n: int, z: complex) -> complex:
        """Second derivative of the spherical Hankel function of the first
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d2(n, z) * cls.hankelh1(n, z)
            + cls._a1_d2(n, z) * cls.hankelh1(n + 1, z)
        )

    @classmethod
    def d3_hankelh1(cls, n: int, z: complex) -> complex:
        """Third derivative of the spherical Hankel function of the first
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d3(n, z) * cls.hankelh1(n, z)
            + cls._a1_d3(n, z) * cls.hankelh1(n + 1, z)
        )

    @classmethod
    def d4_hankelh1(cls, n: int, z: complex) -> complex:
        """Fourth derivative of the spherical Hankel function of the first
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d4(n, z) * cls.hankelh1(n, z)
            + cls._a1_d4(n, z) * cls.hankelh1(n + 1, z)
        )

    @classmethod
    def d5_hankelh1(cls, n: int, z: complex) -> complex:
        """Fifth derivative of the spherical Hankel function of the first
        kind of order `n`

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d5(n, z) * cls.hankelh1(n, z)
            + cls._a1_d5(n, z) * cls.hankelh1(n + 1, z)
        )

    @staticmethod
    def hankelh2(n: int, z: complex) -> complex:
        """Spherical Hankel function of the second kind of order `n`

        :param n: order
        :param z: argument
        """
        return sqrt(pi / (2 * z)) * special.hankel2(n + 0.5, z)

    @classmethod
    def d1_hankelh2(cls, n: int, z: complex) -> complex:
        """First derivative of the spherical Hankel function of the second
        kind of order `n` second kind

        :param n: order
        :param z: argument
        """
        return -cls.hankelh2(n + 1, z) + (n / z) * cls.hankelh2(n, z)

    @classmethod
    def d2_hankelh2(cls, n: int, z: complex) -> complex:
        """Second derivative of the spherical Hankel function of the second
        kind of order `n` second kind

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d2(n, z) * cls.hankelh2(n, z)
            + cls._a1_d2(n, z) * cls.hankelh2(n + 1, z)
        )

    @classmethod
    def d3_hankelh2(cls, n: int, z: complex) -> complex:
        """Third derivative of the spherical Hankel function of the second
        kind of order `n` second kind

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d3(n, z) * cls.hankelh2(n, z)
            + cls._a1_d3(n, z) * cls.hankelh2(n + 1, z)
        )

    @classmethod
    def d4_hankelh2(cls, n: int, z: complex) -> complex:
        """Fourth derivative of the spherical Hankel function of the second
        kind of order `n` second kind

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d4(n, z) * cls.hankelh2(n, z)
            + cls._a1_d4(n, z) * cls.hankelh2(n + 1, z)
        )

    @classmethod
    def d5_hankelh2(cls, n: int, z: complex) -> complex:
        """Fifth derivative of the spherical Hankel function of the second
        kind of order `n` second kind

        :param n: order
        :param z: argument
        """
        return (
            cls._a0_d5(n, z) * cls.hankelh2(n, z)
            + cls._a1_d5(n, z) * cls.hankelh2(n + 1, z)
        )

    @classmethod
    def adaptive_derivative_besselj(
            cls, n: int, z: complex, i: int = 0,
    ) -> complex:
        """Returns the value of the `i`-th derivative of the spherical
        Bessel function of the first kind of order `n`. The
        coefficients for the derivative are calculated at runtime.

        :param n: order of spherical Bessel function
        :param z: argument of the function
        :param i: i-th derivative is computed
        """
        return cls._adaptive_derivative(cls.besselj, i, n, z)

    @classmethod
    def adaptive_derivative_bessely(
            cls, n: int, z: complex, i: int,
    ) -> complex:
        """Returns the value of the `i`-th derivative of the spherical
        Bessel function of the second kind of order `n`. The coefficients
        for the derivative are calculated at runtime.

        :param n: order of spherical Hankel function
        :param z: argument of the function
        :param i: i-th derivative is computed at runtime.
        """
        return cls._adaptive_derivative(cls.bessely, i, n, z)

    @classmethod
    def adaptive_derivative_hankelh1(
            cls, n: int, z: complex, i: int,
    ) -> complex:
        """Returns the value of the `i`-th derivative of the spherical
        Hankel function of order `n`. The coefficients for the derivative
        are calculated at runtime.

        :param n: order of spherical Hankel function
        :param z: argument of the function
        :param i: i-th derivative is computed
        """
        return cls._adaptive_derivative(cls.hankelh1, i, n, z)

    @classmethod
    def adaptive_derivative_hankelh2(
            cls, n: int, z: complex, i: int,
    ) -> complex:
        """Returns the value of the `i`-th derivative of the spherical
        Hankel function of order `n`. The coefficients for the derivative
        are calculated at runtime.

        :param n: order of spherical Hankel function
        :param z: argument of the function
        :param i: i-th derivative is computed
        """
        return cls._adaptive_derivative(cls.hankelh2, i, n, z)

    @classmethod
    def _adaptive_derivative(
        cls, func: Callable[[int, complex], complex],
        i: int, n: int, z: complex,
    ) -> complex:
        out = 0
        for j in np.arange(i + 1):
            out += cls._adaptive_coefficient(
                i, j, n, z,
            ) * func(n + j, z)
        return out

    @classmethod
    def _adaptive_coefficient(
        cls, i: int, j: int,
        n: int, z: complex,
    ) -> complex:
        if j > i or j < 0:
            out = 0
        elif j == i:
            out = (-1)**i
        elif j == 0 and i == 1:
            out = n / z
        else:
            out = (n + 2 * j + 1 - i) / z
            out *= cls._adaptive_coefficient(i - 1, j, n, z)
            out -= cls._adaptive_coefficient(i - 1, j - 1, n, z)

        return out


if __name__ == '__main__':
    pass
