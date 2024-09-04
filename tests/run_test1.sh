#!/bin/bash

# Test 1 : Simple test to see if the number of permeations is correct

# Create output location
mkdir -p outputs/test1

# Define file paths
LOG_FILE="outputs/test1/permeation_SC8.log"
CSV_FILE="outputs/test1/permeation_SC8.csv"

# Run the permeation script
../perm_lip.py -r inputs/test1/ref_SC8_6chnd.gro \
               -f inputs/test1/traj_SC8_6chnd_50ns.xtc \
               -o test1 \
               -x "SC8" \
               -p \
               -t \
               -s 2

# Check if the CSV file exists
if [ -f "$CSV_FILE" ]; then
    LINE_COUNT=$(wc -l < "$CSV_FILE")
    
    # Check if the number of lines is 31 and the log file exists
    if [ "$LINE_COUNT" -eq 31 ] && [ -f "$LOG_FILE" ]; then
        echo "Test passed successfully."
    else
        echo "Test failed."
        exit 1
    fi
else
    echo "Test failed."
    exit 1
fi