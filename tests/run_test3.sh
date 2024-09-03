#!/bin/bash

# Test 3 :  Test the bash executable and dependencies
../run_perm_lip.sh -f inputs/test3/parameters.in

# Define the base directory and all files to check
BASE_DIR="outputs/test3"
FILES=(
    "$BASE_DIR/sub1/limits_SC8_6chnd_sub1.csv"
    "$BASE_DIR/sub1/permeation_SC8_6chnd_sub1.csv"
    "$BASE_DIR/sub1/permeation_SC8_6chnd_sub1.log"
    "$BASE_DIR/sub2/limits_SC8_6chnd_sub2.csv"
    "$BASE_DIR/sub2/permeation_SC8_6chnd_sub2.csv"
    "$BASE_DIR/sub2/permeation_SC8_6chnd_sub2.log"
)

# Flag to track overall success
ALL_PRESENT=true

# Check if each file exists
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Missing: $file"
        ALL_PRESENT=false
    fi
done

# Print overall result
if [ "$ALL_PRESENT" = true ]; then
    echo "All files are present. Test passed successfully."
else
    echo "Some files are missing."
    exit 1
fi