#!/bin/bash

# Directory to search for .reas files
DIRECTORY=/cr/aera02/schlueter/simulations/Rd/RdHasStar/atm27/coreas/

# Check if directory is provided
if [ -z "$DIRECTORY" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Find all .reas files in the specified directory and its subdirectories
find "$DIRECTORY" -type f -name "SIM[0-9][0-9][0-9][0-9][0-9][0-9].reas" | while read -r REAS_FILE; do
    # Run the Python script on each .reas file
    python /cr/users/guelzow/simulations/corsika7/coast/CorsikaOptions/CoREAS/coreas_to_hdf5.py "$REAS_FILE" -hl --flow 100 --fhigh 200 -o /cr/aera02/huege/guelzow/RISE_project/100_200_MHz/
done
