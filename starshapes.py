import numpy as np
import coordtransform


def create_stshp_list(zenith, azimuth, filename="antenna.list", 
                        obslevel=1564.0, obsplane = "groundplane",
                        declination=np.deg2rad(-35.7324), 
                        Rmin=0., Rmax=500., n_rings=20,
                        azimuths=np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]) ):

    """
    filename should be a string with the extension .list
    obsplane = "groundplane" for ground plane
    obsplane = "showerplane" for shower plane
    """

    # compute translation in x and y
    r = np.tan(zenith) * obslevel
    dx = np.cos(azimuth) * r
    dy = np.sin(azimuth) * r

    # compute the B field
    B = np.array([0, np.cos(declination), -np.sin(declination)])

    # create the coordinate transform
    cs = coordtransform.cstrafo(zenith, azimuth, magnetic_field_vector=B)

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
                print("Wrong choice of observation plane. Possible options are 'groundplane' or 'showerplane'.")
                print("Quitting...")
                quit()

    # save the generated starshapes to the file
    with open(filename, "w") as file:
        file.write(f"AntennaPosition = {x} {y} {z} {name}\n")
