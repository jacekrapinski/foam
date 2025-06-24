#!/bin/bash

# Directory containing the input files
INPUT_DIR="./results100"

# Python script to run
PYTHON_SCRIPT="simulation.py"

# Loop through all files in the directory
for file in "$INPUT_DIR"/*; do
  if [[ -f "$file" ]]; then  # Check if it's a file (not a directory)
    filename=$(basename "$file")
    echo "Processing: $filename $file"
    python3 "$PYTHON_SCRIPT" "$file"
  fi
done