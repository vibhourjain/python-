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
exit #!/bin/bash

# Path to the directory containing the files to monitor
DIRECTORY="/path/to/your/directory"

# File to store the last known permissions
PERMISSION_FILE="/path/to/permissions.txt"

# Email configuration
RECIPIENT="your-email@example.com"
SUBJECT="File Permission Changed"
SMTP_SERVER="smtp.example.com"
SENDER="noreply@example.com"

# Expected permissions (e.g., 755)
EXPECTED_PERMISSIONS="755"

# Function to send email
send_email() {
    local file=$1
    local new_permissions=$2
    echo -e "Subject:$SUBJECT\n\nThe permission of file $file has changed. New permissions: $new_permissions" | sendmail -S $SMTP_SERVER -f $SENDER $RECIPIENT
}

# Check if the permissions file exists
if [[ ! -f $PERMISSION_FILE ]]; then
    touch $PERMISSION_FILE
fi

# Iterate over files in the specified directory
for file in "$DIRECTORY"/*; do
    if [[ -f $file ]]; then
        # Get current file permissions (e.g., 755)
        current_permissions=$(stat -c "%a" "$file")

        # Check if the permissions have changed from the last known state
        last_permissions=$(grep "$file" "$PERMISSION_FILE" | cut -d' ' -f2)

        if [[ "$current_permissions" != "$last_permissions" ]]; then
            # Log the new permissions
            echo "$file $current_permissions" >> "$PERMISSION_FILE"
            
            # Send an email notification
            send_email "$file" "$current_permissions"

            # Return a non-zero exit code to trigger an alert in Geneos
            echo "Permission of $file changed to $current_permissions"
            exit 1  # Indicating that permission has changed
        fi
    fi
done

# If no permission change is detected, return 0 (indicating success)
exit 0

