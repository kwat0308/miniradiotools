# author: Jelena
# combine coreas_to_hdf5 and fluencemap codes to automatically produce fluencemaps for all showers in a simulation set

import glob
import numpy as np
import subprocess
from optparse import OptionParser


parser = OptionParser()
parser.add_option("--directory", "--dir", "-d", type="str", dest="directory",
                  help="Specify the full path to the .png files you want to copy.\
                  It assumes that the .png files are in the specified directory.\
                  ")
parser.add_option("--output", "--out", "-o", type="str", dest="output",
                  help="Specify the full path where you want to store the .png files.")

(options, args) = parser.parse_args()


if __name__ == '__main__':
    print(f"Searching directory {options.directory} for .png files")
    # find .png files with glob
    png_names = glob.glob(options.directory + "/*.png")
    # use ** iif you want to go through all subdirectories, use * if you want to go only one level deeper
    print(f"Found {len(png_names)} plots!")

    # loop over all png files
    for png_filename in png_names:
        print("********************************")
        print(f"Now copying {png_filename}")

        # copy png files
        cp_command = ['cp', str(png_filename), str(options.output)]
        subprocess.run(cp_command, check=True)
        print(f"Copied {png_filename} to {options.output}")
