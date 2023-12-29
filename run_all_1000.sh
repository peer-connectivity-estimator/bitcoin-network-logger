#!/bin/bash
# ./run.sh
# ./run.sh --debug=researcher noconsole
# ./run.sh --debug=researcher gui
# ./run.sh --debug=researcher gdb
# ./run.sh gui noconsole gdb

bitcoinParams=""
otherParams=""
datadirParam=""

# Check for '-datadir' parameter
for var in "$@"; do
    if [[ "$var" == -datadir=* ]]; then
        datadirParam="${var#*=}"
        echo "Using provided datadir: $datadirParam"
    elif [[ "$var" == -* ]]; then
        bitcoinParams="$bitcoinParams $var"
    else
        otherParams="$otherParams $var"
    fi
done


echo "Parameters to transfer to Bitcoin: \"$bitcoinParams\""
#exit 1

if [ ! -d "src" ] ; then
	cd .. # If located in src or any other level of depth 1, return
fi


pruned=false
if [ -d /home/$USER/BitcoinFullLedger/ ] && [ ! -f /home/$USER/BitcoinFullLedger/bitcoind.pid ] ; then
	dir=/home/$USER/BitcoinFullLedger
elif [ -d /media/$USER/sf_Bitcoin/blocks/ ] && [ ! -f /media/$USER/sf_Bitcoin/bitcoind.pid ] ; then
	dir=/media/$USER/sf_Bitcoin
elif [ -d /media/$USER/BITCOIN/Bitcoin\ Full\ Ledger/blocks/ ] && [ ! -f /media/$USER/BITCOIN/Bitcoin\ Full\ Ledger/bitcoind.pid ] ; then
	dir=/media/$USER/BITCOIN/Bitcoin\ Full\ Ledger
elif [ -d /media/$USER/BITCOIN/Bitcoin\ Full\ Ledger/Bitcoin\ Full\ Ledger/blocks/ ] && [ ! -f /media/$USER/BITCOIN/Bitcoin\ Full\ Ledger/Bitcoin\ Full\ Ledger/bitcoind.pid ] ; then
	dir=/media/$USER/BITCOIN/Bitcoin\ Full\ Ledger/Bitcoin\ Full\ Ledger
elif [ -d /media/$USER/Blockchains/Bitcoin/blocks/ ] && [ ! -f /media/$USER/Blockchains/Bitcoin/bitcoind.pid ] ; then
	dir=/media/$USER/Blockchains/Bitcoin
elif [ -d "/mnt/610F-0064/blocks/" ] && [ ! -f "/mnt/610F-0064/bitcoind.pid" ] ; then
	dir="/mnt/610F-0064"
elif [ -d /media/$USER/Long\ Term\ Storage/Bitcoin/blocks/ ] && [ ! -f /media/$USER/Long\ Term\ Storage/Bitcoin/bitcoind.pid ] ; then
	dir=/media/$USER/Long\ Term\ Storage/Bitcoin
elif [ -d /media/$USER/Long040Term040Storage/Bitcoin\ Full\ Ledger/blocks/ ] && [ ! -f /media/$USER/Long040Term040Storage/Bitcoin\ Full\ Ledger/bitcoind.pid ] ; then
	dir=/media/$USER/Long040Term040Storage/Bitcoin\ Full\ Ledger


# For running multiple nodes on the same machine
elif [ -d $HOME/.bitcoin/blocks/ ] && [ -f $HOME/.bitcoin/bitcoind.pid ] && 
	 [ -d $HOME/.bitcoin2/blocks/ ] && [ ! -f $HOME/.bitcoin2/bitcoind.pid ] ; then
	dir=$HOME/.bitcoin2
	pruned=true
elif [ -d $HOME/.bitcoin/blocks/ ] && [ -f $HOME/.bitcoin/bitcoind.pid ] && 
	 [ -d $HOME/.bitcoin2/blocks/ ] && [ -f $HOME/.bitcoin2/bitcoind.pid ] && 
	 [ -d $HOME/.bitcoin3/blocks/ ] && [ ! -f $HOME/.bitcoin3/bitcoind.pid ] ; then
	dir=$HOME/.bitcoin3
	pruned=true
elif [ -d $HOME/.bitcoin/blocks/ ] && [ -f $HOME/.bitcoin/bitcoind.pid ] && 
	 [ -d $HOME/.bitcoin2/blocks/ ] && [ -f $HOME/.bitcoin2/bitcoind.pid ] && 
	 [ -d $HOME/.bitcoin3/blocks/ ] && [ -f $HOME/.bitcoin3/bitcoind.pid ] && 
	 [ -d $HOME/.bitcoin4/blocks/ ] && [ ! -f $HOME/.bitcoin4/bitcoind.pid ] ; then
	dir=$HOME/.bitcoin4
	pruned=true

else
	dir=$HOME/.bitcoin
	pruned=true

	if [ ! -d "$dir" ] ; then
		mkdir "$dir"
	fi
fi

# Override 'dir' if '-datadir' parameter was provided
if [ -n "$datadirParam" ]; then
    echo "Overriding with provided datadir: $datadirParam"
    dir="$datadirParam"
fi

if [ -f "$dir/bitcoind.pid" ] ; then
	echo "The directory \"$dir\" has bitcoind.pid, meaning that Bitcoin is already running. In order to ensure that the blockchain does not get corrupted, the program will now terminate."
	exit 1
fi

echo "datadir = $dir"

if [[ " ${bitcoinParams[*]} " =~ " -regtest " ]]; then
	rpcport=18444
	port=18445
	pruned="false"
else
	rpcport=8332
	port=8333
fi


echo "Checking ports..."
while [[ $(lsof -i:$port) ]] | [[ $(lsof -i:$rpcport) ]]; do
	echo "port: $port, rpcport: $rpcport, ALREADY CLAIMED"
	rpcport=$((rpcport+2))
	port=$((port+2))
done
echo "port: $port, rpcport: $rpcport, SELECTED"

# We want to set the bitcoin.conf file regardless of if it exists or not
#if [ ! -f "$dir/bitcoin.conf" ] ; then #| [ port != 8333 ] ; then
	echo "Resetting configuration file"
	echo "server=1" > "$dir/bitcoin.conf"
	echo "rpcuser=cybersec" >> "$dir/bitcoin.conf"
	echo "rpcpassword=kZIdeN4HjZ3fp9Lge4iezt0eJrbjSi8kuSuOHeUkEUbQVdf09JZXAAGwF3R5R2qQkPgoLloW91yTFuufo7CYxM2VPT7A5lYeTrodcLWWzMMwIrOKu7ZNiwkrKOQ95KGW8kIuL1slRVFXoFpGsXXTIA55V3iUYLckn8rj8MZHBpmdGQjLxakotkj83ZlSRx1aOJ4BFxdvDNz0WHk1i2OPgXL4nsd56Ph991eKNbXVJHtzqCXUbtDELVf4shFJXame" >> "$dir/bitcoin.conf"
	echo "rpcport=$rpcport" >> "$dir/bitcoin.conf"
	#echo "rpcallowip=0.0.0.0/0" >> "$dir/bitcoin.conf"
	#echo "rpcbind = 0.0.0.0:8332" >> "$dir/bitcoin.conf"
	#echo "upnp=1" >> "$dir/bitcoin.conf"
	echo "listen=1" >> "$dir/bitcoin.conf"
	echo "" >> "$dir/bitcoin.conf"
	echo "[main]" >> "$dir/bitcoin.conf"
	echo "port=$port" >> "$dir/bitcoin.conf"
	echo "" >> "$dir/bitcoin.conf"
	echo "maxconnections=1000" >> "$dir/bitcoin.conf"
	echo "minconnections=1000" >> "$dir/bitcoin.conf"
	echo "" >> "$dir/bitcoin.conf"
	echo "onion=127.0.0.1:9050" >> "$dir/bitcoin.conf"
	echo "i2psam=127.0.0.1:7656" >> "$dir/bitcoin.conf"
	echo "cjdnsreachable=1" >> "$dir/bitcoin.conf"
	#echo "onlynet=ipv6" >> "$dir/bitcoin.conf"
	#echo "onlynet=onion" >> "$dir/bitcoin.conf"
	#echo "onlynet=i2p" >> "$dir/bitcoin.conf"
	#echo "onlynet=cjdns" >> "$dir/bitcoin.conf"
	
	#echo "dnsseed=0" >> "$dir/bitcoin.conf"
	#echo "dns=0" >> "$dir/bitcoin.conf"
	echo "" >> "$dir/bitcoin.conf"
	echo "rpcport=$rpcport" >> "$dir/bitcoin.conf"
	# echo "[test]" >> "$dir/bitcoin.conf"
	# echo "rpcport=$rpcport" >> "$dir/bitcoin.conf"
	# echo "[regtest]" >> "$dir/bitcoin.conf"
	# echo "rpcport=$rpcport" >> "$dir/bitcoin.conf"
	echo "" >> "$dir/bitcoin.conf"
#fi

if [[ " ${otherParams[*]} " =~ " gui " ]]; then
	if [ "$pruned" == "true" ] ; then
		echo "Pruned mode activated, only keeping 550 block transactions"
		echo

		if [[ " ${otherParams[*]} " =~ " gdb " ]]; then
			gdb -ex run --args src/qt/bitcoin-qt -prune=550 -datadir="$dir" $bitcoinParams --debug=researcher
		else
			src/qt/bitcoin-qt -prune=550 -datadir="$dir" $bitcoinParams #--debug=researcher
		fi
	else
		echo

		if [[ " ${otherParams[*]} " =~ " gdb " ]]; then
			gdb -ex run --args src/qt/bitcoin-qt -datadir="$dir" $bitcoinParams --debug=researcher
		else
			src/qt/bitcoin-qt -datadir="$dir" $bitcoinParams #--debug=researcher
		fi
	fi
else

	# Only open the console if not already open
	if [[ ! " ${otherParams[*]} " =~ " noconsole " ]]; then
		if ! wmctrl -l | grep -q "Bitcoin Core Console Instance" ; then
			# Find the right terminal
			if [ -x "$(command -v mate-terminal)" ] ; then
				mate-terminal -t "Bitcoin Core Console Instance" -- python3 bitcoin_console.py
			elif [ -x "$(command -v xfce4-terminal)" ] ; then
				xfce4-terminal -t "Bitcoin Core Console Instance" -- python3 bitcoin_console.py
			else
				gnome-terminal -t "Bitcoin Core Console Instance" -- python3 bitcoin_console.py
			fi
		fi
	fi

	if [ "$pruned" == "true" ] ; then
		echo "Pruned mode activated, only keeping 550 block transactions"
		echo

		if [[ " ${otherParams[*]} " =~ " gdb " ]]; then
			gdb -ex run --args src/bitcoind -prune=550 -datadir="$dir" $bitcoinParams --debug=researcher
		else
			src/bitcoind -prune=550 -datadir="$dir" $bitcoinParams #--debug=net
		fi
	else
		echo

		if [[ " ${otherParams[*]} " =~ " gdb " ]]; then
			gdb -ex run --args src/bitcoind -datadir="$dir" -txindex=1 $bitcoinParams --debug=researcher
		else
			src/bitcoind -datadir="$dir" -txindex=1 $bitcoinParams
		fi
		# Reindexing the chainstate:
		#src/bitcoind -datadir="/media/sf_Bitcoin" --debug=researcher -reindex-chainstate
		
		# Reindexing the transaction index database
		#src/bitcoind -datadir="$dir" -txindex=1 -reindex $bitcoinParams #--debug=researcher
	fi
fi
