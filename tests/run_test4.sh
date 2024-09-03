#!/bin/bash

# Define the output directory and expected files
OUTPUT_DIR="outputs/test4"
FILES=(
    "permeation_cumul_SC8.pdf"
    "permeation_cumul_SC8.png"
    "permeation_cumul_SC8.xvg"
    "permeation_selec_SC8.sel"
)

# Run the Python script to generate the files
python ../plot_perm_tot.py -o "$OUTPUT_DIR" inputs/test4/permeation_SC8.csv SC8

# Check if the output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Output directory $OUTPUT_DIR does not exist."
    exit 1
fi

# Check for each expected file
for file in "${FILES[@]}"; do
    if [ ! -f "$OUTPUT_DIR/$file" ]; then
        echo "Missing: $OUTPUT_DIR/$file"
        exit 1
    fi
done

echo "All expected files are present. Test suceed !"
