from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.text import Annotation

from osaft.core.functions import pi
from osaft.plotting.datacontainers.wireframe_datacontainer import DeformedLine
from osaft.plotting.scattering.base_plotter import BaseScatteringPlotter


class WireframePlotter(BaseScatteringPlotter):
    """Plotter class for wireframe plot of the particle
    """

    def __init__(self) -> None:
        """Constructor method"""
        super().__init__(particle=True)

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def plot(
        self,
        deformed_radii: list[DeformedLine],
        deformed_circles: list[DeformedLine],
        phase: float = 0,
        ax: Optional[plt.Axes] = None,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Plot wireframe

        :param deformed_radii: deformed line object, radii
        :param deformed_circles: deformed line object, circles
        :param phase: phase
        :param ax: matplotlib Axes object
        """
        # Create figure and axis
        fig, ax = self._create_figure(ax)

        # Loop through circles
        for circle in deformed_circles:
            self._plot_line(ax, circle, phase)

        # Loop through radii
        for radius in deformed_radii:
            self._plot_line(ax, radius, phase)

        # Finalize plot
        radius = self._get_radius(deformed_radii)
        self._set_ticks(ax, radius)
        self._add_labels(ax)

        return fig, ax

    def animate(
        self,
        frames: int,
        interval: float,
        deformed_radii: list[DeformedLine],
        deformed_circles: list[DeformedLine],
        ax: Optional[plt.Axes] = None,
    ) -> FuncAnimation:
        """Animate wireframe

        :param frames: number of frames
        :param interval: interval between frames in ms
        :param deformed_radii: deformed line object, radii
        :param deformed_circles: deformed line object, circles
        :param ax: axes object
        """
        # Create figure and axis
        fig, ax = self._create_figure(ax)

        # Lists of lines
        list_plot_lines = []
        list_data_lines = deformed_circles + deformed_radii

        # Loop through circles and radii
        for circle in deformed_circles:
            _, line_def = self._plot_line(ax, circle, phase=0)
            list_plot_lines.append(line_def)
        for radius in deformed_radii:
            _, line_ref = self._plot_line(ax, radius, phase=0)
            list_plot_lines.append(line_ref)

        # Finalize plot
        radius = self._get_radius(deformed_radii)
        self._set_ticks(ax, radius)
        self._add_labels(ax)
        annotation = self._annotate_phase(ax, 0)

        anim = FuncAnimation(
            fig, self._animation_func,
            frames=frames,
            interval=interval,
            blit=False,
            fargs=(frames, list_data_lines, list_plot_lines, annotation),
        )

        return anim

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_radius(deformed_radii: list[DeformedLine]) -> float:
        return np.max(deformed_radii[0].get_reference()[1])

    @staticmethod
    def _plot_line(
        ax: Optional[plt.Axes],
        deformed_line: DeformedLine,
        phase: float,
    ) -> tuple[Line2D, Line2D]:

        # Plot Reference Configuration
        x_ref, y_ref = deformed_line.get_reference()
        x_ref_sym = np.concatenate([x_ref, -x_ref])
        y_ref_sym = np.concatenate([y_ref, y_ref])
        line_ref, = ax.plot(
            y_ref_sym, x_ref_sym, alpha=0.5, color='grey',
            zorder=1,
        )

        # Deformed points
        x_def, y_def = deformed_line.get_deformed(phase)
        x_def_sym = np.concatenate([np.flip(x_def), -x_def])
        y_def_sym = np.concatenate([np.flip(y_def), y_def])

        # Plot Deformed Configuration
        line_def, = ax.plot(y_def_sym, x_def_sym, color='blue', lw=0.5)

        return line_ref, line_def

    def _animation_func(
        self,
        frame: int,
        n_frames: int,
        deformed_lines: list,
        plot_lines: list,
        annotation: Annotation,
    ):
        phase = frame / n_frames * 2 * pi
        for index, (data, line) in enumerate(zip(deformed_lines, plot_lines)):
            x, y = data.get_deformed(phase)
            x_def_sym = np.concatenate([np.flip(x), -x])
            y_def_sym = np.concatenate([np.flip(y), y])

            line.set_data(y_def_sym, x_def_sym)

        # Update phase annotation
        self._update_phase_annotation(annotation, phase)

        return plot_lines


if __name__ == '__main__':
    pass
