r"""
Construction class for translational modes
"""
from typing import Union, Tuple

import numpy as np

from spinterface.inputs.lattice.modeconstruction.imodeconstruction import IModeConstruction


class CConstructTranslational(IModeConstruction):
    r"""

    """

    def __init__(self, spins: np.ndarray, points: np.ndarray, lattvec: np.ndarray) -> None:
        r"""
        """
        super().__init__(spins, points, lattvec)
        self.shiftedspins = self._create_translated_spins()
        self.evec = self._create_evec()

    def _create_evec(self) -> np.ndarray:
        r"""
        Create translation vector based on the spin configuration and the shifted configuration
        """
        evec = []
        for index, spin in enumerate(self.spins):
            angle = np.arccos(np.dot(spin / np.linalg.norm(spin),
                                     self.shiftedspins[index] / np.linalg.norm(self.shiftedspins[index])))
            spin_diff = self.shiftedspins[index] - spin
            displacement = spin_diff - np.dot(spin_diff, spin) * spin
            displacement = displacement / np.linalg.norm(displacement)
            evec.append(displacement * angle)
        return np.asarray(evec)

    def _create_translated_spins(self) -> np.ndarray:
        r"""
        Saves for each spin the neighbor spin in direction of the next lattice vector
        """
        translated_spins = []
        # under the assumption of equal lattice size in both lattice vectors
        latt_size = int(np.sqrt(len(self.points)))
        for index, point in enumerate(self.points):
            searchpoint = point + self.lattvec
            # find index of neighbor
            index_searchpoint = np.argwhere((np.linalg.norm(self.points - searchpoint, axis=1)) <= 1.0e-4)
            # periodic boundaries
            # find all points on a line through the current point in the direction of lattvec
            if not index_searchpoint:
                searchpoint = point - (latt_size - 1) * self.lattvec
                index_searchpoint = np.argwhere((np.linalg.norm(self.points - searchpoint, axis=1)) <= 1.0e-4)
            translated_spins.append(self.spins[index_searchpoint[0][0]])
        return np.asarray(translated_spins)

    def __call__(self) -> Union[Tuple[np.ndarray, np.ndarray], np.ndarray]:
        return self.evec
