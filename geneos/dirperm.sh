#!/bin/bash

# Define the directories to check
directories=(
    "/path/to/dir1"
    "/path/to/dir2"
    "/path/to/dir3"
    "/path/to/dir4"
)

# Rule: Check if "others" have write permission (numeric permission ends with 2, 3, 6, or 7)
is_violate() {
    local perm=$1
    local others_perm=${perm: -1} # Get the last digit (others' permission)
    if [[ $others_perm =~ [2367] ]]; then
        echo "YES"
    else
        echo "NO"
    fi
}

# Print the header
echo "Directory,Permissions,Is_Violate"

# Loop through each directory and generate the report
for dir in "${directories[@]}"; do
    if [[ -d "$dir" ]]; then
        # Get the numeric permissions using stat
        perm=$(stat -c "%a" "$dir")
        # Check if the directory violates the rule
        violate=$(is_violate "$perm")
        # Print the result
        echo "$dir,$perm,$violate"
    else
        echo "$dir,NOT_FOUND,NA"
    fi
done