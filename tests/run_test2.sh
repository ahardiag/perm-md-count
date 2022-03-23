#!/bin/bash

# Test 2 : Compute the performances of the program while increasing
#          the number of subgroups  

# version of python modules used for this test (through a conda envrionement) :
# - python 3.7.5
# - MDAnalysis 0.20.1
# - numpy 1.17.3
# - matplotlib 3.1.2
# - pandas 0.25.3

list_sub="1 2 4 8 16"
for sub in $list_sub
do
mkdir -p outputs/test2
../perm_lip.py  -r ref_SC8_6chnd.gro \
                -f traj_SC8_6chnd_50ns.xtc \
                -o test2 \
                -x "SC8_$sub" \
                -p \
                -t \
                -s $sub > outputs/test2/log_$sub
[[ $? -eq 0 ]] || { exit 1; }
done
# For any questions, please contact hardiagon@ibpc.fr

echo "nsub Performance" > outputs/test2/result_perf.csv
for sub in $list_sub
do
echo -n "$sub " >> outputs/test2/result_perf.csv
grep Performance outputs/test2/log_$sub | awk '{print $2}' >> outputs/test2/result_perf.csv
done