r"""
Visualization class for initial stage of algorithm
"""
from spinterface.sps_results.stage_visualizer.ivisstage import IVisStage
from pathlib import Path
from typing import Union, Tuple, List
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista


class CVisInitial(IVisStage):
    r"""
    Visualize initial state
    """

    def __init__(self, strategy: int, info_file: Union[Path, str],
                 camera_spin_files: Union[List[Tuple[float, float, float]], None] = None,
                 spinvisualization_technique: str = 'oop', i_initial_evecs: bool = True,
                 n_initial_evecs: int = 10, arrowscale_evec:float = 30) -> None:
        r"""
        Initializes visiualization stage

        Args:
            strategy(int): strategy
            info_file(Path,str): the file which holds information about the initial state
        """
        super().__init__(strategy, camera_spin_files)
        self.parent_directory = Path(info_file).parent
        self.info_file = info_file
        self.i_initial_evecs = i_initial_evecs
        self.n_initial_evecs = n_initial_evecs
        self.arrowscale_evec = arrowscale_evec
        self.spinvisualization_technique = spinvisualization_technique

    @property
    def stage(self) -> str:
        r"""
        Returns:
            the stage
        """
        return 'Initial'

    def _stagestrategytext(self) -> str:
        r"""
        Returns:
            the displace strategy in words
        """
        if self.strategy == 1:
            return 'Visualize eigenvectors of initial state'
        else:
            return 'Describing text for this strategy not yet coded.'

    def __call__(self) -> None:
        r"""
        Excecutes the visualization for the initial stage
        """
        if self.strategy in [1]:
            if not self.i_initial_evecs:
                raise ValueError('Strategy 1 cant be chosen if i_initial_eigenvec in input sps file is False.')
            self._visualize_eigenvectors()

    def _visualize_eigenvectors(self):
        r"""
        Visualizes the spin configurations for all displaced configurations
        """
        for n in range(1,self.n_initial_evecs+1):
            p = self.parent_directory / 'initial_eigenvectors' / f'evec_initial_{n}.dat'
            p_png = self.parent_directory / 'initial_eigenvectors' / f'evec_initial_{n}.png'
            l_latt = CLattice(source='evec', path=p)
            l_visu = CVisualPyVista(lattice=l_latt, cam=self.spincam, arrowscale=self.arrowscale_evec)
            l_visu(outpath=p_png)
            l_visu.plotter.close()
