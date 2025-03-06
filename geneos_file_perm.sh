#!/bin/bash

# Define your files to monitor
FILES=("/path/to/file1" "/path/to/file2" "/path/to/file3")

# Set the expected permission
EXPECTED_PERMISSIONS="755"

# Loop through each file and check permissions
for FILE in "${FILES[@]}"; do
    FILE_PERMISSIONS=$(stat -c "%a" "$FILE")
    
    if [ "$FILE_PERMISSIONS" != "$EXPECTED_PERMISSIONS" ]; then
        echo "Permission change detected on $FILE: $FILE_PERMISSIONS"
        exit 1
    fi
done

echo "All files have correct permissions."
exit 0