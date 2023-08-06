import os
import subprocess
import unittest

from matplotlib import pyplot as plt


class BaseTestPlotting(unittest.TestCase):

    def setUp(self) -> None:
        self.create_output_folder('OutputPlotting')

    @property
    def output_folder_path(self) -> str:
        """ Absolute folder path for all figure outputs
        """
        return self._output_folder_path

    @property
    def root_folder(self) -> str:
        """ Folder patch of the calling script
        """
        return subprocess.Popen(
            ['git', 'rev-parse', '--show-toplevel'],
            stdout=subprocess.PIPE,
        ).communicate()[0].rstrip().decode('utf-8')

    def _get_absolute_filename(self, name: str, file_type: str) -> os.path:
        """ Return the absolute path of root_folder + name
        """
        return os.path.join(self.output_folder_path, f'{name}.{file_type}')

    def create_output_folder(self, folder_name: str) -> None:
        """ Creates a folder if non-existent relative to the root_folder
        """
        abs_path = os.path.join(self.root_folder, folder_name)
        self._output_folder_path = abs_path
        if not os.path.isdir(abs_path):
            os.mkdir(abs_path)

    def save_fig(self, fig: plt.Figure, name: str, **kwargs) -> None:
        """Saves the figure

        :param fig: figures instance
        :param name: name of the file the figure is saved to
        :param **kwargs: passed to matplotlib.Figure.savefig
        """
        file_name = self._get_absolute_filename(name, 'pdf')
        fig.savefig(file_name, **kwargs)
        plt.close(fig)


if __name__ == '__main__':
    pass
