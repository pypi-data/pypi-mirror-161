r"""
Viualizes a STMi file
"""
from spinterface.inputs.lattice.CLattice import CLattice
from spinterface.visualizations.lattices.cvisualpyvista_new_cmap import CVisualPyVistaNewCmap
from spinterface.visualizations.lattices.cvisualpyvista import CVisualPyVista
from pathlib import Path
name = 'ass'
cam_ass = [(25.03556881010106, 4.688359367769459, 50.19833751505569),
 (25.03556881010106, 4.688359367769459, 2.4780631065368652e-05),
 (0.0, 1.0, 0.0)]
name = 'fm'
cam_fm = [(24.510154850781, 0.1697993176167817, 50.19833751505569),
 (24.510154850781, 0.1697993176167817, 2.4780631065368652e-05),
 (0.0, 1.0, 0.0)]
#name = 'skyr_pdfeir_025_hcp'
#name = 'skyr_m5'
cam_skyr_m1_zoom = [(24.510154850781, 0.1697993176167817, 34.28614781486685),
 (24.510154850781, 0.1697993176167817, 2.4780631065368652e-05),
 (0.0, 1.0, 0.0)]
#name = 'chim'
cam_chim = [(23.77457530773292, -2.667436062711644, 50.19833751505569),
 (23.77457530773292, -2.667436062711644, 2.4780631065368652e-05),
 (0.0, 1.0, 0.0)]
#name = 'skyrmionium_m2'
cam_skyrmionium = [(25.070596407389107, 0.06471652575276599, 50.19833751505569),
 (25.070596407389107, 0.06471652575276599, 2.4780631065368652e-05),
 (0.0, 1.0, 0.0)]

file = Path.cwd() / (name +'.dat')

latt = CLattice(source='STM', path=file, N1=50, N2=50, N3=1)

visu = CVisualPyVista(lattice=latt, tiplength=1.0,tipradius=0.5, draw_background=False,cam=cam_skyrmionium, topology=False, heatmap=True, heatmap_saturation=1.0)
#visu.plotter.view_xy()
visu.show()
visu(outpath=Path.cwd() / (name +'_topology.png'))

