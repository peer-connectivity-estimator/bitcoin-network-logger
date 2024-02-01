#!/bin/bash

# Check if the script is run as root
if [ "$(id -u)" != "0" ]; then
  echo "This script must be run as root" >&2
  exit 1
fi

sudo apt-get install libssl-dev

# Install python-bitcoinlib for Bitcoin-related functionality
python3 -m pip install python-bitcoinlib

# Ensure you have the latest pip and setuptools
python3 -m pip install --upgrade pip setuptools
