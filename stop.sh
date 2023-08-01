#!/bin/bash

RPC_USER="cybersec"
RPC_PASSWORD="kZIdeN4HjZ3fp9Lge4iezt0eJrbjSi8kuSuOHeUkEUbQVdf09JZXAAGwF3R5R2qQkPgoLloW91yTFuufo7CYxM2VPT7A5lYeTrodcLWWzMMwIrOKu7ZNiwkrKOQ95KGW8kIuL1slRVFXoFpGsXXTIA55V3iUYLckn8rj8MZHBpmdGQjLxakotkj83ZlSRx1aOJ4BFxdvDNz0WHk1i2OPgXL4nsd56Ph991eKNbXVJHtzqCXUbtDELVf4shFJXame"
RPC_PORT="8332"
BITCOIN_CLI="./src/bitcoin-cli -rpcuser=${RPC_USER} -rpcpassword=${RPC_PASSWORD} -rpcport=${RPC_PORT}"

function isBitcoinUp {
  ps -A | grep -q "bitcoind"
  return $?
}

function stopBitcoin {
	secondCount=0
	while isBitcoinUp; do
		$BITCOIN_CLI stop
		sleep 5
		((secondCount+=5))

		if [ $secondCount -ge 300 ]; then # After five minutes, use a harder stop
			pkill -SIGTERM bitcoind
			sleep 5
			((secondCount+=5))
		fi

		if [ $secondCount -ge 600 ]; then # After ten minutes, force shutdown
			pkill -SIGKILL bitcoind
			sleep 5
			((secondCount+=5))
		fi
	done
}

if isBitcoinUp; then
  stopBitcoin
  echo "Bitcoin Core was been successfully stopped."
else
  echo "Bitcoin Core is not running."
fi