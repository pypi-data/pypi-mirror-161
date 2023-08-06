r"""
Based on a spin lattice construct a normalized eigenvector which is a mode for this lattice (most likely this will be
realized as a translation or rotation).
"""
from abc import ABC, abstractmethod
from typing import Union, Tuple
import numpy as np


class IModeConstruction(ABC):
    r"""
    Abstract base class for construction of modes for selected lattices.
    """
    def __init__(self, spins: np.ndarray, points: np.ndarray, lattvec: np.ndarray) -> None:
        r"""
        Args:
            spins: spins of the lattice
            points: lattice coordinates of the spins
        """
        self.spins = spins
        self.points = points
        self.lattvec = lattvec

    @abstractmethod
    def __call__(self) -> Union[Tuple[np.ndarray,np.ndarray],np.ndarray]:
        r"""
        Returns:
            eigenvector or tuple of eigenvectors
        """
