from collections.abc import Callable
from typing import Optional

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import tri
from matplotlib.animation import FuncAnimation
from matplotlib.cm import ScalarMappable
from matplotlib.collections import TriMesh
from matplotlib.colorbar import Colorbar
from matplotlib.text import Annotation
from matplotlib.tri import Triangulation
from mpl_toolkits.axes_grid1 import make_axes_locatable

from osaft.core.functions import pi, sqrt
from osaft.plotting.scattering.base_plotter import BaseScatteringPlotter


class TriangulationPlotter(BaseScatteringPlotter):
    """Base class for plotting first order solutions such as the acoustic
    scattering fields and particle vibrations.

    :param particle: if `True`, plot of the particle, else plot of the fluid
    :param cmap: colormap passed to matplotlib
    """

    def __init__(
        self,
        particle: bool,
        cmap: str = 'winter',
    ) -> None:
        """Constructor method
        """
        # Call to parent class
        super().__init__(particle)

        # Color map
        self.cmap = cmap

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------

    def plot(
            self,
            X: np.ndarray,
            Y: np.ndarray,
            C: np.ndarray,
            radius: Optional[float],
            symmetric: bool,
            tripcolor: bool,
            cbar_label: str,
            ax: Optional[plt.Axes],
            **kwargs
    ) -> [
        Optional[plt.Figure], plt.Axes, tri.TriMesh, Optional[Colorbar],
        tri.Triangulation,
    ]:
        """Plot for the scattering field

        Plots the scattering field using `tripcolor
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tripcolor.html>`_
        or `tricontourf
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tricontourf.html>`_
        from Matplotlib.

        :param X: array of x-coordinates
        :param Y: array of y-coordinates
        :param C: array of the values
        :param radius: radius for masked triangulation
        :param symmetric: if true the plot is symmetric w.r.t. the x-axis
        :param tripcolor: if `True` tripcolor plot, if `False` tricontourf plot
        :param cbar_label: label for the color bar
        :param ax: axes
        """
        # Create figure and axis
        fig, ax = self._create_figure(ax)
        # Triangulation
        triang = self.masked_triangulation(X, Y, symmetric, radius)
        # Symmetry
        if symmetric:
            C = np.concatenate([C, C])

        # Plot tripcolor or tricontourf plot
        if tripcolor:
            trc = ax.tripcolor(
                triang, C, cmap=self.cmap, shading='gouraud', **kwargs
            )
        else:
            trc = ax.tricontourf(
                triang, C, cmap=self.cmap, **kwargs
            )

        # Add color bar, axis limits, axis labels, etc.
        cbar = self._finish_triplot(
            fig, ax, radius, trc,
            cbar_label,
        )

        return fig, ax, trc, cbar, triang

    def animate(
        self,
        frames: int,
        interval: float,
        tripcolor: bool,
        symmetric: bool,
        cbar_label: str,
        radius: float,
        data_func: Callable[
            [float],
            tuple[np.ndarray, np.ndarray, np.ndarray],
        ],
        C_norm: np.ndarray,
        ax: Optional[plt.Axes],
        **kwargs,
    ) -> FuncAnimation:
        """Animates tricontourf and tripcolor plot

        :param frames: number of frames
        :param interval: interval between frames in ms
        :param tripcolor: if `True` tripcolor, else tricontourf
        :param symmetric: if the symmetric part of plot shall be plotted
        :param cbar_label: label for the color bar
        :param data_func: function that returns speed for given phase
        :param C_norm: absolute values of the field to be plotted
        :param radius: radius
        :param ax: axes object
        :param kwargs: passed through to tripcolor or tricontourf
        """
        # Get Coordinates
        X, Z, _ = data_func(0)

        # Initial plot
        fig, ax, triplot, _, triang = self.plot(
            Z, X, C_norm, radius, symmetric, tripcolor,
            cbar_label, ax, **kwargs
        )

        # Annotate Phase
        annotation = self._annotate_phase(ax, 0)

        if tripcolor:
            anim = FuncAnimation(
                fig,
                self._animation_func_tripcolor,
                frames=frames,
                interval=interval,
                blit=False,
                fargs=(frames, triplot, annotation, data_func, symmetric),
            )
        else:
            anim = FuncAnimation(
                fig, self._animation_func_tricontourf,
                frames=frames,
                interval=interval,
                blit=False,
                fargs=(
                    frames, ax, triplot, triang, annotation, data_func,
                    symmetric,
                ),
            )

        return anim

    # -------------------------------------------------------------------------
    # Triangulation
    # -------------------------------------------------------------------------

    @staticmethod
    def triangulation(
        X: np.ndarray,
        Y: np.ndarray,
        symmetric: bool,
    ) -> tuple[np.ndarray, np.ndarray, tri.Triangulation]:
        """Creates the triangulation

        Creates triangulation of points with coordinates (X[i], Y[i])

        :param X: array of x-coordinates
        :param Y: array of y-coordinates
        :param symmetric: if true the plot is symmetric w.r.t. the x-axis
        """
        if symmetric:
            X = np.concatenate([X, X])
            Y = np.concatenate([Y, -Y])

        triangs = tri.Triangulation(X, Y)
        return X, Y, triangs

    def masked_triangulation(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        symmetric: bool,
        radius: Optional[float] = None,
    ) -> tri.Triangulation:
        """Creates the masked triangulation

        Creates the masked triangulation of points with coordinates
        (X[i],Y[i]). If `radius` is passed points inside radius are masked.

        :param X: array of x-coordinates
        :param Y: array of y-coordinates
        :param symmetric: if true the plot is symmetric w.r.t. the x-axis
        :param radius: radius of the particle
        """
        X, Y, triangs = self.triangulation(X, Y, symmetric=symmetric)
        if not self.particle:
            mask = (
                np.hypot(
                    X[triangs.triangles].mean(axis=1),
                    Y[triangs.triangles].mean(axis=1),
                ) < radius
            )
            triangs.set_mask(mask)
        return triangs

    # -------------------------------------------------------------------------
    # Private Methods: Animation
    # -------------------------------------------------------------------------

    def _animation_func_tripcolor(
        self,
        frame: int,
        n_frames: int,
        triplot: TriMesh,
        annotation: Annotation,
        data_func: Callable[
            [float],
            tuple[np.ndarray, np.ndarray, np.ndarray],
        ],
        symmetric: bool,
    ) -> TriMesh:
        """Animation function for tripcolor plot


        :param frame: frame
        :param n_frames: nbr of frames
        :param triplot: TriMesh object
        :param annotation: phase annotation
        :param data_func: function that returns speed for given phase
        :param symmetric: if the symmetric part of plot shall be plotted
        """
        # Compute Phase
        phase = frame / n_frames * 2 * pi
        # Get data
        _, _, speed = data_func(phase)
        # Symmetry
        if symmetric:
            speed = np.concatenate([speed, speed])
        # Update plot
        triplot.set_array(speed)

        # Update phase annotation
        self._update_phase_annotation(annotation, phase)

        return triplot

    def _animation_func_tricontourf(
            self,
            frame: int,
            n_frames: int,
            ax: plt.Axes,
            triplot: TriMesh,
            triang: Triangulation,
            annotation: Annotation,
            data_func: Callable[
                [float],
                tuple[np.ndarray, np.ndarray, np.ndarray],
            ],
            symmetric: bool,
    ) -> TriMesh:
        """Animation function for tricontourf plot

        :param frame: frame
        :param n_frames: nbr of frames
        :param ax: Axes object
        :param triplot: TriMesh object
        :param triang: triangles of triangulation
        :param annotation: phase annotation
        :param data_func: function that returns speed for given phase
        :param symmetric:
        :return: if the symmetric part of plot shall be plotted
        """
        # Compute Phase
        phase = frame / n_frames * 2 * pi
        # Get data
        _, _, speed = data_func(phase)
        # Symmetry
        if symmetric:
            speed = np.concatenate([speed, speed])
        # Get levels
        levels = triplot.levels

        # Remove artists from plot
        collections = triplot.collections
        for coll in collections:
            triplot.collections.remove(coll)

        # Plot contours anew
        triplot = ax.tricontourf(
            triang, speed, cmap=self.cmap,
            levels=levels,
        )

        # Update phase annotation
        self._update_phase_annotation(annotation, phase)

        return triplot

    # -------------------------------------------------------------------------
    # Private Methods Axes post processing
    # -------------------------------------------------------------------------

    def _finish_triplot(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        radius: Optional[float],
        cbar_mappable: ScalarMappable,
        cbar_label: str,
    ) -> Optional[Colorbar]:
        """Post-processes tricontourf/tripcolor plot

        add ticks, labels, circle, color bar, and color bar label
        :param fig: Figure object
        :param ax: Axes object
        :param radius: particle radius
        :param cbar_mappable: mappable for the color bar
        :param cbar_label: label for the color bar
        """
        self._set_lims(ax)
        self._finish_plot(ax, radius)
        cbar = self._add_colorbar(fig, ax, cbar_mappable, cbar_label)
        return cbar

    @staticmethod
    def _add_colorbar(
        fig: plt.Figure,
        ax: plt.Axes,
        mappable: ScalarMappable,
        label: str,
    ) -> Optional[Colorbar]:
        """Add color bar to figure

        :param fig: figure
        :param mappable: mappable
        """
        if fig is None:
            fig = plt.gcf()  # pragma: no cover

        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', '8%', pad='8%')
        cbar = fig.colorbar(mappable, cax=cax, label=label)
        return cbar

    def _set_lims(
        self,
        ax: plt.Axes,
    ) -> None:
        """Set the limits in the plot

        :param ax: Axes object
        """
        ax.autoscale(True, tight=True)
        old_left, old_right = ax.get_xlim()
        if self.particle:
            left = 1.05 * old_left
            right = 1.05 * old_right
        else:
            left = old_left / sqrt(2)
            right = old_right / sqrt(2)
        ax.set_xlim(left, right)
        ax.set_ylim(left, right)


if __name__ == '__main__':
    pass
