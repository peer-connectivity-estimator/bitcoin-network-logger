#!/bin/bash

sudo apt-get install libssl-dev

# Install python-bitcoinlib for Bitcoin-related functionality
python3 -m pip install python-bitcoinlib

# Ensure you have the latest pip and setuptools
python3 -m pip install --upgrade pip setuptools
