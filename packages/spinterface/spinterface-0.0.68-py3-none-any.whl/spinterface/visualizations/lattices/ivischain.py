from abc import abstractmethod, ABC
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista
from typing import List
from pathlib import Path


class IVisChain(ABC):
    r"""
    Chain for visualization tasks
    """

    def __init__(self, ) -> None:
        r"""
        Initializes the visualization chain
        """