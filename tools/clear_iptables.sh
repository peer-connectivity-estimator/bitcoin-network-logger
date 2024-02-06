#!/bin/bash

# Zero the packet and byte counters in all chains
sudo iptables -Z

# Flush all rules in the filter table
sudo iptables -F

# Set the default policies for the filter table
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT

# Flush all rules in the nat table
sudo iptables -t nat -F

# Flush all rules in the mangle table
sudo iptables -t mangle -F

# Flush all rules again to catch any that might have been missed
sudo iptables -F

# Delete all user-defined chains
sudo iptables -X

echo "iptables has been reset to default state."
