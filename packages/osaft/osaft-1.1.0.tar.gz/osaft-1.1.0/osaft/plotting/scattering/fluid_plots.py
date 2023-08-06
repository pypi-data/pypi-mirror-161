from typing import Optional, Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from osaft.core.functions import pi, sqrt
from osaft.plotting.datacontainers.scattering_datacontainer import (
    FluidScatteringData,
)
from osaft.plotting.scattering.tri_plotter import TriangulationPlotter
from osaft.solutions.base_scattering import BaseScattering


class FluidScatteringPlot:
    """Class for plotting scattering field of the fluid

    Plots the acoustic field inside the particle using Matplotlib
    tricontourf or tripcolor plotting methods.

    :param sol: solution to be plotted
    :param r_max: radial limit of plot range
    :param theta_min: lower limit for tangential plot range
    :param theta_max: upper limit for tangential plot range
    :param resolution: if tuple (radial resolution, tangential resolution)
    :param cmap: color map
    """
    def __init__(
            self,
            sol: BaseScattering,
            r_max: float,
            theta_min: float = 0,
            theta_max: float = pi,
            resolution: Union[int, tuple[int, int]] = 100,
            cmap: str = 'winter',
    ):
        """Constructor method
        """
        self.data = FluidScatteringData(
            sol, sqrt(2) * r_max, theta_min,
            theta_max,
            res=resolution,
        )
        self.plotter = TriangulationPlotter(False, cmap)

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def plot(
            self,
            inst: bool = True,
            phase: float = 0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Tricontourf plot for acoustic velocity field of the fluid

        Plots the velocity amplitude of the first-order acoustic velocity field
        of the fluid using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`

        :param inst: if `True` instantaneous amplitude is plotted
        :param phase: phase [0, 2 * pi]
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        return self._triangulation_plot(
            tripcolor=tripcolor,
            inst=inst,
            phase=phase,
            mode=mode,
            scattered=scattered,
            incident=incident,
            symmetric=symmetric,
            ax=ax,
            **kwargs
        )

    def animate(
            self,
            frames: int = 64,
            interval: float = 100.0,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> FuncAnimation:
        """Tricontourf animation for acoustic velocity field of the fluid

        Animates the velocity amplitude of the first-order acoustic velocity
        field of the fluid over one period using Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`

        :param frames: number of frames for the animation
        :param interval: interval between frames in ms
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        return self._triangulation_animation(
            tripcolor=tripcolor,
            frames=frames,
            interval=interval,
            mode=mode,
            scattered=scattered,
            incident=incident,
            symmetric=symmetric,
            ax=ax,
            **kwargs,
        )

    def plot_evolution(
            self,
            inst: bool = True,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            tripcolor: bool = False,
            layout: tuple[int, int] = (3, 3),
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Tricontourf for acoustic velocity field evolution of the fluid

        Plots the velocity amplitude of the first-order acoustic velocity
        field of the fluid over one period at different phases using
        Matplotlib's
        `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontour.html>`_
        or
        `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        if `tripcolor = True`.

        The first phase value is always :math:`0\\pi` and the last one
        :math:`2\\pi`. The total number of plots and, hence, also the steps
        between the different phase values is the defined by the product of the
        ``layout`` tuple.

        :param inst: if `True` instantaneous amplitude is plotted
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param tripcolor: switches between tripcolor and tricontourf plot
        :param layout: number of rows and columns for plotting
        :param kwargs: passed through to the parent subplots command
        """

        n_row, n_col = layout
        n = n_col * n_row

        phases = np.linspace(0, 2, num=n)

        fig, axes = plt.subplots(
            n_row, n_col,
            sharex=True, sharey=True,
            **kwargs,
        )

        # Get velocity norm, needed to make colormap of the right range
        X, Y, C_norm = self.data.get_velocity_magnitude(
            False, mode=mode, scattered=scattered, incident=incident,
        )
        # Only values inside the plotting range
        C_norm = np.where(
            np.hypot(X, Y) < self.data.r_max,
            C_norm, 0,
        )

        for i, phase in enumerate(phases):

            row = i // n_col
            col = i % n_col
            ax = axes.flat[i]

            X, Z, C = self.data.get_velocity_magnitude(
                instantaneous=inst,
                phase=phase * np.pi,
                mode=mode,
                scattered=scattered,
                incident=incident,
            )
            # Color bar label
            cbar_label = 'Acoustic Velocity [m/s]'

            # Plot
            _, _, cnf, cbar, _ = self.plotter.plot(
                X=Z,
                Y=X,
                C=C,
                radius=self.data.sol.R_0,
                symmetric=symmetric,
                tripcolor=tripcolor,
                cbar_label=cbar_label,
                ax=ax,
                vmin=0,
                vmax=1.01 * C_norm.max(),
            )
            # remove colorbar
            cbar.remove()

            ticks = self.data.sol.R_0 * np.asarray([-1, 1])
            labels = [-1, 1]

            ax.set_title(f'{phase:.2f}' + r'$\pi$')

            if row != (n_row - 1):
                ax.set_xlabel('')
            if col > 0:
                ax.set_ylabel('')

            ax.set_xticks(ticks, labels=labels)
            ax.set_yticks(ticks, labels=labels)

            # set aspect ratio to 1:1
            ax.set_aspect(1)

        fig.tight_layout()
        cbar = fig.colorbar(cnf, ax=axes.ravel().tolist())
        cbar_label = 'Acoustic Velocity [m/s]'
        cbar.ax.set_ylabel(cbar_label)

        return fig, axes

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------

    def _triangulation_plot(
            self,
            tripcolor: bool,
            inst: bool,
            phase: float,
            mode: Optional[int],
            scattered: bool,
            incident: bool,
            symmetric: bool,
            ax: Optional[plt.Axes],
            **kwargs,
    ) -> tuple[plt.Figure, plt.Axes]:
        """Helper function for tripcolor/tricontourf plot

        :param tripcolor: if `True` tripcolor, else tricontourf plot
        :param inst: if `True` instantaneous amplitude is plotted
        :param phase: phase [0, 2 * pi]
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param ax: Axes object
        :param kwargs: passed through to plotting method
        """

        # Data
        X, Z, C = self.data.get_velocity_magnitude(
            instantaneous=inst,
            phase=phase,
            mode=mode,
            scattered=scattered,
            incident=incident,
        )
        # Color bar label
        cbar_label = 'Acoustic Velocity [m/s]'

        # Plot
        fig, ax, _, _, _ = self.plotter.plot(
            X=Z,
            Y=X,
            C=C,
            radius=self.data.sol.R_0,
            symmetric=symmetric,
            tripcolor=tripcolor,
            cbar_label=cbar_label,
            ax=ax,
            **kwargs,
        )
        return fig, ax

    def _triangulation_animation(
            self,
            tripcolor: bool,
            frames: int,
            interval: float,
            mode: Optional[int] = None,
            scattered: bool = True,
            incident: bool = True,
            symmetric: bool = True,
            ax: Optional[plt.Axes] = None,
            **kwargs,
    ) -> FuncAnimation:
        """Helper function for tripcolor/tricontourf animation

        :param tripcolor: if `True` tripcolor, else tricontourf plot
        :param frames: number of frames for the animation
        :param interval: interval between frames in ms
        :param mode: mode of oscillation
        :param scattered: if `True` scattering field is plotted
        :param incident: if `True` incident field is plotted
        :param symmetric: if `True` the symmetry of the solution is used
        :param ax: Axes object
        :param kwargs: passed through to tricontourf()
        """
        # Data function for animation
        def data_func(phase: float) -> tuple[
            np.ndarray, np.ndarray,
            np.ndarray,
        ]:
            """Returns the velocity field for given phase
            Closure is used to fix all additional parameters
            :param phase: phase
            """
            return self.data.get_velocity_magnitude(
                True, phase, mode,
                scattered, incident,
            )
        # Color bar label
        cbar_label = 'Acoustic Velocity [m/s]'

        # Get velocity norm, needed to make colormap of the right range
        X, Y, C_norm = self.data.get_velocity_magnitude(
            False, mode=mode, scattered=scattered, incident=incident,
        )
        # Only values inside the plotting range
        C_norm = np.where(
            np.hypot(X, Y) < self.data.r_max,
            C_norm, 0,
        )

        return self.plotter.animate(
            frames=frames,
            interval=interval,
            tripcolor=tripcolor,
            symmetric=symmetric,
            cbar_label=cbar_label,
            data_func=data_func,
            C_norm=C_norm,
            radius=self.data.sol.R_0,
            ax=ax,
            **kwargs
        )


if __name__ == '__main__':
    pass
