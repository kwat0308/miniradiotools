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
                        obslevel=156400.0, # default for Dunhuang, !!in cm!!
                        obsplane = "gp",
                        Auger_input = False, 
                        inclination=61.60523, # default for Dunhuang (in degrees)
                        Rmin=0., Rmax=50000., n_rings=20, # for positions in starshape !!in cm!!
                        arm_orientations=np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]), # for positions in starshape (in degrees)
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
    filename :  string
               should have the extension ".list"
               If the file is supposed to be used with the 
               radio_mpi Corsika generator (https://github.com/fedbont94/Horeka/tree/radio_mpi),
               keep the default filename.
    obslevel :  float (!!in cm!!)
               Observation level of the detector in the vertical direction
    obsplane :  string
               possible options are:
                  "gp" for antennas positioned on the ground plane
                  "sp" for antennas positioned in the shower plane, in the air
    Auger_input : bool (default is False)
                 True -> you are providing input in Auger coordinates
                 False -> you are providing input in Corsika coordinates
    inclination :  float (in degrees)
                  Inclination of the magnetic field.
                  It describes the angle between the Earth's surface and the magnetic field lines.
                  The default value is given for GRAND's Dunhuang site
                  Is converted to radians immediately

    Rmin, Rmax, n_rings, arm_orientations : used to calculate the positions of the antennas on the arms of the starshape !!in cm!!
            Do not change unless you know what you are doing!
    """

    print(f"Generating antenna positions in {obsplane} at {obslevel} cm.")
    print(f"zenith: {zenith} degrees - in Corsika convention")
    print(f"azimuth: {azimuth} degrees - in Corsika convention")

    # convert to rad for numpy calculations, change azimuth to Auger convention (for radiotools)
    zenith = np.deg2rad(zenith)
    azimuth = np.deg2rad(azimuth)

    # definition of inclination and declination are in coordtransform.py
    inclination = np.deg2rad(inclination) # default value is for Dunhuang
    declination = np.deg2rad(0.12532) # default value is for Dunhuang

    # compute the B field
    # is this also in Auger coordinates?
    B_field = np.array([np.cos(inclination), 0, -np.sin(inclination)])
    
    print("B-vector from starshapes", B_field)


    # define angle for Auger rotation 
    # set as 0 degrees if you want normal Corsika input
    if Auger_input == True:
          rot_angle = np.deg2rad(270) # Auger coordinates are Corsika coordinates rotated by -90 degrees
    else:
          rot_angle = 0

    # rotation matrix for transformation between Auger and Corsika coordinate system
    # rotation matrix for rotation around z-axis
    rotation_z_axis = np.array([[np.cos(rot_angle),  (-1) * np.sin(rot_angle), 0], \
                      [np.sin(rot_angle), np.cos(rot_angle), 0], \
                      [0, 0, 1]])
    
    # inverse rotation matrix for magnetic field vector
    inverse_rotation = np.linalg.inv(rotation_z_axis)
    
    # rotate magnetic field vector vertical axis in opposite direction of station coordinates
    # depends on Auger_input
    B_field = np.dot(inverse_rotation, B_field)



    # define coordinate system transformations
    cst = cstransform(zenith = zenith,
                      azimuth= azimuth,
                      declination=declination, # for Dunhuang
                      inclination=inclination,
                      magnetic_field_vector=B_field # for Dunhuang
                      )

    # compute translation in x and y
    r = np.tan(zenith) * obslevel
    dx = np.cos(azimuth) * r
    dy = np.sin(azimuth) * r

    # array to save all station positions in
    station_positions_groundsystem = []

    # rs = radius slices?
    rs = np.linspace(Rmin, Rmax, n_rings + 1)


    # open the antenna.list file to save the generated starshapes to
    with open(filename, "w") as file:
        for i in np.arange(1, n_rings + 1): # loop over number of antenna rings
                for j in np.arange(len(arm_orientations)): # loop over number of arms
                        # generate station positions in shower plane coordinates
                        station_position = rs[i] * spherical_to_cartesian(np.pi * 0.5, arm_orientations[j])
                        name = "pos_%i_%i_%.0f_%s" % (rs[i], np.rad2deg(arm_orientations[j]), obslevel, obsplane)

                        # ground plane:
                        if obsplane == "gp":
                                # transform station positions to ground plane coordinates and set all the z coordinates to 0
                                pos_2d = cst.transform_from_vxB_vxvxB_2D(station_position)
                                # pos_2d[0] += dx
                                # pos_2d[1] += dy
                                
                                # write transformed coordinates into kartesian vector and 
                                # set z coordinate to observation level
                                gp_position = np.array([pos_2d[0], pos_2d[1], obslevel])

                                # apply rotation matrix to stations
                                # Corsika input will stay the same, Auger input will be rotated by -90 degrees
                                gp_position = np.dot(rotation_z_axis, gp_position)

                                # write all station positions into list for later conversion to shower plane coordinates
                                station_positions_groundsystem.append(gp_position)

                                # save the generated starshapes to the antenna.list file
                                # positions in cm
                                file.write(f"AntennaPosition = {gp_position[0]} {gp_position[1]} {gp_position[2]} {name}\n")

                        # shower plane:
                        elif obsplane == "sp":
                                # transform station positions to ground plane coordinates
                                pos = cst.transform_from_vxB_vxvxB(station_position)
                                # pos[0] += dx
                                # pos[1] += dy

                                # write transformed coordinates into kartesian vector and 
                                # add observation level to z coordinate
                                sp_position = np.array([pos[0], pos[1], (pos[2] + obslevel)])

                                # apply rotation matrix to stations
                                # Corsika input will stay the same, Auger input will be rotated by -90 degrees
                                sp_position = np.dot(rotation_z_axis, sp_position)

                                # write all station positions into list for later conversion to shower plane coordinates
                                station_positions_groundsystem.append(sp_position)

                                # save the generated starshapes to the antenna.list file
                                # positions in cm
                                file.write(f"AntennaPosition = {sp_position[0]} {sp_position[1]} {sp_position[2]} {name}\n")
                        
                        # dealing with wrong obsplanes:
                        else:
                                sys.exit("Wrong choice of observation plane. Possible options are 'gp' or 'sp'. \n Quitting...")

        # print(np.array(station_positions_groundsystem[0:10]))
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
                # positions in cm
                file.write(f"AntennaPosition = {shower_plane_system[i, 0]} {shower_plane_system[i, 1]} {shower_plane_system[i, 2]} {name}\n")
            
            print("Saved antenna positions (in vxB_vxvxB coordinates) to file: ", "shower.list")
