r"""
Combines different visualization in a grid of plots
"""
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista
from typing import List, Tuple
import pyvista as pv
from pathlib import Path


class CVisualCollection:
    r"""

    """

    def __init__(self, frames: List[CVisualPyVista], grid: Tuple[int, int], windowsize: Tuple[float,float] = (4000,4000)) -> None:
        r"""

        :param frames:
        :param grid:
        """
        self.grid = grid
        self.frames = frames
        self.windowsize = windowsize
        nr_frames = self.grid[0] * self.grid[1]
        if len(frames) > nr_frames:
            print('WARNING: number of images exceeds grid. Only the first images will be presented...')
        if len(frames) < nr_frames:
            print('WARNING: number of images less then possible for this grid. There will be free elements...')
        self._make_multiplot()

    def _make_multiplot(self, offscreen: bool = False):
        r"""
        Makes the multiplot
        """
        if offscreen:
            self.plotter = pv.Plotter(shape=self.grid, off_screen=offscreen, lighting='three lights', window_size=self.windowsize)
        else:
            self.plotter = pv.Plotter(shape=self.grid, off_screen=offscreen, lighting='three lights')
        ind1 = 0
        ind2 = 0
        for frame in self.frames:
            if ind1 == self.grid[0]:
                ind2 = ind2 + 1
                ind1 = 0
            self.plotter.subplot(ind1, ind2)
            frame.add_meshes_to_different_plotter(self.plotter)
            ind1 = ind1 + 1

    def show(self) -> None:
        r"""
        Shows the plotter
        """
        print('Look what you have done.......')
        self.plotter.show()

    def __call__(self, outpath: Path = Path.cwd() / 'collection.png') -> None:
        r"""
        Saves the image to a file

        Args:
            outpath(Path): output path for the png image created.
        """
        self._make_multiplot(offscreen=True)
        self.plotter.screenshot(str(outpath))
