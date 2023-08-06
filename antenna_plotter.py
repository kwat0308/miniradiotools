#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: Jelena Köhler, @jelenakhlr
# co-author: Lukas Gülzow, @lguelzow

import numpy as np
import matplotlib.pyplot as plt
from optparse import OptionParser
import sys

# dark plots (e.g. for slides):
# plt.style.use("dark_background")

parser = OptionParser()
parser.add_option("--path", "-p", "--list", "-l", type="str", dest="list", metavar="FILE",
                  help="Specify the full path to the desired .list file.")
parser.add_option("--directory", "--dir", "-d", type="str", dest="dir", metavar="PATH",
                  help="Specify the path of the directory where the desired .list file is located.\n WARNING: This is only possible, if the directory contains ONE .list file.")
parser.add_option("--plotname", "--name", type="str", dest="name",
                  help="Optional: The title of the plot. If not provided, the plot will be named after the antenna names in the file.")

(options, args) = parser.parse_args()

if __name__ == "__main__":
    # find the antenna.list file in the given directory
    if options.list:
        listfile=options.list
    elif options.dir:
        listfile=options.dir
    else:
        sys.exit("No .list file found. Quitting...")

    
    print("Found file: ", listfile)
    fname = listfile.split(".list")[0].split("/")[-1] # remove path and .list extension
    savename = listfile.split(".list")[0] # remove the .list extension

    # read the file
    file = np.genfromtxt(listfile, delimiter = " ")
    # file[:,0] and file[:,1]: "Antennabla = ..."
    x = file[:,2] # x coord
    y = file[:,3] # y coord
    z = file[:,4] # z coord - height
    name = np.loadtxt(listfile, usecols=5, dtype=str) # read names of the antennas


    # * get info from the antenna names for better plot titles * #
    # showerplane starshapes have "showerplane" in the name
    if name[0].split("_")[-1] == "showerplane":
        title = " showerplane starshapes"
    
    # if file was created with the original radiotools, "sp" is showerplane
    elif name[0].split("_")[-1] == "sp":
        title = " showerplane starshapes"

    # groundplane starshapes have "groundplane" in the name
    elif name[0].split("_")[-1] == "groundplane":
        title = " groundplane starshapes"

    # if file was created with the original radiotools, "gp" is groundplane
    elif name[0].split("_")[-1] == "gp":
        title = " groundplane starshapes"

    # if a name for the plot was passed as option, use that:
    elif options.name:
        title = options.name

    # if it's something else, just use the name of the first antenna
    else: 
        title = name[0]
    # * * * * * * * * * * * * * * * *

    # plot 2D
    plt.title(fname + title + " 2D")
    plt.scatter(x, y, color = "hotpink")
    plt.savefig(savename + "_2D.png", dpi = 300)
    plt.close()

    # plot 3D
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    plt.title(fname + title + " 3D")
    ax.scatter(x, y, z, color="hotpink")

    # axis labels
    ax.set_xlabel('vxB [cm]', fontsize=10, rotation=150)
    ax.set_ylabel('vxvxB [cm]', fontsize=10)
    ax.set_zlabel('v[cm]', fontsize=10, rotation=60)

    plt.savefig(savename + "_3D.png", dpi = 300)
    # show the 3D interactive plot
    plt.show()
    plt.close()
