## code from Felix Schlueter
# modified by Jelena
import h5py
import numpy as np
import warnings
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
import matplotlib.ticker as ticker
from mpl_toolkits import mplot3d
import math
from scipy.interpolate import griddata
from radiotools.analyses import radiationenergy

# pretty plots
import cmasher as cmr
import matplotlib as mpl
from matplotlib.pyplot import cm 
from matplotlib import rc
mpl.rcParams['lines.markersize']=5
rc('font', **{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)

            
def read_sliced_radio_shower(input_file,antennalevel):
    corsika = h5py.File(input_file, "r")
    f_coreas = corsika["CoREAS"]
    f_h5_inputs = corsika["inputs"]

    zenith = np.deg2rad(f_h5_inputs.attrs["THETAP"][0])
    azimuth = np.deg2rad(f_h5_inputs.attrs["PHIP"][0])  # convert to auger cs

    # radio obs lvl might differ from particle obs lvl "corsika["inputs"].attrs["OBSLEV"] / 100"
    radio_obs_lvl = f_coreas.attrs["CoreCoordinateVertical"] / 100  # conversion in meter
    core = np.array([0, 0, radio_obs_lvl])

    if "highlevel" not in corsika:
        raise KeyError("No highlevel group present hdf5 file {}".format(input_file))

    # get highlevel information calculated with the coreas_to_hdf5.py converter of the coreas trunk
    f_highlevel = corsika["highlevel"]

    #energy = f_highlevel.attrs["energy"]
    electromagnetic_energy = f_highlevel.attrs["Eem"]
    invisible_energy = f_highlevel.attrs["Einv"]

    # this is calculated from CoREAS using sparse tables. dont trust it!
    # shower.set_parameter(shp.distance_to_shower_maximum_geometric, f_coreas.attrs["DistanceOfShowerMaximum"] / 100)
    xmax = f_highlevel.attrs["gaisser_hillas_dEdX"][2]
    
    print( 'radio_obs_lvl :',  radio_obs_lvl , 'm')

    plane = list(f_highlevel.keys())[0]
    #plane.append(list(f_highlevel.keys())[0])
    radio_obs_lvl = antennalevel
    # change between sp and gp
    plane='obsplane_'+str(int(antennalevel))+'_gp_vB_vvB'

    #plane[2]='obsplane_2000_sp_vB_vvB'
    print('plane:', plane)    

    energy_fluence = np.array(f_highlevel[plane]["energy_fluence_vector"])
    antenna_position = np.array(f_highlevel[plane]["antenna_position"])
    antenna_position_vBvvB= np.array(f_highlevel[plane]["antenna_position_vBvvB"])
    antenna_names = np.array(f_highlevel[plane]["antenna_names"])
    #b = energy_fluence[0][0:2]
    #a = antenna_position[0]

    # rad_en_2D = f_highlevel['obsplane_' + str(radio_obs_lvl) + '_gp_vB_vvB'].attrs['radiation_energy']
    # rad_en_1D = f_highlevel['obsplane_' + str(radio_obs_lvl) + '_gp_vB_vvB'].attrs['radiation_energy_1D']

    # print("radiation energy (2D):", rad_en_2D)
    # print("radiation energy (1D):", rad_en_1D)

    return zenith, azimuth,  xmax, radio_obs_lvl, energy_fluence,antenna_position, antenna_position_vBvvB
    sys.exit('exit test 1')
    #return zenith, azimuth, energy, xmax, radio_obs_lvl, energy_fluence, antenna_position_vBvvB



def selectdata(x,y,limit):
    x2 = []
    y2 = []
    if(len(x)==len(y)):
        for i in range(len(x)-1):
            if(abs(x[i])<limit):
                x2.append(x[i])
                y2.append(y[i])
    else:
        print("in selectdata| wrong input!")
    return x2,y2



def fmt(x, pos):
    a, b = '{:.1e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)
    


def readcoreinfo(fname):
    x, y, z = np.genfromtxt(fname, usecols=(0, 1, 2), unpack=True)
    return x,y,z

# cmaps=['hot','bone','plasma','PuRd','magma','brg', 'gnuplot2_r']
interp= [None, 'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
           'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
           'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']



if __name__ == "__main__":
    import sys
    print('sys.argv: ', sys.argv)
    fname = sys.argv[1] #path to file
    obslev_radio= int(sys.argv[2]) #obs level
    freqband = sys.argv[3] #frequency band of hdf5
    # pltname = sys.argv[4] #name for plot
    zen = sys.argv[4] #zenith
    # if fname[-14:] != "highlevel.hdf5":
    #     sys.exit("Input is not a *highlevel.hdf5 file. Please execute the file as the following:"
    #              "python read_highlevel_hdf5.py SIM*_highlevel.hdf5")
    
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    zenith, azimuth, xmax, radio_obs_lvl, energy_fluence, antenna_position,antenna_position_vBvvB = read_sliced_radio_shower(fname,obslev_radio)
    #zenith, azimuth, energy, xmax, radio_obs_lvl, energy_fluence, antenna_position_vBvvB = read_sliced_radio_shower(fname)
    y =  energy_fluence[0]+energy_fluence[1]+energy_fluence[2]
 
    a0=antenna_position[:,0]
    a1=antenna_position[:,1]
    a2=antenna_position[:,2]

    # total fluence
    y_total = np.array([(energy_fluence[i, 0] + energy_fluence[i, 1] + energy_fluence[i, 2]) for i in range(len(energy_fluence))])
    # vxB fluence
    y_vb = energy_fluence[:, 0]
    # vxvxB fluence
    y_vvb = energy_fluence[:, 1]
    # v fluence
    y_v = energy_fluence[:, 2]

    # 2 pi * int dr y for each
    # from radiotools?


    d0 = antenna_position_vBvvB[:,0]
    d1 = antenna_position_vBvvB[:,1]
    d2 = antenna_position_vBvvB[:,2]

    
    # print(len(y_total)) #240
    # print(len(d0)) #240

    plt.plot(d0, y_total, ".", label="d0")
    plt.plot(d1, y_total, ".", label="d1")
    plt.savefig(fname+"antenna_position_vBvvB.png")
    plt.close()


    # start setting up the plot
    labelsize = 13
    plotxsize = 18
    N =  200j # N : interpolation grid tile size
    extent=(min(d0),max(d0),min(d1),max(d1))
    xs,ys=np.mgrid[extent[0]:extent[1]:N,extent[2]:extent[3]:N]
    
    my_cmap=plt.get_cmap('cmr.bubblegum')
    # create figure
    fig, ax = plt.subplots(nrows=1, ncols=4, sharex=True, sharey=True, figsize=(30, 8))
    fig.suptitle("fluence maps for " + freqband + "\,MHz" + " at zenith " + zen + r"$^\circ$" + "\n" \
        # + "radio observation level " +  str(radio_obs_lvl) + "\,m" + "\n" \
        # + "(observation level specified as " + str(obslev_radio) + ")"\
                + "radio observation level " +  str(radio_obs_lvl) + "\,m" + "\n" \
                , size=labelsize+8)

    #####
    #subplot 1: total fluence
    ax = plt.subplot(141)
    ax.set_title("total fluence", size=labelsize+8)
    ax.plot(d0,d1,"o",markersize=3)# antennas
    ax.set_xlabel(r"$ position \ \ on \ \ vxB \ \ [m] $", size=labelsize+8)
    ax.set_ylabel(r"$ position \ \ on \ \ vx(vxB) \ \ [m] $", size=labelsize+8)
    ax.set_aspect('equal')

    resampled_total = griddata((d0,d1), y_total,(xs,ys),method='linear')
    sca_total = plt.imshow(resampled_total.T,origin='lower',cmap=my_cmap,extent=extent,interpolation='nearest')

    cbar_total = plt.colorbar(sca_total,aspect=25,shrink=0.75)
    cbar_total.ax.tick_params(labelsize=19) 
    cbar_total.set_label(r'$ Energy \ \ Fluence \ \ [eV/m^2] $',size=15)
    # ax.set_xlim([-max(d0) * 0.5, max(d0) * 0.5])
    # ax.set_ylim([-max(d0) * 0.5, max(d0) * 0.5])

    ######
    # subplot 2: v x B
    ax = plt.subplot(142)
    ax.set_title("v x B", size=labelsize+8)
    ax.plot(d0,d1,"o",markersize=3)
    ax.set_xlabel(r"$ position \ \ on \ \ vxB \ \ [m] $", size=labelsize+8)
    ax.set_ylabel(r"$ position \ \ on \ \ vx(vxB) \ \ [m] $", size=labelsize+8)
    ax.set_aspect('equal')

    resampled_vb = griddata((d0,d1), y_vb,(xs,ys),method='linear')
    sca_vb = plt.imshow(resampled_vb.T,origin='lower',cmap=my_cmap,extent=extent,interpolation='nearest')

    cbar_vb = plt.colorbar(sca_vb,aspect=25,shrink=0.75)
    cbar_vb.ax.tick_params(labelsize=19) 
    cbar_vb.set_label(r'$ Energy \ \ Fluence \ \ [eV/m^2] $',size=15)
    # ax.set_xlim([-max(d0) * 0.5, max(d0) * 0.5])
    # ax.set_ylim([-max(d0) * 0.5, max(d0) * 0.5])

    ######
    # subplot 3: v x v x B
    ax = plt.subplot(143)
    ax.set_title("v x (v x B)", size=labelsize+8)
    ax.plot(d0,d1,"o",markersize=3)
    ax.set_xlabel(r"$ position \ \ on \ \ vxB \ \ [m] $", size=labelsize+8)
    ax.set_ylabel(r"$ position \ \ on \ \ vx(vxB) \ \ [m] $", size=labelsize+8)
    ax.set_aspect('equal')

    resampled_vvb = griddata((d0,d1), y_vvb,(xs,ys),method='linear')
    sca_vvb = plt.imshow(resampled_vvb.T,origin='lower',cmap=my_cmap,extent=extent,interpolation='nearest')

    cbar_vvb = plt.colorbar(sca_vvb,aspect=25,shrink=0.75)
    cbar_vvb.ax.tick_params(labelsize=19) 
    cbar_vvb.set_label(r'$ Energy \ \ Fluence \ \ [eV/m^2] $',size=15)
    # ax.set_xlim([-max(d0) * 0.5, max(d0) * 0.5])
    # ax.set_ylim([-max(d0) * 0.5, max(d0) * 0.5])

    ######
    # subplot 4: v
    ax = plt.subplot(144)
    ax.set_title("v", size=labelsize+8)
    ax.plot(d0,d1,"o",markersize=3)

    ax.set_aspect('equal')
    ax.set_xlabel(r"$ position \ \ on \ \ vxB \ \ [m] $", size=labelsize+8)
    ax.set_ylabel(r"$ position \ \ on \ \ vx(vxB) \ \ [m] $", size=labelsize+8)
    

    resampled_v = griddata((d0,d1), y_v,(xs,ys),method='linear')
    sca_v = plt.imshow(resampled_v.T,origin='lower',cmap=my_cmap,extent=extent,interpolation='nearest')

    cbar_v = plt.colorbar(sca_v,aspect=25,shrink=0.75)
    cbar_v.ax.tick_params(labelsize=19) 
    cbar_v.set_label(r'$ Energy \ \ Fluence \ \ [eV/m^2] $',size=15)
    # ax.set_xlim([-max(d0) * 0.5, max(d0) * 0.5])
    # ax.set_ylim([-max(d0) * 0.5, max(d0) * 0.5])

    ######
    # save figure
    fig.tight_layout()
    savename = fname + "fluencemaps_" + "zen" + str(zen) + "_freq" + freqband + "_obslev" + str(obslev_radio) + ".png"
    plt.savefig(savename, dpi=300)
    plt.close()
