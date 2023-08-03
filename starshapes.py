import numpy as np
import coordtransform
import sys

def create_stshp_list(zenith, azimuth, filename="antenna.list", 
                        obslevel=156400.0, # for Dunhuang, in cm for corsika
                        obsplane = "groundplane",
                        inclination=np.deg2rad(61.60523), # for Dunhuang
                        Rmin=0., Rmax=500., n_rings=20, # for positions in starshape
                        azimuths=np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]) # for positions in starshape
                        ):

    """
    Parameters
    ----------
    zenith : float
            zenith angle of the incoming signal/air-shower direction (0 deg is pointing to the zenith)
    azimuth : float
            azimuth angle of the incoming signal/air-shower direction (0 deg is North, 90 deg is South)
    filename: string
            should have the extension ".list"
            If the file is supposed to be used with the 
            radio_mpi Corsika generator (https://github.com/fedbont94/Horeka/tree/radio_mpi),
            keep the default filename.
    obsplane : string
            possible options are:
                "groundplane" for ground plane
                "showerplane" for shower plane
    inclination : float
            Inclination of the magnetic field.
            It describes the angle between the Earth's surface and the magnetic field lines.
            The default value is given for GRAND's Dunhuang site

    Rmin, Rmax, n_rings, azimuths : used to calculate the positions of the antennas on the arms of the starshape
            Do not change unless you know what you are doing!
    """

    # compute translation in x and y
    r = np.tan(zenith) * obslevel
    dx = np.cos(azimuth) * r
    dy = np.sin(azimuth) * r

    # compute the B field
    B = np.array([0, np.cos(inclination), -np.sin(inclination)])

    # create the coordinate transform
    cs = coordtransform.cstrafo(zenith, azimuth, magnetic_field_vector=B) # TODO: check if this is supposed to be used somewhere

    # rs = radius slices?
    rs = np.linspace(Rmin, Rmax, n_rings + 1)

    
    for i in np.arange(1, n_rings + 1):
        for j in np.arange(len(azimuths)):
            station_position = rs[i] * coordtransform.spherical_to_cartesian(np.pi * 0.5, azimuths[j])
            name = "pos_%i_%i_%.0f_%s" % (rs[i], np.rad2deg(azimuths[j]), obslevel, obsplane)

            # ground plane:
            if obsplane == "groundplane":
                pos_2d = coordtransform.transform_from_vxB_vxvxB_2D(station_position)  # position if height in observer plane should be zero
                pos_2d[0] += dx
                pos_2d[1] += dy
                x, y, z = 100 * pos_2d[1], -100 * pos_2d[0], 100 * obslevel

            # shower plane:
            if obsplane == "showerplane":
                pos = coordtransform.transform_from_vxB_vxvxB(station_position)
                pos[0] += dx
                pos[1] += dy
                x, y, z = 100 * pos[1], -100 * pos[0], 100 * (pos[2] + obslevel)
            
            # dealing with wrong obsplanes:
            else:
                sys.exit("Wrong choice of observation plane. Possible options are 'groundplane' or 'showerplane'. \n Quitting...")

    # save the generated starshapes to the antenna.list file
    with open(filename, "w") as file:
        file.write(f"AntennaPosition = {x} {y} {z} {name}\n")
