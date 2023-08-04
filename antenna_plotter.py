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
    path = sys.argv[1]

    # if the specified path is missing a / at the end, add a / to the end of the path
    if (path[-1]!="/"):
        path = path + "/"
        
    listfile = glob.glob(path + "*.list")[0] # find the antenna.list file in the given directory
    print("Found file: ", listfile)
    fname = listfile.split(".list")[0].split("/")[-1] # remove path and .list extension
    savename = listfile.split(".list")[0] # remove the .list extension

    # read the file
    file = np.genfromtxt(listfile, delimiter = " ")

    # file[:,0] and file[:,1]: "Antennabla = ..."
    x = file[:,2] # x coord
    y = file[:,3] # y coord
    z = file[:,4] # z coord - height
    name = file[:,5] # name of the antenna

    plt.title(fname + " 2D")
    plt.scatter(x, y, color = "hotpink")
    plt.savefig(savename + "_2D.png", dpi = 300)
    plt.close()

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    plt.title(fname + " 3D")
    ax.scatter(x, y, z, color="hotpink")
    plt.savefig(savename + "_3D.png", dpi = 300)
    plt.show()
    plt.close()
