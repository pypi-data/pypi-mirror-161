import inspect
import unittest

from matplotlib import pyplot as plt
from plotting.scattering.setup_test_scattering import BaseTestScattering

from osaft import FluidScatteringPlot


class TestFluidScattering(BaseTestScattering):

    def setUp(self) -> None:

        super().setUp()

        r_max = 5 * self.R_0
        self.fluid_plot = FluidScatteringPlot(
            self.yosioka, r_max=r_max,
        )

    def test_tripcolor_symmetric(self):
        fig, ax = self.fluid_plot.plot(
            tripcolor=True,
            inst=False,
            mode=None,
            phase=0,
            symmetric=True,
            incident=True,
            scattered=True,
        )
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_tripcolor_not_symmetric(self):
        fig, ax = self.fluid_plot.plot(
            tripcolor=True,
            inst=False,
            mode=None,
            phase=0,
            symmetric=False,
            incident=True,
            scattered=True,
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_tricontourf(self):
        fig, ax = self.fluid_plot.plot(
            inst=True,
            mode=1,
            phase=0,
            symmetric=True,
            incident=False,
            scattered=True,
        )
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_animation_tricontourf(self):
        anim = self.fluid_plot.animate(
            frames=10,
            interval=100,
            symmetric=True,
            scattered=False,
            incident=True,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_animation_tripcolor(self):
        anim = self.fluid_plot.animate(
            tripcolor=True,
            frames=10,
            interval=100,
            symmetric=True,
            scattered=True,
            incident=True,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_animation_tricontourf_not_symmetric(self):
        anim = self.fluid_plot.animate(
            frames=10,
            interval=100,
            symmetric=False,
            scattered=False,
            incident=True,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_animation_tripcolor_not_symmetric(self):
        anim = self.fluid_plot.animate(
            tripcolor=True,
            frames=10,
            interval=100,
            symmetric=False,
            scattered=True,
            incident=True,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_evolution_tricontourf(self):
        fig, ax = self.fluid_plot.plot_evolution(
            symmetric=True,
            scattered=True,
            incident=False,
            mode=1,
        )
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_evolution_tripcolor(self):
        fig, ax = self.fluid_plot.plot_evolution(
            symmetric=True,
            scattered=True,
            incident=False,
            mode=None,
            tripcolor=True,
        )
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)


if __name__ == '__main__':
    unittest.main()
