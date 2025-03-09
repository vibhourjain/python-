# #!/bin/bash

# # Configuration Variables
# paths="/path/to/folder1 /path/to/folder2 /path/to/file.txt"
# expected_permissions="755"

# # Calculate yesterday's date in seconds since epoch
# threshold_seconds=$(date -d "yesterday" +%s)

# # Print headers
# echo "File,Path,Permissions,Modified,is_permission_change"

# # Loop through the paths
# for path in $paths; do
  # file_name=$(basename "$path")
  # file_permissions=$(stat -c "%a" "$path")
  # modified_seconds=$(stat -c "%Y" "$path")
  # modified_date=$(date -d @$modified_seconds +"%Y-%m-%d %H:%M:%S")

  # # Check if modified date is after the threshold and permissions have changed
  # if [[ "$modified_seconds" -ge "$threshold_seconds" && "$file_permissions" != "$expected_permissions" ]]; then
    # is_permission_change=1
  # else
    # is_permission_change=0
  # fi

  # # Print data row
  # echo "$file_name,$path,$file_permissions,\"$modified_date\",$is_permission_change"
# done


# ## Version 3: based on filename

# #!/bin/bash

# # Configuration Variables
# paths="/path/to/folder1 /path/to/folder2" # Directories to search
# file_pattern="*.txt" # Pattern to match filenames (e.g., *.txt, log-*.log)
# expected_permissions="755"

# # Calculate yesterday's date in seconds since epoch
# threshold_seconds=$(date -d "yesterday" +%s)

# # Print headers
# echo "File,Path,Permissions,Modified,is_permission_change"

# # Loop through the directories
# for dir in $paths; do
  # # Find files matching the pattern within the directory
  # find "$dir" -type f -name "$file_pattern" -printf "%p\n" | while read path; do
    # file_name=$(basename "$path")
    # file_permissions=$(stat -c "%a" "$path")
    # modified_seconds=$(stat -c "%Y" "$path")
    # modified_date=$(date -d @$modified_seconds +"%Y-%m-%d %H:%M:%S")

    # if [[ "$modified_seconds" -ge "$threshold_seconds" && "$file_permissions" != "$expected_permissions" ]]; then
      # is_permission_change=1
    # else
      # is_permission_change=0
    # fi

    # echo "$file_name,$path,$file_permissions,\"$modified_date\",$is_permission_change"
  # done
# done

# # Version 4: different path and pattern
# #!/bin/bash

# # Configuration Variables
# paths=(
  # "/to/monitor/path1"
  # "/to/monitor/path2"
# )

# patterns=(
  # "trade_pattern1_*.log"
  # "orders_pattern1_*.log"
  # "recon_pattern1_*.log"
  # "recon_pattern2_*.log"
  # "settle_pattern1_*.log"
  # "settle_trade_pattern1_*.log"
# )

# expected_permissions="755"

# # Calculate yesterday's date in seconds since epoch
# threshold_seconds=$(date -d "yesterday" +%s)

# # Print headers
# echo "File,Path,Permissions,Modified,is_permission_change"

# # Loop through the paths
# for dir in "${paths[@]}"; do
  # # Loop through the patterns
  # for pattern in "${patterns[@]}"; do
    # # Find files matching the pattern within the directory
    # find "$dir" -type f -name "$pattern" -printf "%p\n" | while read path; do
      # file_name=$(basename "$path")
      # file_permissions=$(stat -c "%a" "$path")
      # modified_seconds=$(stat -c "%Y" "$path")
      # modified_date=$(date -d @$modified_seconds +"%Y-%m-%d %H:%M:%S")

      # if [[ "$modified_seconds" -ge "$threshold_seconds" && "$file_permissions" != "$expected_permissions" ]]; then
        # is_permission_change=1
      # else
        # is_permission_change=0
      # fi

      # echo "$file_name,$path,$file_permissions,\"$modified_date\",$is_permission_change"
    # done
  # done
# done


# Version 5
# Consider only working days

#!/bin/bash

# Configuration Variables
path_patterns=(
  "/to/monitor/path1/trade_pattern1_*.log"
  "/to/monitor/path1/orders_pattern1_*.log"
  "/to/monitor/path2/recon_pattern1_*.log"
  "/to/monitor/path2/recon_pattern2_*.log"
  "/to/monitor/path2/settle_pattern1_*.log"
  "/to/monitor/path2/settle_trade_pattern1_*.log"
)

expected_permissions="755"

# Calculate the start date (Friday)
current_day=$(date +%w) # 0 (Sunday) to 6 (Saturday)

if [[ $current_day -eq 1 ]]; then # Monday
  start_date=$(date -d "3 days ago 00:00:00" +%Y-%m-%d\ %H:%M:%S)
elif [[ $current_day -eq 0 ]]; then # Sunday
  start_date=$(date -d "2 days ago 00:00:00" +%Y-%m-%d\ %H:%M:%S)
elif [[ $current_day -eq 6 ]]; then # Saturday
  start_date=$(date -d "1 days ago 00:00:00" +%Y-%m-%d\ %H:%M:%S)
else # Tuesday to Friday
  start_date=$(date -d "yesterday 00:00:00" +%Y-%m-%d\ %H:%M:%S)
fi

# Print headers
echo "File,Path,Permissions,Modified,is_permission_change"

# Loop through the path_patterns array
for path_pattern in "${path_patterns[@]}"; do
  # Extract path and pattern
  path=$(dirname "$path_pattern")
  pattern=$(basename "$path_pattern")

  # Find files matching the pattern within the directory and modified since the start date
  find "$path" -type f -name "$pattern" -newermt "$start_date" -printf "%p\n" | while read file_path; do
    file_name=$(basename "$file_path")
    file_permissions=$(stat -c "%a" "$file_path")
    modified_seconds=$(stat -c "%Y" "$file_path")
    modified_date=$(date -d @$modified_seconds +"%Y-%m-%d %H:%M:%S")

    if [[ "$file_permissions" != "$expected_permissions" ]]; then
      is_permission_change=1
    else
      is_permission_change=0
    fi

    echo "$file_name,$file_path,$file_permissions,\"$modified_date\",$is_permission_change"
  done
done