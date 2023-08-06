from abc import ABC
from typing import Optional, Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from matplotlib.text import Annotation

from osaft.core.functions import pi, sqrt
from osaft.plotting.base_plotting import BasePlot

plt.style.use('seaborn-muted')


class BaseScatteringPlotter(BasePlot, ABC):
    """Base class for plotting first order solutions such as the acoustic
    scattering fields and particle vibrations.

    :param particle: if `True`, plot of the particle, else plot of the fluid
    """

    def __init__(
        self,
        particle: bool,
    ) -> None:
        """ Constructor method
        """
        # Option if particle plot
        self.particle = particle

    # -------------------------------------------------------------------------
    # Figure handling
    # -------------------------------------------------------------------------

    def _create_figure(
        self,
        ax: plt.Axes,
    ) -> [Union[None, plt.Figure], plt.Axes]:
        """
        Creates a matplotlib Figure instance and a matplotlib Axes instance and
        sets the aspect ratio to 1.
        If `ax` is passed no new instances are created and only the aspect
        ratio is set.

        :param ax: axes
        """
        fig, ax = super()._create_figure(ax)
        ax.set_aspect('equal', 'box')
        ax.grid(False)
        return fig, ax

    # -------------------------------------------------------------------------
    # Post processing
    # -------------------------------------------------------------------------

    def _finish_plot(
        self,
        ax: plt.Axes,
        radius: float,
        xmax: Optional[float] = None,
    ):
        """Post processes the plot
        Adds labels and ticks to the plot

        :param ax: axes
        :param radius: radius of the particle
        :param xmax: max value for plotting range
        """
        self._add_labels(ax)
        self._set_ticks(ax, radius)

    # ------------------------------------------------------------------------
    # Adding Artists and Annotations
    # -------------------------------------------------------------------------

    @staticmethod
    def _annotate_phase(ax: plt.Axes, phase: float) -> Annotation:
        """Annotates the phase to the axes

        Phase is annotated to the top right corner of the axes.

        :param ax: Axes object
        :param phase: phase
        """
        phase_by_pi = phase / pi
        txt = f'$\\varphi = {phase_by_pi:.2f}\\pi $'
        annotation = ax.annotate(
            txt, xy=(0.8, 0.94),
            xycoords='axes fraction', bbox=dict(
                boxstyle='square,pad=0.3', fc='white',
            ),
        )
        return annotation

    @staticmethod
    def _update_phase_annotation(
        annotation: Annotation, phase: float,
    ) -> Annotation:
        """Updates the phase

        :param annotation: Annotation object
        :param phase: phase
        """
        phase_by_pi = phase / pi
        txt = f'$\\varphi = {phase_by_pi:.2f}\\pi $'
        annotation.set_text(txt)
        return annotation

    @staticmethod
    def _add_circle(
        ax: plt.Axes,
        radius: float,
        linewidth: float = 0.5,
        fill: bool = False,
    ) -> None:
        """Draws the particle in the plot

        :param ax: axes
        :param radius: particle
        :param linewidth: linewidth
        :param fill: fill the circle
        """
        circle = Circle(
            (0, 0), radius=radius,
            linewidth=linewidth, fill=fill, color='white',
        )
        ax.add_artist(circle)

    # -------------------------------------------------------------------------
    # Labels and Ticks
    # -------------------------------------------------------------------------

    @staticmethod
    def _add_labels(ax: plt.Axes) -> None:
        """Adds axis labels to plot

        :param ax: axes
        """
        ax.set_xlabel('$z/R_0$ [-]')
        ax.set_ylabel('$x/R_0$ [-]')

    def _set_ticks(
        self,
        ax: plt.Axes,
        radius: float,
    ) -> None:
        """Sets ticks in plot

        :param ax: axes
        :param radius: particle radius
        """
        # Get ticks
        if self.particle:
            ticks, tick_labels = self._get_particle_ticks(radius)
        else:
            ticks, tick_labels = self._get_fluid_ticks(ax, radius)

        # Set ticks and labels
        ax.set_xticks(ticks, labels=tick_labels, minor=False)
        ax.set_yticks(ticks, labels=tick_labels, minor=False)

    @staticmethod
    def _get_fluid_ticks(
        ax: plt.Axes,
        radius: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Sets ticks for a plot of the fluid

        :param radius: particle radius
        """
        # Compute ticks
        _, xmax = ax.get_xlim()
        right_radius = round(xmax / sqrt(2) / radius)
        range_radii = np.linspace(0, right_radius + 1, 3)
        pos_tick_labels = [round(label, 1) for label in range_radii]
        neg_tick_labels = [-label for label in pos_tick_labels if label != 0]
        tick_labels = np.array(pos_tick_labels + neg_tick_labels)
        ticks = tick_labels * radius
        return ticks, tick_labels

    @staticmethod
    def _get_particle_ticks(
        radius: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Returns the ticks

        :param radius: particle radius
        """
        tick_labels = np.array([-1, -0.5, 0, 0.5, 1])
        ticks = tick_labels * radius
        return ticks, tick_labels

    @staticmethod
    def _set_labels(self, ax: plt.Axes):
        ax.set_xlabel('$z/R_0$')
        ax.set_ylabel('$x/R_0$')


if __name__ == '__main__':
    pass
