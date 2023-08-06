r"""
This classes instances represent topological information of a lattice object.
"""
import numpy as np
import spinterface.inputs.lattice.utilities as utils

from spinterface.inputs.lattice.topology.ITopology import ITopology


class CTopologyHexCubic(ITopology):
    r"""
    Objects of this class hold topology information of spin lattices for hexagonal and cubic in plane geometries
    """

    def __init__(self, points: np.ndarray, spins: np.ndarray, N1: int, N2: int, per_boundaries: bool = False) -> None:
        r"""
        Initializer. The lattice points have to be in one layer.

        Args:
            points: positions of the lattice points of the layer [[p1x,p1y,p1z],...]
            spins: spins of the layer [[s1x,s1y,s1z],...]
            N1, N2: number of spins in N1- and N2-direction
        """
        self.points = points
        self.spins = spins
        self.N1 = N1
        self.N2 = N2
        self.per_boundaries = per_boundaries
        if not np.all(points[:, 2] == points[0, 2]):
            raise ValueError('ERROR: Not all the points are in the same layer.')
        if any([self.N1 is None, self.N2 is None]):
            raise ValueError('ERROR: N1 or N2 is None. Cant calculate topology')
        if not per_boundaries:
            self._calculate_topology_notper()
        else:
            self._calculate_topology_per()

    def _calculate_topology_per(self) -> None:
        r"""
        """
        spin_indices, dual_lattice_points, areas1, areas2, polygons1, polygons2, topo_dens = [], [], [], [], [], [], []
        dual_counter = 0
        for idx_a1 in range(self.N1):
            for idx_a2 in range(self.N2):
                #print(f'====a1:{idx_a1}....a2:{idx_a2}======')
                if idx_a1 == self.N1 - 1 and idx_a2 == self.N2 - 1:
                    idx1 = idx_a1 * self.N2 + idx_a2
                    idx2 = idx_a2
                    idx3 = 0
                    idx4 = idx_a1 * self.N2
                    con_vec2 = dual_lattice_points[dual_counter - self.N2] - dual_lattice_points[
                        dual_counter - 2 * self.N2]
                    con_vec1 = dual_lattice_points[dual_counter - 1] - dual_lattice_points[dual_counter - 2]
                    dual_lattice_points.append(dual_lattice_points[dual_counter - 1] + (
                            dual_lattice_points[dual_counter - 1] - dual_lattice_points[dual_counter - 2]))
                    p2 = self.points[idx1] + con_vec2
                    p3 = self.points[idx1] + con_vec1 + con_vec2
                    p4 = self.points[idx1] + con_vec1
                    polygons1.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                      [p2[0], p2[1], p2[2]],
                                      [p3[0], p3[1], p3[2]]])
                    polygons2.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                      [p3[0], p3[1], p3[2]],
                                      [p4[0], p4[1], p4[2]]])
                if idx_a1 == self.N1 - 1 and idx_a2 < self.N2 - 1:
                    idx1 = idx_a1 * self.N2 + idx_a2
                    idx2 = idx_a2
                    idx3 = idx_a2 + 1
                    idx4 = idx_a1 * self.N2 + idx_a2 + 1
                    con_vec = dual_lattice_points[dual_counter - self.N2] - dual_lattice_points[dual_counter - 2 * self.N2]
                    dual_lattice_points.append(dual_lattice_points[dual_counter - self.N2] + con_vec)
                    p3 = self.points[idx4] + con_vec
                    p2 = self.points[idx1] + con_vec
                    polygons1.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                      [p2[0], p2[1], p2[2]],
                                      [p3[0], p3[1], p3[2]]])
                    polygons2.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                      [p3[0], p3[1], p3[2]],
                                      [self.points[idx4, 0], self.points[idx4, 1], self.points[idx4, 2]]])
                if idx_a2 == self.N2 - 1 and idx_a1 < self.N1 - 1:
                    idx1 = idx_a1 * self.N2 + idx_a2
                    idx2 = (idx_a1 + 1) * (self.N2 - 1) + idx_a2 + 1 + idx_a1
                    idx3 = (idx_a1 + 1) * (self.N2 - 1) + 1 + idx_a1
                    idx4 = idx_a1 * self.N2
                    con_vec = dual_lattice_points[dual_counter - 1] - dual_lattice_points[dual_counter - 2]
                    dual_lattice_points.append(dual_lattice_points[dual_counter - 1] + con_vec)
                    p4 = self.points[idx1] + con_vec
                    p3 = self.points[idx2] + con_vec
                    polygons1.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                      [self.points[idx2, 0], self.points[idx2, 1], self.points[idx2, 2]],
                                      [p3[0], p3[1], p3[2]]])
                    polygons2.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                      [p3[0], p3[1], p3[2]],
                                      [p4[0], p4[1], p4[2]]])
                if idx_a1 < self.N1 - 1 and idx_a2 < self.N2 - 1:
                    idx1 = idx_a1 * self.N2 + idx_a2
                    idx2 = (idx_a1 + 1) * (self.N2 - 1) + idx_a2 + 1 + idx_a1
                    idx3 = (idx_a1 + 1) * (self.N2 - 1) + idx_a2 + 2 + idx_a1
                    idx4 = idx_a1 * self.N2 + idx_a2 + 1
                    # calculate the current point of the dual lattice
                    dual_lattice_points.append(
                        np.mean(np.array(
                            [self.points[idx1, :], self.points[idx2, :], self.points[idx3, :], self.points[idx4, :]]),
                            axis=0))
                    polygons1.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                      [self.points[idx2, 0], self.points[idx2, 1], self.points[idx2, 2]],
                                      [self.points[idx3, 0], self.points[idx3, 1], self.points[idx3, 2]]])
                    polygons2.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                      [self.points[idx3, 0], self.points[idx3, 1], self.points[idx3, 2]],
                                      [self.points[idx4, 0], self.points[idx4, 1], self.points[idx4, 2]]])

                #print(f'index 1: {idx1} at {self.points[idx1, :]}')
                #print(f'index 2: {idx2} at {self.points[idx2, :]}')
                #print(f'index 3: {idx3} at {self.points[idx3, :]}')
                #print(f'index 4: {idx4} at {self.points[idx4, :]}')
                #print(f'dual counter: {dual_counter} at {dual_lattice_points[dual_counter]}')
                # save the indices for the current dual lattice point
                spin_indices.append(np.array([idx1, idx2, idx3, idx4]))
                area1 = utils.spherical_area(s1=self.spins[idx1, :], s2=self.spins[idx2, :], s3=self.spins[idx3])
                area2 = utils.spherical_area(s1=self.spins[idx1, :], s2=self.spins[idx3], s3=self.spins[idx4])
                areas1.append(area1)
                areas2.append(area2)
                topo_dens.append((1 / (4 * np.pi)) * (area1 + area2))
                dual_counter = dual_counter + 1
        self._spin_indices = np.array(spin_indices)
        self._topo_dens = np.array(topo_dens)
        self._polygons1 = np.array(polygons1)
        self._polygons2 = np.array(polygons2)
        self._areas1 = np.array(areas1)
        self._areas2 = np.array(areas2)
        self._dual_lattice_points = np.array(dual_lattice_points)
        print(f'length topo dens points: {len(topo_dens)}')
        print(f'length dual latt points: {len(dual_lattice_points)}')

    def _calculate_topology_notper(self) -> None:
        r"""
        Calculate the topology of the given input structure
        """
        spin_indices, dual_lattice_points, areas1, areas2, polygons1, polygons2, topo_dens = [], [], [], [], [], [], []
        for idx_a1 in range(self.N1 - 1):
            for idx_a2 in range(self.N2 - 1):
                # get the indices of the four closest spins
                idx1 = idx_a1 * self.N2 + idx_a2
                idx2 = (idx_a1 + 1) * (self.N2 - 1) + idx_a2 + 1 + idx_a1
                idx3 = (idx_a1 + 1) * (self.N2 - 1) + idx_a2 + 2 + idx_a1
                idx4 = idx_a1 * self.N2 + idx_a2 + 1
                # save the indices for the current dual lattice point
                spin_indices.append(np.array([idx1, idx2, idx3, idx4]))
                # calculate the current point of the dual lattice
                dual_lattice_points.append(
                    np.mean(np.array(
                        [self.points[idx1, :], self.points[idx2, :], self.points[idx3, :], self.points[idx4, :]]),
                        axis=0))
                area1 = utils.spherical_area(s1=self.spins[idx1, :], s2=self.spins[idx2, :], s3=self.spins[idx3])
                area2 = utils.spherical_area(s1=self.spins[idx1, :], s2=self.spins[idx3], s3=self.spins[idx4])
                areas1.append(area1)
                areas2.append(area2)
                polygons1.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                  [self.points[idx2, 0], self.points[idx2, 1], self.points[idx2, 2]],
                                  [self.points[idx3, 0], self.points[idx3, 1], self.points[idx3, 2]]])
                polygons2.extend([[self.points[idx1, 0], self.points[idx1, 1], self.points[idx1, 2]],
                                  [self.points[idx3, 0], self.points[idx3, 1], self.points[idx3, 2]],
                                  [self.points[idx4, 0], self.points[idx4, 1], self.points[idx4, 2]]])
                topo_dens.append((1 / (4 * np.pi)) * (area1 + area2))
        self._spin_indices = np.array(spin_indices)
        self._topo_dens = np.array(topo_dens)
        self._polygons1 = np.array(polygons1)
        self._polygons2 = np.array(polygons2)
        self._areas1 = np.array(areas1)
        self._areas2 = np.array(areas2)
        self._dual_lattice_points = np.array(dual_lattice_points)
        print(f'length topo dens points: {len(topo_dens)}')
        print(f'length dual latt points: {len(dual_lattice_points)}')

    @property
    def dual_lattice_points(self) -> np.ndarray:
        r"""
        Returns:
            the points of the dual lattice
        """
        return self._dual_lattice_points

    @property
    def spin_indices(self) -> np.ndarray:
        r"""
        Returns:
            the indices of the four adjacent spins for the current dual lattice point
        """
        return self._spin_indices

    @property
    def polygons1(self) -> np.ndarray:
        r"""
        Returns:
            the coordinates of the upper triangles for visualizing the topological density
        """
        return self._polygons1

    @property
    def polygons2(self) -> np.ndarray:
        r"""
        Returns:
            the coordinates of the upper triangles for visualizing the topological density
        """
        return self._polygons2

    @property
    def areas1(self) -> np.ndarray:
        r"""
        Returns:
            the spherical area of the triangles associated with polygons 1
        """
        return self._areas1

    @property
    def areas2(self) -> np.ndarray:
        r"""
        Returns:
            the spherical area of the triangles associated with polygons 2
        """
        return self._areas2

    @property
    def topo_dens(self) -> np.ndarray:
        r"""
        Returns:
            the topological density of the dual lattice points
        """
        return self._topo_dens

    @property
    def topological_center(self) -> np.ndarray:
        r"""
        Returns:
            the center of mass with respect to the topological density
        """
        return (1 / self.topologic_charge) * np.sum((self.dual_lattice_points * self.topo_dens[:, None]), axis=0)

    @property
    def topologic_charge(self) -> np.ndarray:
        r"""
        Returns:
            the topologic charge of the lattice
        """
        return np.sum(self.topo_dens)
