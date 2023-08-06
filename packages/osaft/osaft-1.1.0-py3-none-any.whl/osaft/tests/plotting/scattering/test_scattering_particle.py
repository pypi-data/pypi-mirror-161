import inspect
import unittest

from matplotlib import pyplot as plt
from plotting.scattering.setup_test_scattering import BaseTestScattering

from osaft import ParticleScatteringPlot, ParticleWireframePlot


class TestParticleScattering(BaseTestScattering):

    def setUp(self) -> None:
        super().setUp()

        self.particle_plot = ParticleScatteringPlot(
            self.yosioka,
        )

        self.wireframe = ParticleWireframePlot(
            self.yosioka,
            scale_factor=0.1,
        )

    def test_tricontourf(self):
        fig, ax = self.particle_plot.plot(
            inst=True,
            phase=1,
            displacement=True,
            symmetric=True,
        )
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_animation_tripcolor(self):
        anim = self.particle_plot.animate(
            tripcolor=True,
            frames=10,
            interval=100,
            displacement=False,
            mode=None,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_animation_tricontourf(self):
        anim = self.particle_plot.animate(
            frames=10,
            interval=100,
            displacement=True,
            mode=4,
        )
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()

    def test_tripcolor(self):
        fig, ax = self.particle_plot.plot(
            tripcolor=True,
            inst=False,
            phase=1,
            displacement=False,
            symmetric=True,
        )
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_tricontourf_evolution(self):
        fig, ax = self.particle_plot.plot_evolution(
            symmetric=True,
            displacement=True,
            mode=None,
        )
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_evolution_tripcolor(self):
        fig, ax = self.particle_plot.plot_evolution(
            symmetric=True,
            mode=1,
            tripcolor=True,
        )
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_wireframe_plot(self):
        fig, ax = self.wireframe.plot(phase=2)
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_wireframe_evolution(self):
        fig, ax, = self.wireframe.plot_evolution()
        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_wireframe_animation(self):
        anim = self.wireframe.animate(mode=None, frames=10)
        anim.resume()
        plt.show(block=False)
        plt.pause(1)
        plt.close()


if __name__ == '__main__':
    unittest.main()
