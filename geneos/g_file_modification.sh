#!/bin/bash

# Get today's date in YYYYMMDD format
TODAY=$(date +"%Y%m%d")

# Define the directory containing files
DIR_PATH="/path/to/your/folder"

# Print CSV Header
echo "FilePath,Filename,Permission,Last_Modified_Time,File_Arrival_Time,IS_Change"

# List files matching the pattern with today's date
find "$DIR_PATH" -type f -name "*_${TODAY}_dat.csv" | while read -r file; do
    FILENAME=$(basename "$file")
    FILEPATH=$(realpath "$file")
    PERMISSION=$(ls -l "$file" | awk '{print $1}')
    LAST_MODIFIED_TIME=$(stat -c "%y" "$file") # Last modified time
    FILE_ARRIVAL_TIME=$(stat -c "%W" "$file")  # File creation time (0 if not available)

    # Convert FILE_ARRIVAL_TIME to readable format
    if [[ "$FILE_ARRIVAL_TIME" -eq 0 ]]; then
        FILE_ARRIVAL_TIME="$LAST_MODIFIED_TIME"  # If not available, use last modified time
    else
        FILE_ARRIVAL_TIME=$(date -d @"$FILE_ARRIVAL_TIME" "+%Y-%m-%d %H:%M:%S")
    fi

    # Determine if the file was modified (compare last modified and arrival time)
    if [[ "$LAST_MODIFIED_TIME" != "$FILE_ARRIVAL_TIME" ]]; then
        IS_CHANGE="YES"
    else
        IS_CHANGE="NO"
    fi

    # Print results in CSV format
    echo "\"$FILEPATH\",\"$FILENAME\",\"$PERMISSION\",\"$LAST_MODIFIED_TIME\",\"$FILE_ARRIVAL_TIME\",\"$IS_CHANGE\""

done
