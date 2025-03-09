#!/bin/bash

# Configuration Variables
paths="/path/to/folder1 /path/to/folder2 /path/to/file.txt"
expected_permissions="755"

# Calculate yesterday's date in seconds since epoch
threshold_seconds=$(date -d "yesterday" +%s)

# Print headers
echo "File,Path,Permissions,Modified,is_permission_change"

# Loop through the paths
for path in $paths; do
  file_name=$(basename "$path")
  file_permissions=$(stat -c "%a" "$path")
  modified_seconds=$(stat -c "%Y" "$path")
  modified_date=$(date -d @$modified_seconds +"%Y-%m-%d %H:%M:%S")

  # Check if modified date is after the threshold and permissions have changed
  if [[ "$modified_seconds" -ge "$threshold_seconds" && "$file_permissions" != "$expected_permissions" ]]; then
    is_permission_change=1
  else
    is_permission_change=0
  fi

  # Print data row
  echo "$file_name,$path,$file_permissions,\"$modified_date\",$is_permission_change"
done