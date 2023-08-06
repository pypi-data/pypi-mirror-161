# -*- coding: utf-8 -*-
r"""
This module contains the class CLattice. Its realizations represent a spin structure.
"""
import pandas as pd
import spinterface.inputs.lattice.utilities as utils
from spinterface.inputs.lattice.ILattice import ILattice
from spinterface.inputs.lattice.spintransformations.CRotation import CRotationAlongEvec
from pathlib import Path
import numpy as np
from typing import Tuple, List, Union
from scipy.optimize import curve_fit
from spinterface.inputs.lattice.const import LATT_TYPE_SPIN, LATT_TYPE_EVEC, LATT_TYPE_FORCE
from spinterface.inputs.lattice.topology.CTopology import CTopologyHexCubic
from spinterface.inputs.lattice.topology.ITopology import ITopology
from spinterface.inputs.lattice.modeconstruction.cconstructiontranslational import CConstructTranslational
from spinterface.inputs.lattice.CMagnetizations import Magnetisation_Domainwall, Magnetisation_Bimeron, Magnetisation_Chimera


class CLattice(ILattice):
    r"""
    Creates a lattice which can be used to produce a SpinSTMi-type file. The structure will be read through a lattice.in
    file.
    """

    def __init__(self, source: str = 'lattice.in', path: Path = Path.cwd() / 'lattice.in',
                 magdir: np.array = np.array([0.0, 0.0, 1.0]), N1: Union[None, int] = None, N2: Union[None, int] = None,
                 N3: Union[None, int] = None, per_boundaries: bool = False) -> None:
        r"""
        Initializes the lattice

        Args:
            source(str): Defines how the lattice shall be constructed. If source is evec the spins will be the components
            of the eigenvector and the magmoms the length of these components.
            latticefile(Path): path to the lattice.in/STM/evec file from which the lattice will be constructed.
            magdir(np.array): initial magnetisation direction of the lattice.
            N1, N2, N3: in case of reading from STM file one might need the information about N1, N2, and N3 to calculate
            e.g. the topological density.
        """
        self._source = source
        self._per_boundaries = per_boundaries
        if self._source == 'lattice.in':
            self._latticefile = path
            a1, a2, a3, r_motif, N1, N2, N3 = self._readfromlatticefile()
            super().__init__(a1, a2, a3, r_motif, N1, N2, N3, magdir)
        elif self._source in ['STM', 'evec', 'force']:
            self._stmfile = path
            a1, a2, a3, r_motif = None, None, None, None
            super().__init__(a1, a2, a3, r_motif, N1, N2, N3, magdir)
            df = pd.read_csv(path, sep=r'\s+', usecols=[0, 1, 2, 3, 4, 5, 6],
                             names=['x', 'y', 'z', 'sx', 'sy', 'sz', 'm'])
            self._points = np.column_stack((df['x'].to_numpy(), df['y'].to_numpy(), df['z'].to_numpy()))
            self._spins = np.column_stack((df['sx'].to_numpy(), df['sy'].to_numpy(), df['sz'].to_numpy()))
            self._magmoms = df['m'].to_numpy()
        else:
            raise NotImplementedError(f'Source not yet implemented. Choose between lattice.in or STM, evec or force.')

        self._skradius = None
        self._topologies = []

    def _readfromlatticefile(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[np.array], int, int, int]:
        r"""
        Reads the lattice.in.

        Returns:
            a1(np.array): lattice vector a1, multiplied by length stored in alat
            a2(np.array): lattice vector a2, multiplied by length stored in alat
            a3(np.array): lattice vector a3, multiplied by length stored in alat
            r_motif(List(np.array)): positions of the atoms within the unit cell, the corresponding vectors are gien in
            units of a1,a2 and a3.
            N1(int): number of unit cells in a1 direction
            N2(int): number of unit cells in a2 direction
            N3(int): number of unit cells in a3 direction
        """
        with open(str(self._latticefile), 'r') as f:
            for (lnr, line) in enumerate(f):
                L = str(line).lstrip()
                if L.startswith('#'):
                    continue
                if L.startswith('Nsize'):
                    L = L[5:]
                    L.lstrip()
                    ns = L.split()
                    N1 = int(ns[0])
                    N2 = int(ns[1])
                    N3 = int(ns[2])
                if L.startswith('alat'):
                    L = L[4:]
                    L.lstrip()
                    alats = L.split()
                    alat1 = int(float(alats[0]))
                    alat2 = int(float(alats[1]))
                    alat3 = int(float(alats[2]))
                if L.startswith('lattice'):
                    lattline = lnr
                if L.startswith('motif'):
                    L = L[5:]
                    motifline = lnr
                    Nuc = int(L.split()[0])

        with open(str(self._latticefile), 'r') as f:
            for (lnr, line) in enumerate(f):
                L = str(line)
                if lnr == lattline + 1:
                    L.lstrip()
                    a1s = L.split()
                    a1 = np.array([float(a1s[0]), float(a1s[1]), float(a1s[2])])
                if lnr == lattline + 2:
                    L.lstrip()
                    a2s = L.split()
                    a2 = np.array([float(a2s[0]), float(a2s[1]), float(a2s[2])])
                if lnr == lattline + 3:
                    L.lstrip()
                    a3s = L.split()
                    a3 = np.array([float(a3s[0]), float(a3s[1]), float(a3s[2])])
        r_motif = []
        for n in range(Nuc):
            with open(str(self._latticefile), 'r') as f:
                for (lnr, line) in enumerate(f):
                    L = str(line)
                    if lnr == motifline + 1 + n:
                        L.lstrip()
                        r1s = L.split()
                        r_motif.append(np.array([float(r1s[0]), float(r1s[1]), float(r1s[2]), float(r1s[3])]))
        # remove non magnetic atoms from unit cell
        r_motif = [mot for mot in r_motif if mot[3] != 0.0]

        return a1 * alat1, a2 * alat2, a3 * alat3, r_motif, N1, N2, N3

    def add_domainwallstarter(self, boundary_normal: np.ndarray = None, turn_boundary: bool = True,
                              width_boundary_region: float = 1.0) -> None:
        r"""
        Adds a heavyside function to a lattice. This means the spins on one side of the lattice point upwards while the
        other side points downwards. There is one line of spins in plane at the border. The normal direction to the boundary
        can be defined.

        Args:
            boundary_normal: vector defining the normal of the boundary.
            turn_boundary: weither the boundary line of spins shall lie in the in plane direction
            width_boundary_region: allowance for spins to be in the boundary. C
        """

        if self.source == LATT_TYPE_EVEC:
            raise ValueError('Adding a domain wall initial state to an eigenvector lattice makes no sense!')
        if self.source == LATT_TYPE_FORCE:
            raise ValueError('Adding a domain wall initial state to an force lattice makes no sense!')
        # make sure boundary vector is normalized
        if boundary_normal is None:
            boundary_normal = self.a1
        if boundary_normal[2] != 0:
            raise ValueError('No out of plane pointing boundaries are allowed.')
        boundary_normal = boundary_normal / np.linalg.norm(boundary_normal)
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            midpoint = self.layermidpoints[layer]
            points = magstructure_layer[:, :3]
            dots = [np.dot((p - midpoint) / np.linalg.norm(p - midpoint), boundary_normal) for p in points]
            spins = [np.array([0.0, 0.0, 1.0]) if d >= 0 else np.array([0.0, 0.0, -1.0]) for d in dots]
            if turn_boundary:
                midpoint_shifted_forward = midpoint + boundary_normal * width_boundary_region
                midpoint_shifted_backward = midpoint - boundary_normal * width_boundary_region
                dots_forward = [np.dot((p - midpoint_shifted_forward) / np.linalg.norm(p - midpoint_shifted_forward),
                                       boundary_normal)
                                for p in points]
                dots_backward = [np.dot((p - midpoint_shifted_backward) / np.linalg.norm(p - midpoint_shifted_backward),
                                        boundary_normal)
                                 for p in points]

                spins = [boundary_normal if (0 < dots_backward[index]) and (d <= 0) else spins[index] for (index, d) in
                         enumerate(dots_forward)]
            magstructure_layer[:, 3:6] = np.asarray(spins)
            self.setlayer_by_idx(layer, magstructure_layer)

    def addDomainwall(self, r0, direction, width, heli=np.pi):
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            mag = Magnetisation_Domainwall(magstructure_layer[:,0], magstructure_layer[:, 1], r0, direction, width, heli)
            for m in range(len(mag.mz)):
                if mag.mz[m] < (1.0 - 10 ** (-2)):
                    magstructure_layer[m, 3] = mag.mx[m]
                    magstructure_layer[m, 4] = mag.my[m]
                    magstructure_layer[m, 5] = mag.mz[m]
            self.setlayer_by_idx(layer, magstructure_layer)

    def add_bimeron(self, pos0, R, a1, a2):
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            mag = Magnetisation_Bimeron(magstructure_layer[:,0], magstructure_layer[:, 1], pos0, R, a1, a2)
            for m in range(len(mag.mz)):
                if mag.mz[m] < (1.0 - 10 ** (-2)):
                    magstructure_layer[m, 3] = mag.mx[m]
                    magstructure_layer[m, 4] = mag.my[m]
                    magstructure_layer[m, 5] = mag.mz[m]
            self.setlayer_by_idx(layer, magstructure_layer)


    def add_chimera(self, ursprung, vorticity, helicity, c, w, AFM=False, uplo=1, sym_chimera=True, angl_chimera=0.,
                    elongation=False, angl_elongation=0., ab_elongation=[1., 1.]):
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            mag = Magnetisation_Chimera(magstructure_layer[:,0], magstructure_layer[:, 1], ursprung, vorticity, helicity, c, w, AFM, uplo, sym_chimera,
                                        angl_chimera, elongation, angl_elongation, ab_elongation)
            for m in range(len(mag.mz)):
                if (uplo == 1 and mag.mz[m] < (1.0 - 5 * 10 ** (-4))) or (
                        uplo == -1 and mag.mz[m] > -(1.0 - 5 * 10 ** (-4))):
                    magstructure_layer[m, 3] = mag.mx[m]
                    magstructure_layer[m, 4] = mag.my[m]
                    magstructure_layer[m, 5] = mag.mz[m]
            self.setlayer_by_idx(layer, magstructure_layer)


    def add_skyrmiontube(self, vorticity: int = 1.0, helicity: float = np.pi / 1, c: float = 2.5, w: float = 2.0,
                         AFM: bool = False) -> None:
        r"""
        Adds a skyrmion tube in all layers. Each layer has the same skyrmion (same parameters). Does also works for
        monolayer skyrmions

        Args:
            vorticity(int): topological charge of the skyrmion
            helicity(float): pi -> neel, pi/2 -> bloch
            c(float): size of the domain in the middle of the skyrmion
            w(float): size of the region where the spins tilt (domain wall width)
            AFM(bool): whether each layer shall be antiferromagnet
        """
        if self.source == LATT_TYPE_EVEC:
            raise ValueError('Adding a skyrmiontube to an eigenvector lattice makes no sense!')
        if self.source == LATT_TYPE_FORCE:
            raise ValueError('Adding a skyrmiontube to an force lattice makes no sense!')
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            XY = magstructure_layer[:, :2].copy() - self.layermidpoints[layer][:2]
            r = np.linalg.norm(XY, axis=1)
            pp = np.arctan2(XY[:, 1], XY[:, 0])
            th = utils.theta(r, c, w)
            ph = utils.phi(pp, vorticity, helicity)
            n = np.arange(0, len(XY[:, 0]), 1)
            if AFM:
                sign = (-1) ** (n % 2 + n // int(np.sqrt(len(XY[:, 0]))))
            else:
                sign = 1
            uplo = 1
            magstructure_layer[:, 3] = np.sin(th) * np.cos(ph) * sign
            magstructure_layer[:, 4] = np.sin(th) * np.sin(ph) * sign
            magstructure_layer[:, 5] = np.cos(th) * float(uplo) * sign
            self.setlayer_by_idx(layer, magstructure_layer)


    def add_randomspins(self, xlims: Union[None, Tuple[float, float]] = None,
                        ylims: Union[None, Tuple[float, float]] = None) -> None:
        r"""
        Adds random spins within region of lattice
        """
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            vectors = np.random.uniform(-1,1,(len(magstructure_layer[:, 0]), 3))
            norm = np.sqrt((vectors ** 2).sum(-1))[..., np.newaxis]
            normed_vecs = vectors / norm.reshape(-1, 1)
            if xlims is None and ylims is None:
                magstructure_layer[:, 3:6] = normed_vecs
            else:
                if ylims is not None and xlims is None:
                    magstructure_layer = np.array([[atom[0], atom[1], atom[2], normed_vecs[index][0], normed_vecs[index][1],
                                                    normed_vecs[index][2], atom[6]] if ylims[0] < atom[1] < ylims[
                        1] else atom for (index, atom) in enumerate(magstructure_layer)])
                if xlims is not None and ylims is None:
                    magstructure_layer = np.array([[atom[0], atom[1], atom[2], normed_vecs[index][0], normed_vecs[index][1],
                                                    normed_vecs[index][2], atom[6]] if xlims[0] < atom[0] < xlims[
                        1] else atom for (index, atom) in enumerate(magstructure_layer)])
                if xlims is not None and ylims is not None:
                    magstructure_layer = np.array([[atom[0], atom[1], atom[2], normed_vecs[index][0], normed_vecs[index][1],
                                                    normed_vecs[index][2], atom[6]] if (xlims[0] < atom[0] < xlims[
                        1] and ylims[0]<atom[1]<ylims[1]) else atom for (index, atom) in enumerate(magstructure_layer)])
            self.setlayer_by_idx(layer, magstructure_layer)

    def construct_translational_mode(self, lattvec: Union[np.ndarray, None] = None, write_file: bool = False,
                                     outpath: Path = Path.cwd() / 'evec_translation.dat') -> np.ndarray:
        r"""

        """
        if lattvec is None:
            if self.a1 is None or self.a2 is None:
                raise ValueError("Need lattice vector. Either provide as input to this routine or via lattice.in")
            l_lattvec = self.a1
        else:
            l_lattvec = lattvec
        evecconstructor = CConstructTranslational(spins=self.spins, points=self.points, lattvec=l_lattvec)
        evec = evecconstructor()
        if write_file:
            data = {'x': self.points[:, 0], 'y': self.points[:, 1], 'z': self.points[:, 2], 'vx': evec[:, 0],
                    'vy': evec[:, 1], 'vz': evec[:, 2], 'v': np.linalg.norm(evec, axis=1)}
            df = pd.DataFrame(data)
            df.to_csv(outpath, header=False, sep=' ', index=False)
        return evec

    def construct_rotational_mode(self) -> None:
        r"""

        :return:
        """
        raise ValueError('not yet coded!')

    def rotate(self, displacement: Union[Path, np.ndarray], scale: float = 1.0) -> None:
        r"""
        Rotates the spinconfiguration of the lattice along the displacement according to Rodrigues formula.
        :param displacement: 2D np array: [[p1x,p1y,p1z],...,[pNx,pNy,pNz]] where N is the number of spins in the lattice.
            The rotation axis for the ith spin is given by s_i x p_i and its rotation angle is defined as |p_i|.
        :param scale: Scales the rotation angle of all spins
        """
        if self.source == LATT_TYPE_EVEC:
            raise ValueError('Rotating the eigenvector itself does not make sense!')
        if self.source == LATT_TYPE_FORCE:
            raise ValueError('Rotating the force does not make sense!')
        l_spins = self.spins
        # decide on the source of the rotations:
        if type(displacement) == type(Path.cwd()):
            rotator = CRotationAlongEvec(spins=l_spins, scale=scale, evec_source='file', evec_path=displacement)
        elif type(displacement) == type(np.array([0.0, 0.0, 0.0])):
            rotator = CRotationAlongEvec(spins=l_spins, scale=scale, evec_source='data', evec_data=displacement)
        else:
            raise ValueError('Not the correct data type for displacement input.')
        self.spins = rotator.applyrotation()

    @property
    def source(self) -> str:
        r""""
        Returns:
            the source of the lattice. For lattice.in and STM a spin configuration is assumed. For
        """
        if self._source == 'lattice.in' or self._source == 'STM':
            return LATT_TYPE_SPIN
        elif self._source == 'evec':
            return LATT_TYPE_EVEC
        elif self._source == 'force':
            return LATT_TYPE_FORCE

    @property
    def skradius(self) -> List[Union[None, float]]:
        r"""
        Returns:
             the skyrmion radius in units of the lattice constant for all layers. None if no skyrmion exists or the fit
             fails.
        """
        if self.source == LATT_TYPE_EVEC:
            raise ValueError('Calculating the skyrmion radius for an eigenvector lattice makes no sense!')
        if self.source == LATT_TYPE_FORCE:
            raise ValueError('Calculating the skyrmion radius for a force lattice makes no sense!')
        rads = []
        for n in range(self.nlayer):
            currentlayer = self.getlayer_by_idx(n)
            if np.min(currentlayer[:, 3:6]) >= 0.0:
                print(f'layer {n} does not contain skyrmion.')
                rads.append(None)
            else:
                minmag = currentlayer[currentlayer[:, 5] == np.min(currentlayer[:, 5])]
                start_parameter = [minmag[0][0], minmag[0][1], 2.5, 3.0]
                try:
                    popt, pcov = curve_fit(utils.sk_2dprofile, currentlayer[:, :2], currentlayer[:, 5], start_parameter,
                                           maxfev=2000)
                    popt, pcov = curve_fit(utils.sk_2dprofile, currentlayer[:, :2], currentlayer[:, 5], popt)
                    rads.append(utils.sk_radius(popt[2], popt[3]))
                except RuntimeError:
                    print(f'layer {n} does not contain skyrmion.')
                    rads.append(None)
        return rads

    @property
    def topologies(self) -> List[ITopology]:
        r"""
        Returns a list of topology objects. One for each layer
        """
        if self.source != LATT_TYPE_SPIN:
            print('WARNING: You calc. the topology of a non-spin-lattice. Might not make sense at all.')
        self._topologies = []
        for idx_layer in range(self.nlayer):
            selected_layer = self.getlayer_by_idx(idx=idx_layer)
            points = selected_layer[:, :3]
            spins = selected_layer[:, 3:6]
            self._topologies.append(CTopologyHexCubic(points=points, spins=spins, N1=self.N1, N2=self.N2, per_boundaries=self._per_boundaries))
        return self._topologies
