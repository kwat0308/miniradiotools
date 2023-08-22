#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Inspired by the radiotools package https://github.com/nu-radio/radiotools/
# author: Jelena Köhler, @jelenakhlr
# co-author: Lukas Gülzow, @lguelzow

import numpy as np
from utils.coordtransform import cstransform
from utils.coordtransform import spherical_to_cartesian
import sys
from radiotools.atmosphere import models

def create_stshp_list(zenith, azimuth, filename="antenna.list", 
                        obslevel=156400.0, # default for Dunhuang, !!in cm!!
                        obsplane = "gp",
                        Auger_CS = True, 
                        inclination=61.60523, # default for Dunhuang (in degrees)
                        Rmin=0., Rmax=50000., n_rings=30, # for positions in starshape !!in cm!!
                        antenna_rings=None, # predefined ring radii for antenna
                        arm_orientations=np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]), # for positions in starshape (in degrees)
                        vxB_plot=False
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
    Auger_CS : bool (default is False)
                 True -> you are providing input in Auger coordinates
                 False -> you are providing input in Corsika coordinates
    inclination :  float (in degrees)
                  Inclination of the magnetic field.
                  It describes the angle between the Earth's surface and the magnetic field lines.
                  The default value is given for GRAND's Dunhuang site
                  Is converted to radians immediately
    Rmin, Rmax, n_rings, arm_orientations : used to calculate the positions of the antennas on the arms of the starshape !!in cm!!
            Do not change unless you know what you are doing!
    antenna_rings :  array of antenna ring radii (in cm!)
         predefined list of antenna ring radii
    """

    # convert to rad for numpy calculations
    zenith = np.deg2rad(zenith)
    azimuth = np.deg2rad(azimuth)

    # definition of inclination and declination are in coordtransform.py
    inclination = np.deg2rad(inclination) # default value is for Dunhuang
    declination = np.deg2rad(0.12532) # default value is for Dunhuang

    # print information about input processing
    print(f"Generating antenna positions in {obsplane} at {obslevel} cm.")
    print(f"zenith: {np.rad2deg(zenith)} degrees - in Corsika convention")

    # define angle for Auger rotation 
    # set as 0 degrees if you want normal Corsika input
    # Auger coordinates are Corsika coordinates rotated by -90 degrees
    # so: x direction = East, y direction = North
    if Auger_CS == True:
          rot_angle = np.deg2rad(270)

          # save corsika azimuth angle for output
          corsika_azimuth = np.round(np.rad2deg(azimuth) - 270, decimals=2)
          # print Corsika input angle for Auger input
          print(f"azimuth: {corsika_azimuth} degrees - in Corsika convention")


    elif Auger_CS == False:
          rot_angle = 0

          # save corsika azimuth angle for output
          corsika_azimuth = np.round(np.rad2deg(azimuth) - 180, decimals=2)
          # print Corsika input angle
          print(f"azimuth: {corsika_azimuth} degrees - in Corsika convention")

    
    else:  # dealing with wrong input choices:
        sys.exit("Invalid input. Possible options for Auger_CS are 'True' or 'False'. \n Quitting...")


    print("These are the angles that should go into the Corsika input file!!!")


    # rotation matrix for transformation between Auger and Corsika coordinate system
    # rotation matrix for rotation around z-axis
    rotation_z_axis = np.array([[np.cos(rot_angle),  (-1) * np.sin(rot_angle), 0], \
                      [np.sin(rot_angle), np.cos(rot_angle), 0], \
                      [0, 0, 1]])
    
    # inverse rotation matrix for magnetic field vector
    inverse_rotation = np.linalg.inv(rotation_z_axis)


    # compute the B field in Corsika system (x direction = North, y direction = West)
    B_field = np.array([np.cos(inclination), 0, -np.sin(inclination)])
    print("Magnetic field vector: ", B_field)
    print("Magnetic field inclination", np.rad2deg(inclination))
    
    # rotate magnetic field vector vertical axis in opposite direction of station coordinates
    # depends on Auger_CS
    B_field = np.dot(inverse_rotation, B_field)

    
    # define coordinate system transformations
    cst = cstransform(zenith = zenith,
                      azimuth= azimuth,
                      declination=declination, # for Dunhuang
                      inclination=inclination,
                      magnetic_field_vector=B_field # for Dunhuang
                      )

    # TODO: add obslevel corsika to inputs
    # compute translation in x and y
    r = np.tan(zenith) * obslevel
    dx = np.cos(azimuth) * r
    dy = np.sin(azimuth) * r

    # array to save all station positions in
    station_positions_groundsystem = []

    # check whether antenna ring radii are provided by input
    if antenna_rings is None:
        antenna_rings = np.linspace(Rmin, Rmax, n_rings + 1)

    # if provided, add an additional antenna in the middle
    else:
        n_rings = len(antenna_rings)
        antenna_rings = np.append(0, antenna_rings)


    # open the antenna.list file to save the generated starshapes to
    with open(filename, "w") as file:
        for i in np.arange(1, n_rings + 1): # loop over number of antenna rings
                for j in np.arange(len(arm_orientations)): # loop over number of arms
                        # generate station positions in shower plane coordinates
                        station_position = antenna_rings[i] * spherical_to_cartesian(np.pi * 0.5, arm_orientations[j])
                        name = "pos_%i_%i_%.0f_%s" % (antenna_rings[i], np.rad2deg(arm_orientations[j]), obslevel, obsplane)

                        # ground plane:
                        if obsplane == "gp":
                                # transform station positions to ground plane coordinates and set all the z coordinates to 0
                                pos_2d = cst.transform_from_vxB_vxvxB_2D(station_position)
                                # pos_2d[0] += dx
                                # pos_2d[1] += dy
                                
                                # write transformed coordinates into kartesian vector and 
                                # set z coordinate to observation level
                                gp_position = np.array([pos_2d[0], pos_2d[1], obslevel])

                                # write all station positions into list for plot in vxB coordinates
                                station_positions_groundsystem.append(gp_position)

                                # apply rotation matrix to stations
                                # Corsika input will stay the same, Auger input will be rotated by -90 degrees
                                gp_position = np.dot(rotation_z_axis, gp_position)

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

                                # write all station positions into list for plot in vxB coordinates
                                station_positions_groundsystem.append(sp_position)

                                # apply rotation matrix to stations
                                # Corsika input will stay the same, Auger input will be rotated by -90 degrees
                                sp_position = np.dot(rotation_z_axis, sp_position)

                                # save the generated starshapes to the antenna.list file
                                # positions in cm
                                file.write(f"AntennaPosition = {sp_position[0]} {sp_position[1]} {sp_position[2]} {name}\n")
                        
                        # dealing with wrong obsplanes:
                        else:
                                sys.exit("Wrong choice of observation plane. Possible options are 'gp' or 'sp'. \n Quitting...")

        print("Saved antenna positions (in groundplane coordinates) to file: ", filename)


    # in case you want to plot the antennas in the shower plane coordinate system
    if vxB_plot==True:
        # open the shower.list file to save the generated starshapes to
        with open("shower.list", "w") as file:
                
            # transform the station positions to vxB system for plot
            shower_plane_system = cst.transform_to_vxB_vxvxB(np.array(station_positions_groundsystem))
         
            for i in range(len(shower_plane_system)):
                # save the generated starshapes to the antenna.list file
                # positions in cm
                file.write(f"AntennaPosition = {shower_plane_system[i, 0]} {shower_plane_system[i, 1]} {shower_plane_system[i, 2]} {name}\n")
            
            print("Saved antenna positions (in vxB_vxvxB coordinates) to file: ", "shower.list")


    # return corsika azimuth angle to for automatically generating corsika input files with the right values
    return corsika_azimuth


def get_rmax(X):
    """ returns maximum axis distance in meter for a given simulation as
    function of the atmosphere X in g/cm2 for a given atmosphere (and zenith angle) """
    # rough hardcoded parametrisation...
    # change to xmax calculation later
    return -148 + 0.712 * X


def cherenkov_radius(x, a=1.00120823e-01, b=6.23688357e+00, c=1.10037370e+02):
    """ rough estimation of radius of the cherenkov ring in meter. x = zenith in radians """
    # rough hardcoded parametrisation...
    # change to xmax calculation later
    return (a * np.exp(b * x) + c)


def get_starshaped_pattern_radii(zenith, obs_level, at=None, atm_model=None):
    # This is just validated for has shower
    # is not even sopisticated
    zenith = np.deg2rad(zenith)
    obs_level = obs_level/100 # convert from cm to m

    if at is None:
        if atm_model is None:
            sys.exit("No proper arguments for get_starshaped_pattern_radii")

        at = models.Atmosphere(atm_model)

    maxX = at.get_atmosphere(zenith, obs_level)

    rmax = get_rmax(maxX) * 100
    r_cherenkov_upper_limit = (cherenkov_radius(zenith) * 1.23 + 80) * 100

    antenna_rings = np.append(0.005 * rmax, np.append(
                   np.linspace(0.01 * rmax, r_cherenkov_upper_limit, 14, endpoint=False),
                   np.linspace(r_cherenkov_upper_limit, rmax, 15)))

    return antenna_rings
