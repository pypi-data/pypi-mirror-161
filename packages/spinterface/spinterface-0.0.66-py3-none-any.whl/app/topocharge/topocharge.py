from spinterface.inputs.CWriteInputs import CWriteInput
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista
from pathlib import Path

latt = CWriteInput(name='lattice.in', Nsize='3 3 1', alat='1.0 1.0 1.0',
                       lines=['lattice', '0.5 -0.86602540378 0.0', '0.5 0.86602540378 0.0', '0.0 0.0 1.0',
                              'motif 1 atoms', '0.0 0.0 0.0 3.0'])
latt()
lattice = CLattice(source='lattice.in', per_boundaries=True)
print(lattice.topologies[0].topological_center)


