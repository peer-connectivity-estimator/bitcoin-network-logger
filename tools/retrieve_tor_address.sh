#!/bin/bash

# Define the HiddenServiceDir relative to the current directory
HIDDEN_SERVICE_DIR="$(pwd)/HiddenServiceDir"

# Path to the hostname file within the HiddenServiceDir
HOSTNAME_FILE="$HIDDEN_SERVICE_DIR/hostname"

# Check if the hostname file exists and print the onion address
if [ -f "$HOSTNAME_FILE" ]; then
    echo "Your Tor onion address is:"
    cat "$HOSTNAME_FILE"
else
    echo "The hostname file does not exist. Make sure your Tor service is configured and running."
fi
