from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from osaft.plotting.base_plotting import BasePlot
from osaft.plotting.datacontainers.arf_datacontainer import ARFData


class ARFPlotter(BasePlot):

    def __init__(self) -> None:
        self._abscissa = None
        self._attr_name = None

    def plot_solution(
            self, x_values: np.ndarray, data: ARFData,
            ax: plt.Axes, plot_method, **kwargs,
    ) -> (plt.Figure, plt.Axes):
        fig, ax = self._create_figure(ax)

        plt.sca(ax)
        plot_method(
            x_values, data.plotting,
            label=data.name,
            linestyle=data.line_style,
            **kwargs,
        )

        return fig, ax

    @staticmethod
    def add_legend(ax: plt.Axes) -> None:
        ax.legend()

    @staticmethod
    def set_labels(
        ax: plt.Axes,
        attr_name: str,
        norm_name: Optional[str] = None,
    ) -> None:
        ax.set_xlabel(f'Attribute {attr_name}')

        if norm_name is None:
            ax.set_ylabel(r'$F^{\mathrm{rad}}$ $\mathrm{[N]}$')
        else:
            ax.set_ylabel('normalized ARF [-]')


if __name__ == '__main__':
    pass
