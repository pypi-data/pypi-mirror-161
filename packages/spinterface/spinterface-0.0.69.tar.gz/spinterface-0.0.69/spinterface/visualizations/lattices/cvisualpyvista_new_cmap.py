# -*- coding: utf-8 -*-
r"""
Module contains implementation of pyvista visualizations for spin lattices.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import vtkmodules.util.vtkConstants
import matplotlib as mpl
from spinterface.visualizations.lattices.utilities import get_colormap
import pyvista as pv
import vtk
import numpy as np
from spinterface.visualizations.lattices.ivisualizer import IVisualizer
from spinterface.inputs.lattice.ILattice import ILattice
from typing import List, Tuple, Union, Dict
from spinterface.visualizations.const import SPINDEFAULT_SETTINGS, EVECDEFAULT_SETTINGS
from spinterface.inputs.lattice.const import LATT_TYPE_EVEC, LATT_TYPE_SPIN


class CVisualPyVistaNewCmap(IVisualizer):
    r"""
    Class for visualizing spin lattices with py vista library
    """

    def __init__(self, lattice: ILattice, tiplength: Union[float, None] = None, tipradius: Union[float, None] = None,
                 arrowscale: Union[float, None] = None, draw_background: Union[bool, None] = None,
                 cam: Union[List[Tuple[float, float, float]], None] = None,
                 cmap: str = 'hsv_spind', total_mag=False, topology=False) -> None:
        r"""
        Initializes the visualization

        Args:
            tiplength(float): geometry of arrow: tiplength
            tipradius(float): geometry of arrow: tipradius
            arrowscale(float): geometry of arrow: arrowscale
            draw_background(bool): shall i draw the background of the lattice
            camera: camera position
            cmap: string for the choice of the colormap. Defined in utilities module
            total_mag(bool): if the sum over the lattice vectors shall be visualized in the center of the lattice
            topology(bool): if topology information shall be visualized
        """
        super().__init__(lattice)
        self.text_objects = []
        self.total_mag = total_mag
        self.topology = topology
        self.tiplength, self.tipradius, self.arrowscale, self.drawbackground = self._load_settings(tiplength, tipradius,
                                                                                                   arrowscale,
                                                                                                   draw_background)
        self.cam = cam
        self.cmap = get_colormap(cmap)
        self._make_plotter()

    def _load_settings(self, tl: Union[float, None], tr: Union[float, None],
                       asc: Union[float, None], dbg: Union[bool, None]) -> Tuple[float, float, float, bool]:
        r"""
        Returns:
            loads the tiplength, tipradius and arrowscale depending on the inputs and the lattice type
        """
        # Decide on loading settings
        if self.lattice.source == LATT_TYPE_SPIN:
            print(f'loading defaults for type: {LATT_TYPE_SPIN}')
            tiplength = SPINDEFAULT_SETTINGS['tiplength']
            tipradius = SPINDEFAULT_SETTINGS['tipradius']
            arrowscale = SPINDEFAULT_SETTINGS['arrowscale']
            drawbackground = SPINDEFAULT_SETTINGS['drawbackground']
        elif self.lattice.source == LATT_TYPE_EVEC:
            print(f'loading defaults for type: {LATT_TYPE_SPIN}')
            tiplength = EVECDEFAULT_SETTINGS['tiplength']
            tipradius = EVECDEFAULT_SETTINGS['tipradius']
            arrowscale = EVECDEFAULT_SETTINGS['arrowscale']
            drawbackground = EVECDEFAULT_SETTINGS['drawbackground']
        else:
            raise ValueError('Not a valid lattice source!')
        if tl is not None:
            print('Overwriting tiplength setting with user input')
            tiplength = tl
        if tr is not None:
            print('Overwriting tiplradius setting with user input')
            tipradius = tr
        if asc is not None:
            print('Overwriting arrowscale setting with user input')
            arrowscale = asc
        if dbg is not None:
            print('Overwriting drawbackground setting with user input')
            drawbackground = dbg
        return tiplength, tipradius, arrowscale, drawbackground

    def _make_plotter(self, offscreen: bool = False):
        r"""
        Creates the plotter. The plotter will be recreated when saving the image
        """
        self.plotter = pv.Plotter(off_screen=offscreen, lighting='three lights')
        self._configureplotter()
        self.plotter.camera_position = self.cam
        plotpoints = self.lattice.points[:, :]
        plotspins = self.lattice.spins[:, :]
        plot_colors = self.get_colors(plotspins=plotspins)
        # create color dictionary
        # cmap = self.create_cmap(plot_colors)
        self.PD = pv.PolyData(plotpoints)
        self.PD["colors"]=plot_colors
        self.surf = self.PD.delaunay_2d()
        self.plotter.add_mesh(self.PD,scalars="colors",rgb=True)
        if self.total_mag:
            self._draw_total_magnetization()
        if self.topology:
            self._draw_topology()
        if self.drawbackground:
            self._draw_background()

    def create_cmap(self, plot_colors) -> mpl.colors.ListedColormap:
        r"""

        """
        N = len(plot_colors)  # number of points
        print(N)
        vals = np.ones((N, 4))
        vals[:, 0] = plot_colors[:, 0]
        vals[:, 1] = plot_colors[:, 1]
        vals[:, 2] = plot_colors[:, 2]
        cmap = mpl.colors.ListedColormap(vals)
        return cmap

    def get_colors(self, plotspins: np.ndarray) -> np.ndarray:
        r"""

        """
        colors = []
        for spin in plotspins:
            colors.append(self.HSVtoRGB(spin))
        return np.array(colors)

    @staticmethod
    def HSVtoRGB(vec: np.ndarray, saturation: float = 0.2) -> np.ndarray:
        r"""

        """
        vecnorm = np.linalg.norm(vec)
        H = np.arctan2(vec[1] / vecnorm, vec[0] / vecnorm)
        value = 1 - abs(vec[2] / vecnorm)
        chroma = saturation * value
        # H angle is in interval -pi;pi shift it to 0,2pi
        # also transfer to 0;360
        H = (H + np.pi) * (180 / np.pi)
        Hprime = H / 60
        X = chroma * (1 - abs(Hprime % 2 - 1))
        if 0 <= Hprime < 1:
            r1 = chroma
            g1 = X
            b1 = 0
        elif 1 <= Hprime < 2:
            r1 = X
            g1 = chroma
            b1 = 0
        elif 2 <= Hprime < 3:
            r1 = 0
            g1 = chroma
            b1 = X
        elif 3 <= Hprime < 4:
            r1 = 0
            g1 = X
            b1 = chroma
        elif 4 <= Hprime < 5:
            r1 = X
            g1 = 0
            b1 = chroma
        elif 5 <= Hprime <= 6:
            r1 = chroma
            g1 = 0
            b1 = X
        else:
            raise ValueError
        m = value - chroma
        r = r1 + m
        g = g1 + m
        b = b1 + m
        return np.array([r, g, b])

    def _draw_topology(self) -> None:
        r"""
        Visualizes the topology information of a lattice.
        """
        if self.lattice.source != LATT_TYPE_SPIN:
            print('WARNING: topology for non spin lattices might not make sense.')
        topos = self.lattice.topologies
        # draw the topologic density for each layer
        for layeridx in range(self.lattice.nlayer):
            topo = topos[layeridx]
            cell_types = np.array([vtk.VTK_TRIANGLE for count in range(len(topo.polygons1[::3, 1]))], np.int8)
            cells_list = []
            for idx in range(len(topo.polygons1[::3, 1])):
                cells_list.extend([3, idx * 3, idx * 3 + 1, idx * 3 + 2])
            cells = np.asarray(cells_list)
            grid1 = pv.UnstructuredGrid(cells, cell_types, topo.polygons1[:, :])
            grid1['dens'] = topo.areas1
            self.plotter.add_mesh(grid1, cmap='seismic')
            cell_types = np.array([vtk.VTK_TRIANGLE for count in range(len(topo.polygons2[::3, 1]))], np.int8)
            cells_list = []
            for idx in range(len(topo.polygons2[::3, 1])):
                cells_list.extend([3, idx * 3, idx * 3 + 1, idx * 3 + 2])
            cells = np.asarray(cells_list)
            grid2 = pv.UnstructuredGrid(cells, cell_types, topo.polygons2[:, :])
            grid2['dens'] = topo.areas2
            self.plotter.add_mesh(grid2, cmap='seismic')
            # visualize the center of mass with respect to topologic density.
            center = pv.PolyData(topo.topological_center)
            center = pv.Sphere(radius=1.0, center=topo.topological_center)
            # self.plotter.add_mesh(center, color='k')

    def _draw_total_magnetization(self) -> None:
        r"""
            the total magnetization (the sum of all spins) in the center of the lattice
        """
        length_tot_mag = np.linalg.norm(self.lattice.total_magnetization)

        if self.lattice.source == 'evec':
            if length_tot_mag < 50:
                print('WARNING: the norm of the total magnetization is below 50. The visualization of it might not be '
                      'visible!')
            arrow = pv.Arrow(start=self.lattice.midpoint, direction=self.lattice.total_magnetization, tip_length=0.25,
                             tip_radius=0.1, tip_resolution=20,
                             shaft_radius=0.05, shaft_resolution=20, scale=length_tot_mag / 10)
        else:
            if length_tot_mag < 500:
                print('WARNING: the norm of the total magnetization is below 500. The visualization of it might not be '
                      'visible!')
            arrow = pv.Arrow(start=self.lattice.midpoint, direction=self.lattice.total_magnetization, tip_length=0.25,
                             tip_radius=0.1, tip_resolution=20,
                             shaft_radius=0.05, shaft_resolution=20, scale=length_tot_mag / 100)
        self.plotter.add_mesh(arrow, color='k')

    def _draw_background(self) -> None:
        r"""
        Draws the background of the lattice
        """
        for layer in range(self.lattice.nlayer):
            magstruct = self.lattice.getlayer_by_idx(layer)
            points = magstruct[:, :3]
            points_poly = pv.PolyData(points)
            surface = points_poly.delaunay_2d()
            self.plotter.add_mesh(surface, show_edges=True, opacity=0.5)


    def _configureplotter(self) -> None:
        r"""
        Configures the plotter object
        """
        pv.set_plot_theme("ParaView")
        pv.rcParams['transparent_background'] = True
        self.plotter.set_background('black')

        def cam() -> None:
            print('Camera postion: ', self.plotter.camera_position)

        self.plotter.add_key_event('c', cam)

    def show(self) -> None:
        r"""
        Shows the plotter
        """
        print('Look what you have done.......')
        print('to get current cam-position press key c')
        self.plotter.show()

    def add_text(self, **kwargs):
        r"""
        """
        self.plotter.add_text(**kwargs)
        self.text_objects.append(dict(**kwargs))

    def __call__(self, outpath: Path = Path.cwd() / 'spin.png') -> None:
        r"""
        Saves the image to a file

        Args:
            outpath(Path): output path for the png image created.
        """
        self._make_plotter(offscreen=True)
        for text_object in self.text_objects:
            self.plotter.add_text(**text_object)
        self.plotter.window_size = [4000, 4000]
        self.plotter.screenshot(str(outpath))
