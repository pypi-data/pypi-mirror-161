import inspect
import unittest

import numpy as np
from matplotlib import pyplot as plt

from osaft import ARFPlot, WaveType, gorkov1962, king1934, yosioka1955
from osaft.solutions.base_arf import BaseARF
from osaft.tests.basetest_plotting import BaseTestPlotting


def create_solutions() -> list[BaseARF]:
    f = 1e6
    R_0 = 1e-6
    rho_s = 1850
    c_s = 5000
    rho_f = 997
    c_f = 1500
    p_0 = 1e5
    wave_types = WaveType.TRAVELLING
    position = None

    out = []
    out.append(
        king1934.ARF(
            f, R_0,
            rho_s,
            rho_f, c_f,
            p_0, wave_types, position,
        ),
    )

    out.append(
        yosioka1955.ARF(
            f, R_0,
            rho_s, c_s,
            rho_f, c_f,
            p_0, wave_types, position,
        ),
    )

    out.append(
        gorkov1962.ARF(
            f, R_0,
            rho_s, c_s,
            rho_f, c_f,
            p_0, wave_types, position,
        ),
    )

    return out


class TestARFPlot(BaseTestPlotting):

    def setUp(self) -> None:
        super().setUp()

        self.plotter = ARFPlot()

    def test_name_error(self) -> None:
        solutions = create_solutions()
        for sol in solutions:
            self.plotter.add_solutions(sol)
            self.assertRaises(ValueError, self.plotter.add_solutions, sol)

    def test_error_add_zero_solutions(self) -> None:
        self.assertRaises(TypeError, self.plotter.add_solutions)

    def test_add_multiple_solutions(self):
        solutions = create_solutions()
        self.plotter.add_solutions(*solutions)

        # Test if solutions are inside
        for sol in solutions:
            self.assertTrue(sol.name in self.plotter._solutions.keys())

    def test_modulo_in_linestyles(self) -> None:
        solutions = create_solutions()
        for i in np.arange(6):
            for sol in solutions:
                tmp = sol
                tmp.name = f'{tmp.name}_{i}'
                self.plotter.add_solutions(tmp)

        self.plotter.set_abscissa(np.linspace(1e-6, 1e-5), 'R_0')

        fig, ax = self.plotter.plot_solutions()

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_add_and_remove_solutions(self) -> None:
        solutions = create_solutions()
        for sol in solutions:
            self.plotter.add_solutions(sol)
        self.plotter.remove_solution(solutions[1])

    def test_repeated_ARF_over_R(self) -> None:
        solutions = create_solutions()

        self.plotter.set_abscissa(np.linspace(1e-6, 1e-5), 'R_0')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions()
        fig, ax = self.plotter.plot_solutions()

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_ARF_over_R(self) -> None:
        solutions = create_solutions()

        self.plotter.set_abscissa(np.linspace(1e-6, 1e-5, num=100), 'R_0')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions()

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_normARF_over_f(self) -> None:
        solutions = create_solutions()

        self.plotter.set_abscissa(np.linspace(1e4, 5e6, num=100), 'f')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions(
            normalization=solutions[1].name,
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_normARF_over_f_semilogx(self) -> None:
        solutions = create_solutions()

        self.plotter.set_abscissa(np.linspace(1e4, 5e6, num=100), 'f')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions(
            normalization=solutions[1].name,
            plot_method=plt.semilogx,
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_normARF_over_f_loglog(self) -> None:
        solutions = create_solutions()

        self.plotter.set_abscissa(np.linspace(1e4, 5e6, num=100), 'f')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions(
            normalization=solutions[1].name,
            plot_method=plt.loglog,
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_max_norm_over_f(self):
        solutions = create_solutions()

        self.plotter.set_abscissa(np.linspace(1e4, 5e6, num=100), 'f')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions(
            normalization='max',
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)


class DummyClass(BaseARF):
    """Dummy class to test methods
    """
    name = 'Dummy'
    R_0 = 1

    def compute_arf(self):
        return 2 * self.R_0


class TestARFNormalization(unittest.TestCase):

    def setUp(self) -> None:

        self.cls = DummyClass()
        self.R_values = np.arange(1, 10)

        self.arf_plot = ARFPlot('R_0', self.R_values)
        self.arf_plot.add_solutions(self.cls)

    def test_display_values(self):

        x_values = np.linspace(0, 1, len(self.R_values))
        _, ax = self.arf_plot.plot_solutions(display_values=x_values)
        abscissa = ax.lines[0].get_xdata()
        np.testing.assert_array_equal(x_values, abscissa)

    def test_max_norm(self) -> None:

        _, ax = self.arf_plot.plot_solutions(normalization='max')
        arf = ax.lines[0].get_ydata()
        self.assertAlmostEqual(max(arf), 1)
        self.assertTrue(np.all(arf <= 1))

    def test_other_class_norm(self):
        norm = 'Dummy'
        _, ax = self.arf_plot.plot_solutions(normalization=norm)
        arf = ax.lines[0].get_ydata()
        self.assertAlmostEqual(max(arf), 1)

    def test_float_norm(self) -> None:

        norm = 5
        _, ax = self.arf_plot.plot_solutions(normalization=norm)
        arf = ax.lines[0].get_ydata()
        np.testing.assert_array_equal(2 * self.R_values / 5, arf)

    def test_array_norm(self) -> None:

        norm = np.arange(1, 10)
        _, ax = self.arf_plot.plot_solutions(normalization=norm)
        arf = ax.lines[0].get_ydata()
        np.testing.assert_array_equal(2 * np.ones(len(norm)), arf)

    def test_callable_norm(self) -> None:
        def norm(R_0):
            return 2 * R_0

        _, ax = self.arf_plot.plot_solutions(normalization=norm)
        arf = ax.lines[0].get_ydata()
        np.testing.assert_array_equal(np.ones(len(self.R_values)), arf)

    def test_wrong_norm(self):
        self.assertRaises(
            ValueError, self.arf_plot.plot_solutions,
            normalization='blabla',
        )


class TestMulticore(unittest.TestCase):

    def test_multicore(self):

        king, _, _ = create_solutions()
        king_copy = king.copy()
        king_copy.name = 'King Copy'

        plot = ARFPlot('R_0', np.linspace(1e-6, 10e6))
        plot.add_solutions(king)
        plot.add_solutions(king_copy, multicore=True)

        fig, ax = plot.plot_solutions()

        arf_king = ax.lines[0].get_ydata()
        arf_king_copy = ax.lines[0].get_ydata()

        np.testing.assert_array_equal(arf_king, arf_king_copy)


if __name__ == '__main__':
    unittest.main()
