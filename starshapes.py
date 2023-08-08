#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Inspired by the radiotools package https://github.com/nu-radio/radiotools/
# author: Jelena Köhler, @jelenakhlr
# co-author: Lukas Gülzow, @lguelzow

import numpy as np
from utils.coordtransform import cstransform
from utils.coordtransform import spherical_to_cartesian
import sys

def create_stshp_list(zenith, azimuth, filename="antenna.list", 
                        obslevel=156400.0, # default for Dunhuang, in cm for corsika
                        obsplane = "gp",
                        inclination=61.60523, # default for Dunhuang
                        Rmin=0., Rmax=50000., n_rings=20, # for positions in starshape in cm
                        arm_orientations=np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]), # for positions in starshape in degrees
                        vxB_plot=True
                        ):

    """
    Parameters
    ----------
    zenith :  float (in degrees)
             zenith angle of the incoming signal/air-shower direction (0 deg is pointing vertically upwards)
             Is converted to radians immediately
    azimuth :  float (in degrees)
              azimuth angle of the incoming signal/air-shower direction (0 deg is North, 90 deg is West)
              Is converted to radians immediately
    filename:  string
              should have the extension ".list"
              If the file is supposed to be used with the 
              radio_mpi Corsika generator (https://github.com/fedbont94/Horeka/tree/radio_mpi),
              keep the default filename.
    obsplane :  string
               possible options are:
                  "gp" for antenna positions in the ground plane
                  "sp" for antenna positions in the shower plane, in the air
    inclination :  float (in degrees)
                  Inclination of the magnetic field.
                  It describes the angle between the Earth's surface and the magnetic field lines.
                  The default value is given for GRAND's Dunhuang site
                  Is converted to radians immediately

    Rmin, Rmax, n_rings, arm_orientations : used to calculate the positions of the antennas on the arms of the starshape
            Do not change unless you know what you are doing!
    """
    print("Generating antenna positions in ", obsplane)
    print("zenith: ", zenith)
    print("azimuth: ", azimuth)

    # convert to rad for numpy calculations
    zenith = np.deg2rad(zenith)
    azimuth = np.deg2rad(azimuth)
    # definition of these are in coordtransform.py
    inclination = np.deg2rad(inclination) # default value is for Dunhuang
    declination = np.deg2rad(0.12532) # default value is for Dunhuang

    # define coordinate system transformations
    cst = cstransform(zenith = zenith,
                      azimuth= azimuth,
                      declination=declination, # for Dunhuang
                      inclination=inclination # for Dunhuang
                      )

    # compute translation in x and y
    r = np.tan(zenith) * obslevel
    dx = np.cos(azimuth) * r
    dy = np.sin(azimuth) * r

    # array to save all station positions in
    station_positions_groundsystem = []

    # compute the B field
    B = np.array([0, np.cos(inclination), -np.sin(inclination)])

    # rs = radius slices?
    rs = np.linspace(Rmin, Rmax, n_rings + 1)


    # open the antenna.list file to save the generated starshapes to
    with open(filename, "w") as file:
        for i in np.arange(1, n_rings + 1): # loop over number of antenna rings
                for j in np.arange(len(arm_orientations)): # loop over number of arms
                        station_position = rs[i] * spherical_to_cartesian(np.pi * 0.5, arm_orientations[j])
                        name = "pos_%i_%i_%.0f_%s" % (rs[i], np.rad2deg(arm_orientations[j]), obslevel, obsplane)

                        # ground plane:
                        if obsplane == "gp":
                                pos_2d = cst.transform_from_vxB_vxvxB_2D(station_position)  # position if height in observer plane should be zero
                                # pos_2d[0] += dx
                                # pos_2d[1] += dy
                                
                                # two versions!
                                # keep the same coordinate system and see proper starshapes in antenna_plotter
                                x, y, z = pos_2d[0], pos_2d[1], obslevel
                                # change coordinate system from Auger to Corsika
                                # x, y, z = pos_2d[1], (-1) * pos_2d[0], obslevel

                                station_positions_groundsystem.append([x, y, z])

                                # save the generated starshapes to the antenna.list file
                                file.write(f"AntennaPosition = {x} {y} {z} {name}\n")

                        # shower plane:
                        elif obsplane == "sp":
                                pos = cst.transform_from_vxB_vxvxB(station_position)
                                # pos[0] += dx
                                # pos[1] += dy

                                # two versions!
                                # keep the same coordinate system and see proper starshapes in antenna_plotter
                                x, y, z = pos[0], pos[1], (pos[2] + obslevel)
                                # change coordinate system from Auger to Corsika
                                # x, y, z = pos[1], (-1) * pos[0], (pos[2] + obslevel)

                                station_positions_groundsystem.append([x, y, z])

                                # save the generated starshapes to the antenna.list file
                                file.write(f"AntennaPosition = {x} {y} {z} {name}\n")
                        
                        # dealing with wrong obsplanes:
                        else:
                                sys.exit("Wrong choice of observation plane. Possible options are 'gp' or 'sp'. \n Quitting...")

        print(np.array(station_positions_groundsystem[0:10]))
        print("Saved antenna positions (in cartesian coordinates) to file: ", filename)


    # in case you want to plot the antennas in the shower plane coordinate system
    if vxB_plot==True:
        # open the shower.list file to save the generated starshapes to
        with open("shower.list", "w") as file:
                
            # transform the station positions to vxB system for plot
            shower_plane_system = cst.transform_to_vxB_vxvxB(np.array(station_positions_groundsystem))
            # print(shower_plane_system[0:10])
         
            for i in range(len(shower_plane_system)):
                # save the generated starshapes to the antenna.list file
                file.write(f"AntennaPosition = {shower_plane_system[i, 0]} {shower_plane_system[i, 1]} {shower_plane_system[i, 2]} {name}\n")
            
            print("Saved antenna positions (in vxB_vxvxB coordinates) to file: ", "shower.list")
