import matplotlib.pyplot as plt
import numpy as np

import matplotlib as mpl
from matplotlib import rc
from cycler import cycler
import cmasher as cmr
import glob
from optparse import OptionParser
import sys

# mpl setup
mpl.rcParams['lines.markersize'] = 5
rc('font', **{'family':'serif','serif':['Palatino']})
rc('text', usetex = True)


# my colors
# plt.style.use("dark_background")
n = 3 # Number of colors
new_colors = [plt.get_cmap('cmr.bubblegum_r')(1. * i/n) for i in range(n)]
mpl.rcParams['axes.prop_cycle'] = cycler('color', new_colors)


parser = OptionParser()
parser.add_option("--path", "-p", "--file", "-f", type="str", dest="file", metavar="FILE",
                  help="Specify the path to the desired trace file.")
parser.add_option("--plotname", "--name", type="str", dest="name",
                  help="Optional: The title of the plot. If not provided, the plot will be named after the antenna names in the file.")
parser.add_option("--out", "-o", type="str", dest="out",
                  help="Specify the path to store the output. If not provided, the plot will be stored in the current directory.")


(options, args) = parser.parse_args()

# * * * * * * * * * * * * * * * * *

if __name__ == "__main__":
    # find the antenna.list file in the given directory
    if options.name:
        plotname=options.name
    else:
        plotname=options.file


    plt.rc('font', size=12)
    trace = np.loadtxt(options.file)

    time = trace[:,0]*1E9
    x = trace[:,1]
    y = trace[:,2]
    z = trace[:,3]

    plt.title(plotname)
    plt.plot(time, x, label="x")
    plt.plot(time, y, label="y")
    plt.plot(time, z, label="z")
    plt.legend()
    plt.xlabel("time in ns")
    plt.ylabel("efield in cgs")

    if options.out:
        plt.savefig(f"{options.out}/{plotname}.png", dpi=300)
    else: 
        plt.savefig(f"{plotname}.png", dpi=300)

    plt.show()
    plt.close()

