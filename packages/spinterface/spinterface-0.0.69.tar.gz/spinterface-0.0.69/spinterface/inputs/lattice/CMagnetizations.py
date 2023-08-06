import numpy as np
from spinterface.inputs.lattice.utilities import rotate_spins,rotation_matrix

class Magnetisation_Chimera():
    def __init__(self, X, Y, pos0, m, g, c, w, AFM, uplo, sym_chimera, angl_chimera, elongation, angl_elongation, ab_elongation):
        self.mx, self.my, self.mz = self.build_chimera(X, Y, pos0, m, g, c, w, uplo, AFM, sym_chimera, angl_chimera, elongation, angl_elongation, ab_elongation)

    #==========================================================
    # functions for the polar and azimutal angle of an skyrmion.
    # theta is the standard bogdanov profile
    #==========================================================
    def theta(self, r,c,w):
        comp1 = np.arcsin(np.tanh((-r -c)*2/w))
        comp2 = np.arcsin(np.tanh((-r +c)*2/w))
        return np.pi + comp1 + comp2

    def phi(self, p, m, g):
        return  m*p + g
    #==========================================================
    # here the magnetisation of the skyrmion is build with
    # respect to the profile parameters, helicity and vorticity
    #==========================================================
    def build_chimera(self, X, Y, pos0, m, g, c, w, uplo, AFM, sym_chimera, angl_chimera, elongation, angl_elongation, ab_elongation):
        assert len(X) == len(Y)
        mx, my, mz = [], [], []
        for n in range(len(X)):
            x, y = X[n]-pos0[0], Y[n]-pos0[1]
            r, p = np.sqrt(x**2 + y**2), np.arctan2(y,x)
            # HANDLE ELONGATION OF SKYRMION IF CHOSEN. USE ELLIPTIC PARAMETERISATION FOR RADIAL DISTANCE @r
            if elongation :
                #r = r/(1+exz*abs(np.cos(p-angl_elongation)))
                r = r*(2.-np.sqrt((ab_elongation[0]*np.cos(p-angl_elongation))**2 + (ab_elongation[1]*np.sin(p-angl_elongation))**2))

            # SET AZIMUTHAL ANGLE FOR RADIAL THETA PROFILE
            th = self.theta(r,c,w)
            # chimera case: change vorticity if @p switches half planes
            # the idea is to map @p to @p_tmp, which is 0<p_tmp<pi/2 for every spin, whos vorticity has to be switched
            # EDIT: IF WE WANT TO HAVE SYMMETRIC CHIMERA STATES, WE HAVE TO DEVIDE NOT ONLY INTO HALF PLANES
            #       INSTEAD WE HAVE TO HAVE INTERVALS OF pi/m , WITH VORTICITY @m
            if sym_chimera :
                plane_devider = m
            else :
                plane_devider = 1
            # MAP POLAR ANGLE TO EASIER TO HANDLE INTERVALL
            p_tmp = p + np.pi/2. -angl_chimera
            #p_tmp = p -angl_chimera
            # SINCE p=arctan(x,y) IS IN [-pi, +pi], SUBTRACTING @angl_chimera CAN VIOLATE THESE BOUNDARIES --> HANDLE THIS BY MAPPING BACK
            if p_tmp < -np.pi :
                p_tmp += 2.*np.pi
            # DECIDE; WHICH VORTICITY TO TAKE, DEPENDING ON INTERVALL WE ARE IN RIGHT NOW
            if (p_tmp > 0) and (p_tmp < np.pi/plane_devider) :
                ph = self.phi(p, -m, g + np.pi + 2*angl_chimera)
            else :
                ph = self.phi(p, m, g)

            # alternate sign of spin if @AFM is True
            if AFM :
                sign = (-1)**(n%2 + n//int(np.sqrt(len(X))))
            else :
                sign = 1
            # actually setting of vector components resembling spin
            mx.append(sign*np.sin(th)*np.cos(ph))
            my.append(sign*np.sin(th)*np.sin(ph))
            mz.append(sign*np.cos(th)*float(uplo))
        return mx, my, mz



class Magnetisation_Domainwall():
    def __init__(self, X, Y, r0, direction, width, heli):
        self.mx, self.my, self.mz = self.build_domainwall(X, Y, r0, direction, width, heli)

    def build_domainwall(self, X, Y, r0, direction, width, heli):
        mx, my, mz = [], [], []
        direction = np.asarray(direction)/np.linalg.norm(direction)
        R0 = np.absolute(direction)*r0
        # construct axis for rotation:
        axismat = rotation_matrix([0.0, 0.0, 1.0], heli)
        axis = rotate_spins([direction[0]], [direction[1]], [0.0], axismat)
        axis = np.asarray([axis[0][0], axis[1][0], axis[2][0]])
        # rotate every spin with own matrix according to @theta and @axis
        # the angle theta is given by the DW profile
        for n in range(len(X)):
            r = np.asarray([X[n], Y[n]])
            arg = np.dot(r-R0, direction)/width
            theta = 2.0*np.arctan(np.exp(arg))
            mat = rotation_matrix(axis, theta)
            mag = rotate_spins([0.0] ,[0.0], [1.0], mat)
            mx.append(mag[0][0])
            my.append(mag[1][0])
            mz.append(mag[2][0])
        return mx, my, mz

class Magnetisation_Bimeron():
    def __init__(self, X, Y, pos0, R, a1, a2):
        self.mx, self.my, self.mz = self.build_bimeron(X, Y, pos0, R, a1, a2)

    #===============================================
    #magnetisation direction in spherical coordinates
    #===============================================
    def theta(self, R, c_i, c_j, a1, a2):
        rho = np.sqrt(a1*c_i**2 + a2*c_j**2)
        return np.arccos(R * c_i / (rho**2 + (R**2)/4 ))

    def phi(self, R, c_i, c_j):
        return np.arctan2((c_i - R/2), (c_j)) - np.arctan2((c_i + R/2),(c_j))


    def build_bimeron(self, X, Y, pos0, R, a1, a2):
        r = 1
        assert len(X) == len(Y)
        mx, my, mz = np.zeros(len(X)), np.zeros(len(X)), np.zeros(len(X))
        for n in range(len(X)):
            theta_c = self.theta(R, X[n]-pos0[0], Y[n]-pos0[1], a1, a2)
            phi_c   = self.phi(R, X[n]-pos0[0], Y[n]-pos0[1])
            mx[n] = np.round(r*np.sin(theta_c)*np.cos(phi_c),8)
            my[n] = np.round(r*np.sin(theta_c)*np.sin(phi_c),8)
            mz[n] = np.round(r*np.cos(theta_c),8)
        return mx, my, mz


