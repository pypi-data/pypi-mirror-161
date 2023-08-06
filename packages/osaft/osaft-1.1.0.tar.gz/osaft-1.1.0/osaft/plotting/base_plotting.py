from matplotlib import pyplot as plt


class BasePlot:
    """Parent class for all plotting classes."""

    @staticmethod
    def _create_figure(ax: plt.Axes) -> [plt.Figure, plt.Axes]:
        """
        Creates a matplotlib Figure instance and a matplotlib Axes instance.
        If `ax` is passed no new instances are created.

        :param ax: axes
        """
        if ax is None:
            fig, ax = plt.subplots()
            return fig, ax
        else:
            return ax.get_figure(), ax


if __name__ == '__main__':
    pass
