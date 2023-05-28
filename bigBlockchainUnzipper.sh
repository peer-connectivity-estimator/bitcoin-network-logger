#!/bin/bash

# Install the prereq with sudo apt-get install p7zip-full

directories=(
"/path/to/ssd1"
"/path/to/ssd2"
# Add more paths as needed
)

target="/path/to/home/directory"
counter=1

# Check all files exist before processing
echo "Checking all files exist before processing..."

while true; do
    # Reset found flag for each iteration
    filefound=false

    # Iterate over directories
    for dir in "${directories[@]}"; do
        # Determine file name based on counter
        if [[ $counter -eq 1 ]]; then
            filename="giantZip.zip"
        else
            filename="giantZip.z$(($counter - 1))"
        fi

        # Check if the file exists in current directory
        if [[ -f "$dir/$filename" ]]; then
            filefound=true
            break
        fi
    done

    # If the file was not found in any directory, print error message and exit
    if [[ $filefound == false ]]; then
        echo "File $filename not found in any directory. Please make sure all files are present before processing."
        exit 1
    fi

    # Increase the counter
    counter=$((counter + 1))
done

echo "All files are present. Starting processing..."

# Reset the counter
counter=1

# Now that all files are confirmed to exist, start processing
while true; do
    # Reset found flag for each iteration
    filefound=false

    # Iterate over directories
    for dir in "${directories[@]}"; do
        # Determine file name based on counter
        if [[ $counter -eq 1 ]]; then
            filename="giantZip.zip"
        else
            filename="giantZip.z$(($counter - 1))"
        fi

        # Check if the file exists in current directory
        if [[ -f "$dir/$filename" ]]; then
            filefound=true

            echo "Processing $dir/$filename"
            mv "$dir/$filename" "$target"
            7z x "$target/$filename" -o"$target"
            rm "$target/$filename"

            # Break the loop as the file is found and processed
            break
        fi
    done

    # If the file was not found in any directory, break the while loop
    if [[ $filefound == false ]]; then
        echo "File $filename not found in any directory."
        break
    fi

    # Increase the counter
    counter=$((counter + 1))
done
