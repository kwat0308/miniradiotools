import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rc

# mpl setup
mpl.rcParams['lines.markersize'] = 5
rc('font', **{'family':'serif','serif':['Palatino']})
rc('text', usetex = True)

# dark plots (e.g. for slides):
# plt.style.use("dark_background")

if __name__ == "__main__":
    import sys
    print('sys.argv: ', sys.argv)
    path = sys.argv[1] # first argument should be the path to the antenna.list file

    # if the specified path is missing a / at the end, add a / to the end of the path
    if (path[-1]!="/"):
        path = path + "/"
    

    # find the antenna.list file in the given directory
    listfile = glob.glob(path + "*.list")[0] 
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
    
    # groundplane starshapes have "groundplane" in the name
    elif name[0].split("_")[-1] == "groundplane":
        title = " groundplane starshapes"

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
    plt.savefig(savename + "_3D.png", dpi = 300)
    # show the 3D interactive plot
    plt.show()
    plt.close()
