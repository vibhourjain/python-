#!/bin/bash

# Configuration Variables
paths="/home/zkajghh/*.log"
expected_permissions="755"

# Calculate yesterday's date in YYYY-MM-DD format
date_threshold=$(date -d "yesterday" +%Y-%m-%d)

# Get yesterday's date in seconds since epoch
threshold_seconds=$(date -d "$date_threshold" +%s)

# Loop through the paths
for path in $paths; do
  file_name=$(basename "$path")
  file_permissions=$(stat -c "%a" "$path")
  modified_seconds=$(stat -c "%Y" "$path")

  if [[ "$modified_seconds" -ge "$threshold_seconds" && "$file_permissions" != "$expected_permissions" ]]; then
    echo "File: $file_name, Path: $path, Permissions: $file_permissions, Modified: $(date -d @$modified_seconds)"
  fi
done