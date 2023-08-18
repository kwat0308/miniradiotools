# author: Jelena
# combine coreas_to_hdf5 and fluencemap codes to automatically produce fluencemaps for all showers in a simulation set

import glob
import numpy as np
import subprocess
from optparse import OptionParser

from coreas_to_hdf5_mods import *

# dark plots (e.g. for slides):
# plt.style.use("dark_background")

parser = OptionParser()
parser.add_option("--directory", "--dir", "-d", type="str", dest="directory",
                  help="Specify the full path to the inp directory of the simulation set.\
                  It assumes that the .reas files are in subdirectories of the specified one.\
                  ")

(options, args) = parser.parse_args()

# TODO: read obslevel from file
obslevel = "156400" # Dunhuang

# TODO: read zenith from file
zenith = "65" # in degrees

# TODO: add frequency band as input parameter
flow = "30"
fhigh = "80"
freqband = f"{flow}-{fhigh}"

if __name__ == '__main__':
    print(f"Searching directory {options.directory} for .reas files")
    # find .reas files with glob
    reas_names = glob.glob(options.directory + "/SIM??????.reas")
    print(f"Found {len(reas_names)} showers to plot!")

    # loop over all reas files
    for reas_filename in reas_names:
        print("********************************")
        print(f"Now analyzing {reas_filename}")
        path_to_reas = reas_filename.split("SIM")[-2]
        output_filename_hl = reas_filename.split(".reas")[0] + "_highlevel.hdf5"
        
        # Run coreas_to_hdf5_mods.py
        coreas_to_hdf5 = [
            'python', 'coreas_to_hdf5_mods.py', str(reas_filename), '-hl', '--flow', str(flow), '--fhigh', str(fhigh), 
            "--outputDirectory", str(path_to_reas)
        ]
        subprocess.run(coreas_to_hdf5, check=True)
        print(f"Created {reas_filename}_highlevel.hdf5")

        # Run fluencemap_mods.py
        fluencemap_command = [
            'python', 'fluencemap_mods.py', str(output_filename_hl), str(obslevel), str(freqband), str(zenith)
        ]
        subprocess.run(fluencemap_command, check=True)
        print(f"Plotted fluencemap for {output_filename_hl}")

# TODO: skip if one shower happens to be incomplete. currently this crashes the whole process