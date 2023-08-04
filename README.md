# miniradiotools
 
Welcome to the miniradiotools package! It is a minimalistic python package for the basic needs in radio analysis.

Since miniradiotools is meant to be used with CORSIKA (https://web.iap.kit.edu/corsika/usersguide/usersguide.pdf) and its radio extension CoREAS (https://web.ikp.kit.edu/huege/downloads/coreas-manual.pdf), it uses CORSIKA conventions.

It's inspired by the radiotools package: https://github.com/nu-radio/radiotools/


## Input Parameters

The scripts use GRAND's Dunhuang site as reference for default parameters, but they can easily be changed for any other site.

Magnetic field parameters can be looked up here: https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml#igrfwmm

## Scripts
### antenna_plotter.py
Plots antenna positions from antenna.list files with the structure:\
AntennaPosition = {x} {y} {z} {name}

### starshapes.py
Generates antennas in starshape positions for groundplane or showerplane.

### coordtransform.py
Has coordinate transformation functions. Do not touch unless you know what you are doing!

### energy_fluence.py
Calculates energy fluence.

## How to run
### antenna_plotter.py
python antenna_plotter.py <path_to_antenna.list>

### starshapes.py
Using ipython or another python script, call the function

create_stshp_list(\
    zenith, azimuth, filename="antenna.list", \
                        obslevel=156400.0, # for Dunhuang, in cm for corsika\
                        obsplane = "showerplane",\
                        inclination=np.deg2rad(61.60523), # for Dunhuang\
                        Rmin=0., Rmax=500., n_rings=20, # for positions in starshape\
                        azimuths=np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]), # for positions in starshape\
                        vxB_plot=False\
                        )

Zenith and azimuth have to be specified, all other parameters are optional.

**Zenith** and **azimuth** have to be specified in **degrees**, they are converted to radians in the script.

**Inclination** has to be specified in **radians**, but np.deg2rad(<degrees>) is fine as input.

Set *vxb_plot=True* if you want to store the positions in vxb coordinates as well.