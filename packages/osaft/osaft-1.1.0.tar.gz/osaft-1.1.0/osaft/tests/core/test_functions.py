import unittest

import numpy as np
from scipy.special import exp1, factorial, lpmv
from sympy.physics.quantum.cg import CG

from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import LegendreFunctions as Leg
from osaft.core.functions import (
    cartesian_2_spherical_coordinates,
    cartesian_2_spherical_vector,
)
from osaft.core.functions import clebsch_gordan_coefficient as cg
from osaft.core.functions import (
    cos,
    exp,
    full_range,
    integrate,
    integrate_osc,
    pi,
    sin,
    spherical_2_cartesian_coordinates,
    spherical_2_cartesian_vector,
    sqrt,
    xexpexp1,
)
from osaft.tests.basetest import NumericTestCase


class TestFunctions(NumericTestCase):

    # -------------------------------------------------------------------------
    # Range
    # -------------------------------------------------------------------------

    def test_full_range(self):
        res = full_range(1)
        self.assertEqual(res, range(0, 2))

        res = full_range(-1, 3)
        self.assertEqual(res, range(-1, 4))

        self.assertRaises(ValueError, full_range, 1, 0, 3)

    # -------------------------------------------------------------------------
    # Coordinate Transforms
    # -------------------------------------------------------------------------

    def test_cartesian_2_spherical(self):

        x = 0
        z = 0
        r, theta = cartesian_2_spherical_coordinates(x, z)
        self.assertEqual(r, 0)
        self.assertEqual(theta, 0)

        x = 1
        z = 1
        r, theta = cartesian_2_spherical_coordinates(x, z)
        self.assertEqual(r, sqrt(2))
        self.assertEqual(theta, pi / 4)

        x = -1
        z = 0
        r, theta = cartesian_2_spherical_coordinates(x, z)
        self.assertEqual(r, 1)
        self.assertEqual(theta, -pi / 2)

        x = -1
        z = 1
        r, theta = cartesian_2_spherical_coordinates(x, z)
        self.assertEqual(r, sqrt(2))
        self.assertEqual(theta, -pi / 4)

        x = -1
        z = -1
        r, theta = cartesian_2_spherical_coordinates(x, z)
        self.assertEqual(r, sqrt(2))
        self.assertEqual(theta, -pi * 3 / 4)

    def test_spherical_2_cartesian(self):

        r = 0
        theta = 0
        x, z = spherical_2_cartesian_coordinates(r, theta)
        self.assertAlmostEqual(x, 0)
        self.assertAlmostEqual(z, 0)

        r = 0
        theta = pi / 2
        x, z = spherical_2_cartesian_coordinates(r, theta)
        self.assertAlmostEqual(x, 0)
        self.assertAlmostEqual(z, 0)

        r = 2
        theta = pi / 4
        x, z = spherical_2_cartesian_coordinates(r, theta)
        self.assertAlmostEqual(x, 2 * sqrt(2) / 2)
        self.assertAlmostEqual(z, 2 * sqrt(2) / 2)

        r = 3
        theta = pi / 4
        x, z = spherical_2_cartesian_coordinates(r, theta)
        self.assertAlmostEqual(x, 3 * sqrt(2) / 2)
        self.assertAlmostEqual(z, 3 * sqrt(2) / 2)

        r = 2
        theta = pi / 2
        x, z = spherical_2_cartesian_coordinates(r, theta)
        self.assertAlmostEqual(x, 2)
        self.assertAlmostEqual(z, 0, threshold=1e-10)

        r = 2
        theta = pi
        x, z = spherical_2_cartesian_coordinates(r, theta)
        self.assertAlmostEqual(x, 0, threshold=1e-10)
        self.assertAlmostEqual(z, -2)

    def test_spherical_2_cartesian_velocities(self):

        theta = 3 / 7 * pi
        v_r = 10
        v_theta = -1
        v_x = sin(theta) * v_r + cos(theta) * v_theta
        v_z = cos(theta) * v_r - sin(theta) * v_theta
        self.assertEqual(
            (v_x, v_z), spherical_2_cartesian_vector(v_r, v_theta, theta),
        )

        theta = 0
        v_r = 10
        v_theta = -1
        v_x = sin(theta) * v_r + cos(theta) * v_theta
        v_z = cos(theta) * v_r - sin(theta) * v_theta
        self.assertEqual(
            (v_x, v_z), spherical_2_cartesian_vector(v_r, v_theta, theta),
        )

        theta = -pi
        v_r = 0
        v_theta = -1
        v_x = sin(theta) * v_r + cos(theta) * v_theta
        v_z = cos(theta) * v_r - sin(theta) * v_theta
        self.assertEqual(
            (v_x, v_z), spherical_2_cartesian_vector(v_r, v_theta, theta),
        )

    def test_cartesian_2_spherical_velocities(self):

        theta = 0
        v_x = 10
        v_z = 0
        v_r, v_theta = cartesian_2_spherical_vector(v_x, v_z, theta)
        self.assertAlmostEqual(v_r, 0)
        self.assertAlmostEqual(v_theta, v_x)

        theta = pi / 4
        v_x = 10
        v_z = 0
        v_r, v_theta = cartesian_2_spherical_vector(v_x, v_z, theta)
        self.assertAlmostEqual(v_r, v_x * sqrt(2) / 2)
        self.assertAlmostEqual(v_theta, v_x * sqrt(2) / 2)

        theta = pi / 2
        v_x = 10
        v_z = 0
        v_r, v_theta = cartesian_2_spherical_vector(v_x, v_z, theta)
        self.assertAlmostEqual(v_r, v_x)
        self.assertAlmostEqual(v_theta, 0)

        theta = 0
        v_x = 0
        v_z = 10
        v_r, v_theta = cartesian_2_spherical_vector(v_x, v_z, theta)
        self.assertAlmostEqual(v_r, v_z)
        self.assertAlmostEqual(v_theta, 0)

        theta = pi / 4
        v_x = 0
        v_z = 10
        v_r, v_theta = cartesian_2_spherical_vector(v_x, v_z, theta)
        self.assertAlmostEqual(v_r, v_z * sqrt(2) / 2)
        self.assertAlmostEqual(v_theta, -v_z * sqrt(2) / 2)

        theta = pi / 2
        v_x = 0
        v_z = 10
        v_r, v_theta = cartesian_2_spherical_vector(v_x, v_z, theta)
        self.assertAlmostEqual(v_r, 0)
        self.assertAlmostEqual(v_theta, -v_z)

        theta = 0
        v_x = 10
        v_z = 10
        speed = np.hypot(v_x, v_z)
        v_r, v_theta = cartesian_2_spherical_vector(v_x, v_z, theta)
        self.assertAlmostEqual(v_r, speed * sqrt(2) / 2)
        self.assertAlmostEqual(v_theta, speed * sqrt(2) / 2)

    # -------------------------------------------------------------------------
    # Integration
    # -------------------------------------------------------------------------

    def test_integrate(self):
        def func(x):
            return sin(x)**2

        self.assertAlmostEqual(integrate(func, 0, 2 * pi)[0], pi)
        self.assertAlmostEqual(integrate(func, 0, 2 * pi, 1e-12)[0], pi)

        def func(x):
            return -2 * x + 1

        self.assertAlmostEqual(integrate(func, 0, 2)[0], -2)
        self.assertAlmostEqual(integrate(func, -2, 1 / 2)[0], 6.25)
        self.assertAlmostEqual(integrate(func, -2, 1 / 2, 1e-12)[0], 6.25)

    def test_integrate_osc(self):

        def h1_0(z):
            return Bf.hankelh1(0, k_v * z).real

        def h1_1(z):
            return Bf.hankelh1(1, k_v * z).real

        def h1_2(z):
            return Bf.hankelh1(2, k_v * z).real

        def h1_3(z):
            return Bf.hankelh1(3, k_v * z).real

        def j1_0(z):
            return Bf.besselj(0, k_v * z).real

        def j1_1(z):
            return Bf.besselj(1, k_v * z).real

        def j1_2(z):
            return Bf.besselj(2, k_v * z).real

        def j1_3(z):
            return Bf.besselj(3, k_v * z).real

        # Parameters
        R0 = 8e-6
        lambda_v = 30e-6
        delta = 50e-6
        x1 = R0
        x2 = R0 + 20 * delta
        k_v = 2 * pi / lambda_v + 1j / delta

        # Zeroth Order Bessel and Hankel
        self.assertAlmostEqual(
            integrate_osc(h1_0, x1, x2, delta, lambda_v)[0],
            8.37973712155099e-7, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(h1_1, x1, x2, delta, lambda_v)[0],
            2.397545981955677e-6, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(h1_2, x1, x2, delta, lambda_v)[0],
            2.219617723321184e-6, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(h1_3, x1, x2, delta, lambda_v)[0],
            4.026448321970975e-7, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(j1_0, x1, x2, delta, lambda_v)[0],
            4.38223531947702, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(j1_1, x1, x2, delta, lambda_v)[0],
            4.659233107792744, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(j1_2, x1, x2, delta, lambda_v)[0],
            -4.310991826110144, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(j1_3, x1, x2, delta, lambda_v)[0],
            -4.750479141883805, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(h1_0, x1, x2, delta)[0],
            8.37973712155099e-7, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(h1_1, x1, x2, delta)[0],
            2.397545981955677e-6, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(h1_2, x1, x2, delta)[0],
            2.219617723321184e-6, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(h1_3, x1, x2, delta)[0],
            4.026448321970975e-7, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(j1_0, x1, x2, delta)[0],
            4.38223531947702, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(j1_1, x1, x2, delta)[0],
            4.659233107792744, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(j1_2, x1, x2, delta)[0],
            -4.310991826110144, threshold=1e-7,
        )
        self.assertAlmostEqual(
            integrate_osc(j1_3, x1, x2, delta)[0],
            -4.750479141883805, threshold=1e-7,
        )

    # -------------------------------------------------------------------------
    # Clebsch Gordan
    # -------------------------------------------------------------------------

    def test_clebsch_gordan(self):
        def random_value():
            return np.random.randint(0, 4)
        nbr_nonzero = 0

        # Test function for int values

        while nbr_nonzero < 20:
            j1 = random_value()
            j2 = random_value()
            m1 = random_value()
            m2 = random_value()
            j = random_value()
            m = random_value()

            result = cg(j1, m1, j2, m2, j, m)

            self.assertAlmostEqual(
                result,
                float(CG(j1, m1, j2, m2, j, m).doit()),
            )

            if result != 0:
                nbr_nonzero += 1

        # Test errors for non int inputs
        numbers = [1.5, 1, 1, 1, 1, 1]

        for i in np.arange(6):
            j = numbers[i % 6]
            j1 = numbers[(i + 1) % 6]
            j2 = numbers[(i + 2) % 6]
            m = numbers[(i + 3) % 6]
            m1 = numbers[(i + 4) % 6]
            m2 = numbers[(i + 5) % 6]

        self.assertRaises(ValueError, cg, j1, m1, j2, m2, j, m)

    # -------------------------------------------------------------------------
    # Legendre Polynomials
    # -------------------------------------------------------------------------

    def test_legendre(self):

        # first_legendre_cos_poly
        def tmp(theta, coefficients):
            out = 0
            for n, c in enumerate(coefficients):
                out += c * lpmv(1, n, cos(theta))
            return out

        for _ in np.arange(10):
            theta = 2 * pi * np.random.rand()
            coefficients = np.random.rand(10) + 1j * np.random.rand(10)
            n = np.random.randint(0, 5)

            # Test Monomial
            # legendre_cos_monomial
            self.assertEqual(
                Leg.cos_monomial(n, theta, coefficients[0]),
                coefficients[0] * lpmv(0, n, cos(theta)),
            )

            # first_legendre_cos_monomial
            self.assertEqual(
                Leg.first_cos_monomial(n, theta, coefficients[0]),
                coefficients[0] * lpmv(1, n, cos(theta)),
            )

            # Test Polynomials
            theta = 2 * pi * np.random.rand(5)
            for index, th in enumerate(theta):
                # legendre_cos_poly
                self.assertEqual(
                    Leg.cos_poly(theta, coefficients)[index],
                    np.polynomial.legendre.legval(
                        cos(th),
                        coefficients,
                    ),
                )
                # legendre_first_cos_poly
                self.assertAlmostEqual(
                    Leg.first_cos_poly(theta, coefficients)[index],
                    tmp(th, coefficients),
                )

    # -------------------------------------------------------------------------
    # Exponential Integral
    # -------------------------------------------------------------------------

    def test_xexpexp1(self):

        def compare_function(z: complex, N: int = 20):
            if z.real > 20:
                out = 0
                for n in full_range(N):
                    out += factorial(n) / (-z) ** n
                return out
            else:
                return z * exp(z) * exp1(z)

        for x in np.linspace(1, 100, 10):
            z1 = x * (1 + 1j)
            z2 = -1j * z1
            z3 = z1 + z2
            self.assertAlmostEqual(xexpexp1(z1), compare_function(z1))
            self.assertAlmostEqual(xexpexp1(z2), compare_function(z2))
            self.assertAlmostEqual(xexpexp1(z3), compare_function(z3))

    def _assert_equal_complex(self, z1, z2):
        threshold = 1e-8 * np.abs(z2[0])

        self.assertTrue(np.abs(np.real(z1[0]) - np.real(z2[0])) < threshold)
        self.assertTrue(np.abs(np.imag(z1[0]) - np.imag(z2[0])) < threshold)


if __name__ == '__main__':
    unittest.main()
