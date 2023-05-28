#!/bin/bash

# Install the prereq with sudo apt-get install unzip

fileNameOfTheZipFiles="BitcoinFullLedgerCompressed-5-25-2023"

directories=(
"/media/research/BTC"
"/media/research/SIM/btc"
"/media/research/Windows/btc"
# Add more paths as needed
)

target="/home/research/BitcoinFullLedger"
counter=1
max_counter=459  # Set this to the maximum counter value

# Check all files exist before processing
echo "Checking all files exist before processing..."

while [[ $counter -le $max_counter ]]; do
    # Reset found flag for each iteration
    filefound=false

    # Iterate over directories
    for dir in "${directories[@]}"; do
        # Determine file name based on counter
        if [[ $counter -eq 1 ]]; then
            filename="$fileNameOfTheZipFiles.zip"
        else
            counter_str=$(printf "%02d" $(($counter - 1)))
            filename="$fileNameOfTheZipFiles.z$counter_str"
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
while [[ $counter -le $max_counter ]]; do
    # Reset found flag for each iteration
    filefound=false

    # Iterate over directories
    for dir in "${directories[@]}"; do
        # Determine file name based on counter
        if [[ $counter -eq 1 ]]; then
            filename="$fileNameOfTheZipFiles.zip"
        else
            counter_str=$(printf "%02d" $(($counter - 1)))
            filename="$fileNameOfTheZipFiles.z$counter_str"
        fi

        # Check if the file exists in current directory
        if [[ -f "$dir/$filename" ]]; then
            filefound=true

            echo "Processing $dir/$filename"
            # Move the part to the target directory
            mv "$dir/$filename" "$target"
            
            # Unzip the archive if it's the first part
            if [[ $counter -eq 1 ]]; then
                unzip "$target/$filename" -d "$target"
            fi

            # Remove the part from the target directory
            rm "$target/$filename"

            # Break the loop as the file is found and processed
            break
        fi
    done

    # If the file was not found in any directory, break the while loop
    if [[ $filefound
