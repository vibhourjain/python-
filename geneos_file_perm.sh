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



•	Return a non-zero exit code to trigger an alert in Geneos.
	•	If no changes are detected, it will return 0 (successful).

2. Configure the FKM Sampler in Geneos

Now, you will configure the FKM Sampler in Geneos to run the script at regular intervals.

Steps:
	1.	Open Geneos Gateway Setup Editor.
	2.	Add a new FKM Sampler:
	•	Sampler Type: Script
	•	Command: Path to the script (e.g., /path/to/monitor_permissions.sh)
	•	Interval: Set a suitable interval (e.g., every minute or every 5 minutes) to monitor the files.
	3.	Configure Text Matching and Alerting:
	•	In the FKM Sampler configuration, set up text matching on the output of the script.
	•	If the script returns "Permission of $file changed", you will want to capture that output and raise an alert in Geneos.
	•	Thresholds: Set a Threshold in Geneos that will trigger an alert if the script exits with a non-zero status (indicating a permission change).
	•	Exit Code 1 means a change was detected.
	4.	Configure Email Alerts (Optional):
	•	You can configure Geneos Alerts to send email notifications based on the threshold or text output from the script.

3. Set Up Email Notification in Geneos (Optional)

You can set up Geneos to send email alerts when permission changes are detected:
	•	Create an Alert in Geneos: You can configure a Threshold or Text Matching alert in Geneos to send an email notification when the FKM Sampler returns the permission change output or a non-zero exit code.

4. Test the Configuration
	1.	Save the configuration and apply it to the Geneos Gateway.
	2.	Monitor the Geneos Active Console to verify that the sampler runs correctly and that alerts are being triggered if file permissions change.
	3.	Check your email inbox to confirm that email notifications are being sent when the script detects changes.

Conclusion

By using this setup:
	•	File permissions in the specified directory are continuously monitored.
	•	Email notifications are sent whenever the permissions change.
	•	Geneos will display alerts with the file name and new permissions.

This approach provides a robust metho
