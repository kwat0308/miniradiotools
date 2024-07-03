#!/usr/bin/env python
# -*- coding: utf-8 -*-

# copied and slightly modified from https://github.com/nu-radio/radiotools
# author: Jelena Köhler, @jelenakhlr
# co-author: Lukas Gülzow, @lguelzow


import numpy as np
import math
from numpy.linalg import linalg
import copy
import sys

#* * * * * * * * * * * * * * * * * 

"""
The following functions are copied from radiotools.helper. They are needed for the class below.
"""

def spherical_to_cartesian(zenith, azimuth):
    """
    Make sure that both angles are in radians - numpy uses radians!
    """
    sinZenith = np.sin(zenith)
    x = sinZenith * np.cos(azimuth)
    y = sinZenith * np.sin(azimuth)
    z = np.cos(zenith)
    if hasattr(zenith, '__len__') and hasattr(azimuth, '__len__'):
        return np.array([x, y, z]).T
    else:
        return np.array([x, y, z])
    

#* * * * * * * * * * * * * * * * *
 
"""
The following class is copied and modified from radiotools.coordinatesystems. It is originally called "cstrafo" there.
"""

class cstransform():

    """ class to perform coordinate transformations typically used in air shower radio detection

    the following transformations are implemented:

    From the cartesian ground coordinate system (x: East, y: North, z: up) to
     * to the vxB-vx(vxB) system
     * to the on-sky coordinate system (spherical coordinates eR, eTheta, ePhi)
     * to a ground coordinate system where the y-axis is oriented to magnetic North (instead of geographic North)
     * to a shower plane coordinate system in which the z-axis is parallel to the shower axis
       and the shower axis projected on ground is in the yz-plane 

    and vice versa.
    """

    def __init__(self, zenith, azimuth, 
                 inclination=np.deg2rad(61.60523), # default for Dunhuang
                 declination=np.deg2rad(0.12532), # default for Dunhuang
                 magnetic_field_vector=None):
        
        """ Initialization with signal/air-shower direction and magnetic field configuration.

        All parameters should be specified according to CORSIKA conventions.

        Parameters
        ----------
        zenith : float (in radians)
            zenith angle of the incoming signal/air-shower direction (0 deg is pointing upwards)
        azimuth : float (in radians)
            azimuth angle of the incoming signal/air-shower direction (0 deg is North, 90 deg is West)
        inclination : float (in radians)
            Inclination of the magnetic field
            It describes the angle between the Earth's surface and the magnetic field lines.
            The default value is given for GRAND's Dunhuang site
        declination : float (in radians)
            Declination of the magnetic field
            It describes the angle between the magnetic north of a compass and geographic north.
            The default value is given for GRAND's Dunhuang site
        
        magnetic_field_vector (optional): 3-vector, default None
            the magnetic field vector in the cartesian ground coordinate system,
            if no magnetic field vector is specified, the value is calculated from the given inclination.
        """

        # v points along shower propagation direction
        showeraxis = -1 * spherical_to_cartesian(zenith, azimuth)  # -1 is because shower is propagating towards us

        magnetic_field_normalized = magnetic_field_vector / linalg.norm(magnetic_field_vector)
        vxB = np.cross(showeraxis, magnetic_field_normalized)
        e1 = vxB
        e2 = np.cross(showeraxis, vxB)
        e3 = np.cross(e1, e2)

        e1 /= linalg.norm(e1)
        e2 /= linalg.norm(e2)
        e3 /= linalg.norm(e3)

        self.__transformation_matrix_vBvvB = copy.copy(np.matrix([e1, e2, e3]))
        self.__inverse_transformation_matrix_vBvvB = np.linalg.inv(
            self.__transformation_matrix_vBvvB)

        # initialize transformation matrix to on-sky coordinate system (er, etheta, ephi)
        ct = np.cos(zenith) # cosinus theta 
        st = np.sin(zenith) # sinus theta 
        cp = np.cos(azimuth) # cosinus phi
        sp = np.sin(azimuth) # sinus phi
        e1 = np.array([st * cp, st * sp, ct])
        e2 = np.array([ct * cp, ct * sp, -st])
        e3 = np.array([-sp, cp, 0])
        self.__transformation_matrix_onsky = copy.copy(np.matrix([e1, e2, e3]))
        self.__inverse_transformation_matrix_onsky = np.linalg.inv(
            self.__transformation_matrix_onsky)

        # initialize transformation matrix from magnetic north to geographic north coordinate system
       
        c = np.cos(-1 * declination)
        s = np.sin(-1 * declination)
        e1 = np.array([c, -s, 0])
        e2 = np.array([s, c, 0])
        e3 = np.array([0, 0, 1])
        self.__transformation_matrix_magnetic = copy.copy(
            np.matrix([e1, e2, e3]))
        self.__inverse_transformation_matrix_magnetic = np.linalg.inv(
            self.__transformation_matrix_magnetic)

        # initialize transformation matrix from ground (geographic) cs to ground 
        # cs where x axis points into shower direction projected on ground
        c = np.cos(-1 * azimuth)
        s = np.sin(-1 * azimuth)
        e1 = np.array([c, -s, 0])
        e2 = np.array([s, c, 0])
        e3 = np.array([0, 0, 1])
        self.__transformation_matrix_azimuth = copy.copy(
            np.matrix([e1, e2, e3]))
        self.__inverse_transformation_matrix_azimuth = np.linalg.inv(
            self.__transformation_matrix_azimuth)

        # initialize transformation matrix from ground (geographic) cs to shower plane (early-late) cs
        # rotation along z axis -> shower axis along y axis
        c = np.cos(-azimuth + np.pi / 2)
        s = np.sin(-azimuth + np.pi / 2)
        e1 = np.matrix([[c, -s, 0],
                        [s, c, 0],
                        [0, 0, 1]])

        # rotation along x axis -> rotation in shower plane
        c = np.cos(zenith)
        s = np.sin(zenith)
        e2 = np.matrix([[1, 0, 0],
                        [0, c, -s],
                        [0, s, c]])

        self.__transformation_matrix_early_late = copy.copy(np.matmul(e2, e1))
        self.__inverse_transformation_matrix_early_late = np.linalg.inv(
            self.__transformation_matrix_early_late)



    def __transform(self, positions, matrix):
        return np.squeeze(np.asarray(np.dot(matrix, positions)))

    def transform_from_ground_to_onsky(self, positions):
        """ on sky coordinates are eR, eTheta, ePhi """
        return self.__transform(positions, self.__transformation_matrix_onsky)

    def transform_from_onsky_to_ground(self, positions):
        """ on sky coordinates are eR, eTheta, ePhi """
        return self.__transform(positions, self.__inverse_transformation_matrix_onsky)

    def transform_from_magnetic_to_geographic(self, positions):
        return self.__transform(positions, self.__transformation_matrix_magnetic)

    def transform_from_geographic_to_magnetic(self, positions):
        return self.__transform(positions, self.__inverse_transformation_matrix_magnetic)

    def transform_from_azimuth_to_geographic(self, positions):
        return self.__transform(positions, self.__transformation_matrix_azimuth)

    def transform_from_geographic_to_azimuth(self, positions):
        return self.__transform(positions, self.__inverse_transformation_matrix_azimuth)



    def transform_from_early_late(self, positions, core=None):
        """ transform a single station position or a list of multiple
        station positions back to x,y,z CS
        """
        # to keep positions constant (for the outside)
        if(core is not None):
            positions = np.array(copy.deepcopy(positions))

        # if a single station position is transformed: (3,) -> (1, 3)
        if positions.ndim == 1:
            positions = np.expand_dims(positions, axis=0)

        _, nY = positions.shape
        if(nY != 3):
            sys.exit("Illegal position given")
        else:
            result = []
            for pos in positions:
                temp = self.__transform(
                    pos, self.__inverse_transformation_matrix_early_late)
                if(core is not None):
                    result.append(temp + core)
                else:
                    result.append(temp)

            return np.squeeze(np.array(result))



    def transform_to_early_late(self, positions, core=None):
        """ transform a single station position or a list of multiple
        station positions into the shower plane system
        """
        # to keep positions constant (for the outside)
        if(core is not None):
            positions = np.array(copy.deepcopy(positions))

        # if a single station position is transformed: (3,) -> (1, 3)
        if positions.ndim == 1:
            positions = np.expand_dims(positions, axis=0)

        _, nY = positions.shape
        if(nY != 3):
            sys.exit("Illegal position given")
        else:
            result = []
            for pos in positions:
                if(core is not None):
                    pos -= core
                result.append(self.__transform(
                    pos, self.__transformation_matrix_early_late))
            return np.squeeze(np.array(result))



    def transform_to_vxB_vxvxB(self, station_position, core=None):
        """ transform a single station position or a list of multiple
        station positions into vxB, vxvxB shower plane

        This function is supposed to transform time traces with the shape
        (number of polarizations, length of trace) and a list of station positions
        with the shape of (length of list, 3). The function automatically differentiates
        between the two cases by checking the length of the second dimension. If
        this dimension is '3', a list of station positions is assumed to be the input.
        Note: this logic will fail if a trace will have a shape of (3, 3), which is however
        unlikely to happen.

        """
        # to keep station_position constant (for the outside)
        if(core is not None):
            station_position = np.array(copy.deepcopy(station_position))

        # if a single station position is transformed: (3,) -> (1, 3)
        if station_position.ndim == 1:
            station_position = np.expand_dims(station_position, axis=0)

        nX, nY = station_position.shape
        if(nY != 3):
            return self.__transform(station_position, self.__transformation_matrix_vBvvB)
        else:
            result = []
            for pos in station_position:
                if(core is not None):
                    pos -= core
                result.append(self.__transform(pos, self.__transformation_matrix_vBvvB))
            return np.squeeze(np.array(result))



    def transform_from_vxB_vxvxB(self, station_position, core=None):
        """ transform a single station position or a list of multiple
        station positions back to x,y,z CS

        This function is supposed to transform time traces with the shape
        (number of polarizations, length of trace) and a list of station positions
        with the shape of (length of list, 3). The function automatically differentiates
        between the two cases by checking the length of the second dimension. If
        this dimension is '3', a list of station positions is assumed to be the input.
        Note: this logic will fail if a trace will have a shape of (3, 3), which is however
        unlikely to happen.
        """

        # to keep station_position constant (for the outside)
        if(core is not None):
            station_position = np.array(copy.deepcopy(station_position))

        # if a single station position is transformed: (3,) -> (1, 3)
        if station_position.ndim == 1:
            station_position = np.expand_dims(station_position, axis=0)

        nX, nY = station_position.shape
        if(nY != 3):
            return self.__transform(station_position, self.__inverse_transformation_matrix_vBvvB)
        else:
            result = []
            for pos in station_position:
                temp = self.__transform(
                    pos, self.__inverse_transformation_matrix_vBvvB)
                if(core is not None):
                    result.append(temp + core)
                else:
                    result.append(temp)

            return np.squeeze(np.array(result))



    def transform_from_vxB_vxvxB_2D(self, station_position, core=None):
        """ transform a single station position or a list of multiple
        station positions back to x,y,z CS """
        # to keep station_position constant (for the outside)
        if(core is not None):
            station_position = np.array(copy.deepcopy(station_position))

        # if a single station position is transformed: (3,) -> (1, 3)
        if station_position.ndim == 1:
            station_position = np.expand_dims(station_position, axis=0)

        result = []
        for pos in station_position:
            position = np.array(
                [pos[0], pos[1], self.get_height_in_showerplane(pos[0], pos[1])])
            pos_transformed = self.__transform(
                position, self.__inverse_transformation_matrix_vBvvB)
            if(core is not None):
                pos_transformed += core
            result.append(pos_transformed)

        return np.squeeze(np.array(result))



    def get_height_in_showerplane(self, x, y):
        return -1. * (self.__transformation_matrix_vBvvB[0, 2] * x + self.__transformation_matrix_vBvvB[1, 2] * y) / self.__transformation_matrix_vBvvB[2, 2]



    def get_euler_angles(self):
        R = self.__transformation_matrix_vBvvB
        if(abs(R[2, 0]) != 1):
            theta_1 = -math.asin(R[2, 0])
            theta_2 = math.pi - theta_1
            psi_1 = math.atan2(R[2, 1] / math.cos(theta_1),
                               R[2, 2] / math.cos(theta_1))
            psi_2 = math.atan2(R[2, 1] / math.cos(theta_2),
                               R[2, 2] / math.cos(theta_2))
            phi_1 = math.atan2(R[1, 0] / math.cos(theta_1),
                               R[0, 0] / math.cos(theta_1))
            phi_2 = math.atan2(R[1, 0] / math.cos(theta_2),
                               R[0, 0] / math.cos(theta_2))
        else:
            phi_1 = 0.
            if(R[2, 0] == -1):
                theta_1 = math.pi * 0.5
                psi_1 = phi_1 + math.atan2(R[0, 1], R[0, 2])
            else:
                theta_1 = -1. * math.pi * 0.5
                psi_1 = -phi_1 + math.atan2(-R[0, 1], -R[0, 2])
        return psi_1, theta_1, phi_1
