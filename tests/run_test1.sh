#!/bin/bash

# Test 1 : Simple test to see if the number of permeations is correct

# Output should be :
# --->    30 events of permeation during 50.000 ns!
# ---> Relative number of permeations :     6         

# version of python modules used for this test (through a conda envrionement) :
# - python 3.7.5
# - MDAnalysis 0.20.1
# - numpy 1.17.3
# - matplotlib 3.1.2
# - pandas 0.25.3

# Extract informations from water permeation events through the lipid membrane
../perm_lip.py  -r ref_SC8_6chnd.gro \
                -f traj_SC8_6chnd_50ns.xtc \
                -o test1 \
                -x "SC8" \
                -p \
                -t \
                -s 2
[[ $? -eq 0 ]] || { exit 1; }
# Plot the total number of water permeations with respect to time
python plot_perm_tot.py outputs/test1/permeation_SC8.csv SC8

# For any questions, please contact hardiagon@ibpc.fr
