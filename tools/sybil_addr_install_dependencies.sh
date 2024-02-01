#!/bin/bash

# Install python-bitcoinlib for Bitcoin-related functionality
python3 -m pip install python-bitcoinlib

# Attempt to install a package named 'bitcoin' if it exists
python3 -m pip install bitcoin

# Ensure you have the latest pip and setuptools
python3 -m pip install --upgrade pip setuptools
