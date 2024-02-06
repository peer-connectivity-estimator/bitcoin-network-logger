#!/bin/bash

# Display network interfaces
ifconfig

# Ask the user to confirm the network interface
echo "Please enter the network interface from the above list that you wish to configure (default is enp0s3):"
read interface

./clear_iptables.sh

# Set default interface if none specified
if [ -z "$interface" ]; then
	interface="enp0s3"
fi

echo "Configuring iptables for interface: $interface"

# iptables configuration
sudo iptables -P FORWARD DROP # We aren't a router
sudo iptables -A INPUT -i "$interface" -m iprange --src-range 10.0.2.1-10.0.2.255 -j ACCEPT

# Accept all incoming and outgoing traffic to and from localhost (127.0.0.1)
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT

sudo iptables -P INPUT DROP # Drop everything we don't accept
sudo iptables -P OUTPUT ACCEPT # Default OUTPUT policy (adjust if needed)

echo "iptables configuration updated."
