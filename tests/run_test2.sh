#!/bin/bash

# Test 2: Compute the performance of the program with different subgroups  

# Create output location
mkdir -p outputs/test2

# List of subgroups
list_sub="1 2 4"

# Create output directory
mkdir -p outputs/test2

# Run tests and check each step
for sub in $list_sub; do
    # Run the script and capture output
    ../perm_lip.py -r inputs/test1/ref_SC8_6chnd.gro \
                   -f inputs/test1/traj_SC8_6chnd_50ns.xtc \
                   -o test2 \
                   -x "SC8_$sub" \
                   -p \
                   -t \
                   -s $sub > outputs/test2/log_$sub
    
    # Check if the command was successful
    if [ $? -ne 0 ]; then
        echo "Test failed for subgroup $sub."
        exit 1
    fi

    # Check if the log file exists and contains performance data
    performance=$(grep Performance outputs/test2/log_$sub | awk '{print $2}')
    if [ -z "$performance" ]; then
        echo "Performance data missing for subgroup $sub."
        exit 1
    fi

    # Append results to CSV
    echo "$sub,$performance" >> outputs/test2/result_perf.csv
done

# Add header to CSV
sed -i '1i nsub,Performance' outputs/test2/result_perf.csv

echo "Test passed successfully."
