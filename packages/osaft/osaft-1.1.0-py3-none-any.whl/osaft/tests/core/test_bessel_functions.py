import unittest

import numpy as np
from scipy.special import hankel1, hankel2, jv, yv

from osaft.core.functions import BesselFunctions as Bf
from osaft.core.functions import pi, sqrt
from osaft.tests.basetest import NumericTestCase


class TestBesselFunctions(NumericTestCase):

    def setUp(self) -> None:

        self.rng = np.random.default_rng()

    def test_besselj_and_derivatives(self):
        def j(n, z):
            return sqrt(pi / 2 / z) * jv(n + 0.5, z)

        for n in self.rng.integers(0, 10, size=10):
            for _ in np.arange(10):
                z = self.random_z()
                self.assertAlmostEqual(j(n, z), Bf.besselj(n, z), 1e-9)
                self.assertAlmostEqual(
                    self._df(j, n, z), Bf.d1_besselj(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d2f(j, n, z), Bf.d2_besselj(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d3f(j, n, z), Bf.d3_besselj(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d4f(j, n, z), Bf.d4_besselj(n, z), 1e-9,
                )

        n = 0
        self.assertAlmostEqual(
            self._df(j, n, z), Bf.d1_besselj(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d2f(j, n, z), Bf.d2_besselj(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d3f(j, n, z), Bf.d3_besselj(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d4f(j, n, z), Bf.d4_besselj(n, z), 1e-9,
        )

    def test_bessely_and_derivatives(self):
        def y(n, z):
            return sqrt(pi / 2 / z) * yv(n + 0.5, z)

        for n in self.rng.integers(0, 10, size=10):
            for _ in np.arange(10):
                z = self.random_z()
                self.assertAlmostEqual(y(n, z), Bf.bessely(n, z), 1e-9)
                self.assertAlmostEqual(
                    self._df(y, n, z), Bf.d1_bessely(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d2f(y, n, z), Bf.d2_bessely(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d3f(y, n, z), Bf.d3_bessely(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d4f(y, n, z), Bf.d4_bessely(n, z), 1e-9,
                )

        n = 0
        self.assertAlmostEqual(
            self._df(y, n, z), Bf.d1_bessely(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d2f(y, n, z), Bf.d2_bessely(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d3f(y, n, z), Bf.d3_bessely(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d4f(y, n, z), Bf.d4_bessely(n, z), 1e-9,
        )

    def test_hankelh1_and_derivatives(self):
        def h1(n, z):
            return sqrt(pi / z / 2) * hankel1(n + 0.5, z)

        for n in self.rng.integers(0, 10, size=10):
            for _ in np.arange(10):
                z = self.random_z()
                self.assertAlmostEqual(h1(n, z), Bf.hankelh1(n, z))
                self.assertAlmostEqual(
                    self._df(h1, n, z), Bf.d1_hankelh1(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d2f(h1, n, z), Bf.d2_hankelh1(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d3f(h1, n, z), Bf.d3_hankelh1(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d4f(h1, n, z), Bf.d4_hankelh1(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d5f(h1, n, z), Bf.d5_hankelh1(n, z), 1e-9,
                )

        n = 0
        self.assertAlmostEqual(
            self._df(h1, n, z), Bf.d1_hankelh1(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d2f(h1, n, z), Bf.d2_hankelh1(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d3f(h1, n, z), Bf.d3_hankelh1(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d4f(h1, n, z), Bf.d4_hankelh1(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d5f(h1, n, z), Bf.d5_hankelh1(n, z), 1e-9,
        )

    def test_hankelh2_and_derivatives(self):
        def h2(n, z):
            return sqrt(pi / z / 2) * hankel2(n + 0.5, z)

        for n in self.rng.integers(0, 10, size=10):
            for _ in np.arange(10):
                z = self.random_z()
                self.assertAlmostEqual(h2(n, z), Bf.hankelh2(n, z), 1e-9)
                self.assertAlmostEqual(
                    self._df(h2, n, z), Bf.d1_hankelh2(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d2f(h2, n, z), Bf.d2_hankelh2(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d3f(h2, n, z), Bf.d3_hankelh2(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d4f(h2, n, z), Bf.d4_hankelh2(n, z), 1e-9,
                )
                self.assertAlmostEqual(
                    self._d5f(h2, n, z), Bf.d5_hankelh2(n, z), 1e-9,
                )

        n = 0
        self.assertAlmostEqual(
            self._df(h2, n, z), Bf.d1_hankelh2(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d2f(h2, n, z), Bf.d2_hankelh2(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d3f(h2, n, z), Bf.d3_hankelh2(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d4f(h2, n, z), Bf.d4_hankelh2(n, z), 1e-9,
        )
        self.assertAlmostEqual(
            self._d5f(h2, n, z), Bf.d5_hankelh2(n, z), 1e-9,
        )

    def test_adaptive_derivative(self):
        def j(n, z):
            return sqrt(pi / 2 / z) * jv(n + 0.5, z)

        def y(n, z):
            return sqrt(pi / 2 / z) * yv(n + 0.5, z)

        def h1(n, z):
            return sqrt(pi / z / 2) * hankel1(n + 0.5, z)

        def h2(n, z):
            return sqrt(pi / z / 2) * hankel2(n + 0.5, z)

        dfdzs = [self._df, self._d2f, self._d3f, self._d4f, self._d5f]

        for n in self.rng.integers(0, 10, size=10):
            for _ in np.arange(10):
                z = self.random_z()
                for i, df in enumerate(dfdzs, start=1):
                    self.assertAlmostEqual(
                        df(j, n, z), Bf.adaptive_derivative_besselj(n, z, i),
                        1e-9,
                    )
                    self.assertAlmostEqual(
                        df(y, n, z), Bf.adaptive_derivative_bessely(n, z, i),
                        1e-9,
                    )
                    self.assertAlmostEqual(
                        df(h1, n, z), Bf.adaptive_derivative_hankelh1(n, z, i),
                        1e-9,
                    )
                    self.assertAlmostEqual(
                        df(h2, n, z), Bf.adaptive_derivative_hankelh2(n, z, i),
                        1e-9,
                    )

        n = 0
        for i, df in enumerate(dfdzs, start=1):
            self.assertAlmostEqual(
                df(j, n, z), Bf.adaptive_derivative_besselj(n, z, i), 1e-9,
            )
            self.assertAlmostEqual(
                df(y, n, z), Bf.adaptive_derivative_bessely(n, z, i), 1e-9,
            )
            self.assertAlmostEqual(
                df(h1, n, z), Bf.adaptive_derivative_hankelh1(n, z, i), 1e-9,
            )
            self.assertAlmostEqual(
                df(h2, n, z), Bf.adaptive_derivative_hankelh2(n, z, i), 1e-9,
            )

    # -------------------------------------------------------------------------
    # Helper
    # -------------------------------------------------------------------------

    @staticmethod
    def _df(func, n, z):
        out = -func(n + 1, z) + (n / z) * func(n, z)
        return out

    @classmethod
    def _d2f(cls, func, n, z):
        out = -cls._df(func, n + 1, z)
        out -= n / z**2 * func(n, z)
        out += n / z * cls._df(func, n, z)
        return out

    @classmethod
    def _d3f(cls, func, n, z):
        out = -cls._d2f(func, n + 1, z)
        out += 2 * n / z**3 * func(n, z)
        out -= n / z**2 * cls._df(func, n, z)
        out -= n / z**2 * cls._df(func, n, z)
        out += n / z * cls._d2f(func, n, z)
        return out

    @classmethod
    def _d4f(cls, func, n, z):
        out = -cls._d3f(func, n + 1, z)
        out -= 6 * n / z**4 * func(n, z)
        out += 3 * 2 * n / z**3 * cls._df(func, n, z)
        out -= 3 * n / z**2 * cls._d2f(func, n, z)
        out += n / z * cls._d3f(func, n, z)
        return out

    @classmethod
    def _d5f(cls, func, n, z):
        out = -cls._d4f(func, n + 1, z)
        out += 24 * n / z**5 * func(n, z)
        out -= 24 * n / z**4 * cls._df(func, n, z)
        out += 12 * n / z**3 * cls._d2f(func, n, z)
        out -= 4 * n / z**2 * cls._d3f(func, n, z)
        out += n / z * cls._d4f(func, n, z)
        return out


if __name__ == '__main__':
    unittest.main()
