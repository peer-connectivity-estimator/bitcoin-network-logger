# TODO:
#	- Add consideration for peers connecting and disconnecting between samples
#		- Then if getpeerinfo[address] doesn't exist, just copy the stats from above, have a dummy template for if it's never received a getpeerinfo entry before
#	- Add number of peer connections to machine_state
#		- Also consider adding mempool size, MAYBE bucket info too
#	- Add a block_data.csv file too, that logs all the individual info for the blocks with matching timestamps
#		- If using getchaintips, we may even be able to capture forks and stale blocks!

# Sanity checking to ensure that it behaves properly
#	getblockfrompeer "blockhash" peer_id
# Horizontal line --> make sure good score works properly

# -------------------------------------------------------------------

# Logs a lot of Bitcoin info into the Research_Logs folder
# 	For the initial block download, data is written to Research_Logs/IBD_Research_Log/
# 	Otherwise, every month the logging directory changes to Research_Logs/MONTH_YEAR_Research_Log/, and the node restarts

from threading import Timer
import datetime
import json
import os
import platform
import psutil
import re
import shutil
import subprocess
import sys
import time

# The path to copy over the finalized output files (preferably an external storage device)
outputFilesToTransferPath = '/home/linux/Desktop/Research_Logs'

#numSecondsPerSample = 60
numSecondsPerSample = 10

outputFilesToTransfer = []
if not os.path.exists(outputFilesToTransferPath):
	print(f'Note: {outputFilesToTransferPath} does not exist, please set it, then retry.')
	sys.exit()
prevBlockHeight = None
prevBlockHash = None

# Send a command to the linux terminal
def terminal(cmd):
	return os.popen(cmd).read()

# Send a command to the Bitcoin console
def bitcoin(cmd):
	# The following are mock commands to work on the implementation without requiring the node up
	if cmd == 'getchaintips':
		return """[
  {
	"height": 791846,
	"hash": "0000000000000000000458e426948dec172ee891fd6684bcd24bb331819cc5a8",
	"branchlen": 26,
	"status": "headers-only"
  },
  {
	"height": 791820,
	"hash": "000000000000000000048809d486e4cd65ba16dccf7be2f2184e86011746b68b",
	"branchlen": 0,
	"status": "active"
  }
]"""
	elif cmd == 'getblockchaininfo':
		return """{
  "chain": "main",
  "blocks": 791822,
  "headers": 791846,
  "bestblockhash": "00000000000000000003d288db338920ac70cdc18b22680f3433415d8820bcd7",
  "difficulty": 49549703178592.68,
  "time": 1685299124,
  "mediantime": 1685296654,
  "verificationprogress": 0.9999473676814419,
  "initialblockdownload": false,
  "chainwork": "000000000000000000000000000000000000000049e6ee76f6527960df7dbe10",
  "size_on_disk": 780964179,
  "pruned": true,
  "pruneheight": 791456,
  "automatic_pruning": true,
  "prune_target_size": 576716800,
  "warnings": ""
}"""
	elif cmd == 'getmininginfo':
		return """{
  "blocks": 791846,
  "difficulty": 49549703178592.68,
  "networkhashps": 4.062438317971382e+20,
  "pooledtx": 9794,
  "chain": "main",
  "warnings": ""
}"""
	elif cmd == 'getnettotals':
		return """{
  "totalbytesrecv": 279699994,
  "totalbytessent": 76273873,
  "timemillis": 1685311542470,
  "uploadtarget": {
	"timeframe": 86400,
	"target": 0,
	"target_reached": false,
	"serve_historical_blocks": true,
	"bytes_left_in_cycle": 0,
	"time_left_in_cycle": 0
  }
}"""
	elif cmd == 'getblock 0000000000000000000458e426948dec172ee891fd6684bcd24bb331819cc5a8':
		return """{
  "hash": "0000000000000000000458e426948dec172ee891fd6684bcd24bb331819cc5a8",
  "confirmations": 1,
  "height": 791846,
  "version": 1073676288,
  "versionHex": "3fff0000",
  "merkleroot": "811bf4bb860bceabcb05a280599b27208b8f6e6e1b697cee978a7c0a8745f2d5",
  "time": 1685310888,
  "mediantime": 1685307490,
  "nonce": 2067043226,
  "bits": "1705ae3a",
  "difficulty": 49549703178592.68,
  "chainwork": "000000000000000000000000000000000000000049eb280bbadd1efbe547a290",
  "nTx": 3578,
  "previousblockhash": "000000000000000000038acddc18db9829a8e4517d321cf29b88e89eeee05e50",
  "strippedsize": 746634,
  "size": 1753537,
  "weight": 3993439,
  "tx": [
	"ec0dba36a961cf78448b2d4bd5291eed74f3f1ef6e881f770f86cfeebb6dd74b",
	"356d93bafe9506cbc278b1e5ee78621d16c24c522cafd4f68ce20927757b23f0"
  ]
}"""
	elif cmd == 'gettxout ec0dba36a961cf78448b2d4bd5291eed74f3f1ef6e881f770f86cfeebb6dd74b 0':
		return """{
  "bestblock": "00000000000000000000ef263c1a23ba30872e9982352562df5e84115b806050",
  "confirmations": 3,
  "value": 6.75362791,
  "scriptPubKey": {
	"asm": "OP_HASH160 4b09d828dfc8baaba5d04ee77397e04b1050cc73 OP_EQUAL",
	"desc": "addr(38XnPvu9PmonFU9WouPXUjYbW91wa5MerL)#ap48vquh",
	"hex": "a9144b09d828dfc8baaba5d04ee77397e04b1050cc7387",
	"address": "38XnPvu9PmonFU9WouPXUjYbW91wa5MerL",
	"type": "scripthash"
  },
  "coinbase": true
}"""
	elif cmd == 'getblockstats 791846':
		return """{
  "avgfee": 14079,
  "avgfeerate": 50,
  "avgtxsize": 490,
  "blockhash": "0000000000000000000458e426948dec172ee891fd6684bcd24bb331819cc5a8",
  "feerate_percentiles": [
	28,
	37,
	43,
	53,
	81
  ],
  "height": 791846,
  "ins": 6005,
  "maxfee": 797347,
  "maxfeerate": 1948,
  "maxtxsize": 45581,
  "medianfee": 7319,
  "mediantime": 1685307490,
  "mediantxsize": 316,
  "minfee": 1925,
  "minfeerate": 15,
  "mintxsize": 150,
  "outs": 10725,
  "subsidy": 625000000,
  "swtotal_size": 1665404,
  "swtotal_weight": 3641015,
  "swtxs": 3345,
  "time": 1685310888,
  "total_out": 542930816532,
  "total_size": 1753150,
  "total_weight": 3991999,
  "totalfee": 50362791,
  "txs": 3578,
  "utxo_increase": 4720,
  "utxo_size_inc": 366048,
  "utxo_increase_actual": 4702,
  "utxo_size_inc_actual": 363937
}"""
	elif cmd == 'getchaintxstats 1 "0000000000000000000458e426948dec172ee891fd6684bcd24bb331819cc5a8"':
			return """{
  "time": 1685310888,
  "txcount": 844906653,
  "window_final_block_hash": "0000000000000000000458e426948dec172ee891fd6684bcd24bb331819cc5a8",
  "window_final_block_height": 791846,
  "window_block_count": 1,
  "window_tx_count": 3578,
  "window_interval": 745,
  "txrate": 4.802684563758389
}"""
	elif cmd == 'getmempoolinfo':
		return """{
  "loaded": true,
  "size": 12017,
  "bytes": 26109830,
  "usage": 80949680,
  "total_fee": 3.20091376,
  "maxmempool": 300000000,
  "mempoolminfee": 0.00001000,
  "minrelaytxfee": 0.00001000,
  "incrementalrelayfee": 0.00001000,
  "unbroadcastcount": 0,
  "fullrbf": false
}"""
	else:
		return terminal('./src/bitcoin-cli -rpcuser=cybersec -rpcpassword=kZIdeN4HjZ3fp9Lge4iezt0eJrbjSi8kuSuOHeUkEUbQVdf09JZXAAGwF3R5R2qQkPgoLloW91yTFuufo7CYxM2VPT7A5lYeTrodcLWWzMMwIrOKu7ZNiwkrKOQ95KGW8kIuL1slRVFXoFpGsXXTIA55V3iUYLckn8rj8MZHBpmdGQjLxakotkj83ZlSRx1aOJ4BFxdvDNz0WHk1i2OPgXL4nsd56Ph991eKNbXVJHtzqCXUbtDELVf4shFJXame -rpcport=8332 ' + str(cmd))

# 'getblockchaininfo':
# 		return """{
#   "chain": "main",
#   "blocks": 791822,
#   "headers": 791846,
#   "bestblockhash": "00000000000000000003d288db338920ac70cdc18b22680f3433415d8820bcd7",
#   "difficulty": 49549703178592.68,
#   "time": 1685299124,
#   "mediantime": 1685296654,
#   "verificationprogress": 0.9999473676814419,
#   "initialblockdownload": false,
#   "chainwork": "000000000000000000000000000000000000000049e6ee76f6527960df7dbe10",
#   "size_on_disk": 780964179,
#   "pruned": true,
#   "pruneheight": 791456,
#   "automatic_pruning": true,
#   "prune_target_size": 576716800,
#   "warnings": ""
# }"""

# 'getchaintips':
# 		return """getblock[
#   {
# 	"height": 791846,
# 	"hash": "0000000000000000000458e426948dec172ee891fd6684bcd24bb331819cc5a8",
# 	"branchlen": 26,
# 	"status": "headers-only"
#   },
#   {
# 	"height": 791820,
# 	"hash": "000000000000000000048809d486e4cd65ba16dccf7be2f2184e86011746b68b",
# 	"branchlen": 0,
# 	"status": "active"
#   }

# Generate the block information CSV header line
def makeBlockchainStateHeader():
	line = 'Timestamp,'
	line += 'Timestamp (UNIX epoch),'
	line += 'Time Since Last Sample (seconds),'
	line += 'Block Height,'
	line += 'Block Status,'
	line += 'Is Block Stale,'
	line += 'Block Timestamp (UNIX epoch),'
	line += 'Median Timestamp of Last 11 Blocks (to prevent timestamp manipulation),'
	line += 'Transaction Rate (tx/second),'
	line += 'Number of Confirmations,'
	line += 'Block Hash,'
	line += 'Previous Block Hash,'
	line += 'Next Block Hash (if known),'
	line += 'Block Size (bytes),'
	line += 'Block Size Including Segregated Witnesses (bytes),'
	line += 'Stripped Size (excluding witness data) (bytes),'
	line += 'Difficulty,'
	line += 'Chainwork,'
	line += 'Weight (BIP 141),'
	line += 'Version,'
	line += 'Nonce,'
	line += 'Coinbase Subsidy Reward Without Fees (satoshi),'
	line += 'Coinbase Subsidy Reward With Fees (satoshi),'
	line += 'Coinbase Address (Block Solver),'
	line += 'Coinbase Transaction Type (),'
	line += 'Coinbase Transaction Assembly,'
	line += 'Number of Transactions (Tx),'
	line += 'Number of Tx Inputs,'
	line += 'Number of Tx Outputs,'
	line += 'Total Output Value (satoshi),'
	line += 'Total Tx Fees (satoshi),'
	line += 'Average Tx Size (bytes),'
	line += 'Median Tx Size (bytes),'
	line += 'Minimum Tx Size (bytes),'
	line += 'Maximum Tx Size (bytes),'
	line += 'Average Tx Fee (satoshi),'
	line += 'Median Tx Fee (satoshi),'
	line += 'Minimum Tx Fee (satoshi),'
	line += 'Maximum Tx Fee (satoshi),'
	line += 'Average Tx Fee Rate (satoshi/byte),'
	line += '10th Percentile Tx Fee Rate (satoshi/byte),'
	line += '25th Percentile Tx Fee Rate (satoshi/byte),'
	line += 'Median Tx Fee Rate (satoshi/byte),'
	line += '75th Percentile Tx Fee Rate (satoshi/byte),'
	line += '90th Percentile Tx Fee Rate (satoshi/byte),'
	line += 'Minimum Tx Fee Rate (satoshi/byte),'
	line += 'Maximum Tx Fee Rate (satoshi/byte),'
	line += 'Number of Segregated Witness Txs,'
	line += 'Total Segregated Witness Tx Sizes (bytes),'
	line += 'Total Segregated Witness Tx Weights (bytes),'
	return line

# If any new blocks exist, log them
def maybeLogBlock(timestamp, directory, getblockchaininfo, getchaintips):
	global prevBlockHeight, prevBlockHash

#!!!!!!!!!!! put this into the machine state info along with numpeers
# 		elif cmd == 'getblockchaininfo':
# 		return """{
#   "chain": "main",
#   "blocks": 791822,
#   "headers": 791846,
#   "bestblockhash": "00000000000000000003d288db338920ac70cdc18b22680f3433415d8820bcd7",
#   "difficulty": 49549703178592.68,
#   "time": 1685299124,
#   "mediantime": 1685296654,
#   "verificationprogress": 0.9999473676814419,
#   "initialblockdownload": false,
#   "chainwork": "000000000000000000000000000000000000000049e6ee76f6527960df7dbe10",
#   "size_on_disk": 780964179,
#   "pruned": true,
#   "pruneheight": 791456,
#   "automatic_pruning": true,
#   "prune_target_size": 576716800,
#   "warnings": ""
# }"""

	# Quickly check if any new blocks have arrived, if they haven't 
	if prevBlockHash is not None:
		for i, tip in enumerate(getchaintips):
			if tip['status'] == 'active':
				# No new block has been received, return
				if prevBlockHash == tip['hash']: return
				break

	filePath = os.path.join(directory, 'blockchain_state.csv')
	if not os.path.exists(filePath):
		print(f'Creating blockchain state file')
		file = open(filePath, 'w')
		file.write(makeBlockchainStateHeader() + '\n')
		prevLine = ''
	else:
		# Read the last line from the file
		with open(filePath, 'r') as f:
			prevLines = f.readlines()
			if len(prevLines) > 1: prevLine = prevLines[-1].split(',')
			else: prevLine = ''
		# Try to open the file for appending, loop until successful
		attempts = 0
		file = None
		while file is None:
			try:
				attempts += 1
				file = open(filePath, 'a')
			except PermissionError as e:
				print(f'{e}, attempt {attempts}')
				time.sleep(1)
 
	timestampSeconds = (timestamp - datetime.datetime(1970, 1, 1)).total_seconds()
	if prevLine == '':
		timeSinceLastSample = ''
	else: 
		timeSinceLastSample = timestampSeconds - float(prevLine[1])

	# If we're in IBD mode, then don't try to iterate through the blocks between samples, otherwise, if more than one block arrives during a sample they'll all be logged
	allowSkippedBlocks = getblockchaininfo['initialblockdownload']

	# Fetch the active tip from getchaintips
	activeTip = {'height': getblockchaininfo['blocks'], 'hash': getblockchaininfo['bestblockhash'], 'branchlen': 0, 'status': 'active'}
	for i, tip in enumerate(getchaintips):
		if tip['status'] == 'active':
			activeTip = tip
			del getchaintips[i]
			break

	# If we don't want to iterate through the change in blocks, then reset the previous block height
	if prevBlockHeight is None or allowSkippedBlocks:
		prevBlockHeight = activeTip['height']

	# Construct an array of all the tips we want to process
	numBlocks = activeTip['height'] - prevBlockHeight + 1
	tipsToProcess = []
	for height in range(prevBlockHeight, activeTip['height'] + 1):
		tipsToProcess.append({
			'height': height,
			'status': 'active',
			'isStale': '0',
		})
	for tip in getchaintips:
		tipsToProcess.append({
			'height': tip['height'],
			'status': tip['status'],
			'isStale': '1',
		})

	# Now loop through all the tips and log each one as a separate line in the CSV
	lines = ''
	for tip in tipsToProcess:

		height = tip['height']
		tipStatus = tip['status']
		tipIsStale = tip['isStale']

		getblockstats = json.loads(bitcoin(f'getblockstats {height}'))
		blockHash = getblockstats['blockhash']
		getblock = json.loads(bitcoin(f'getblock {blockHash}'))
		coinbaseTransactionHash = getblock['tx'][0]
		gettxout = json.loads(bitcoin(f'gettxout {coinbaseTransactionHash} 0'))

		# Quick sanity checking just to ensure that this is indeed the coinbase transaction
		if gettxout['coinbase'] is not True:
			coinbaseTransactionHash = ''
			gettxout = {
				'bestblock': '',
				'confirmations': '',
				'value': '',
				'scriptPubKey': {
					'asm': '',
					'desc': '',
					'hex': '',
					'address': '',
					'type': ''
				},
				'coinbase': True
			}

		getchaintxstats = json.loads(bitcoin(f'getchaintxstats {numBlocks} "{blockHash}"'))

		lines = str(timestamp) + ','
		lines += str(timestampSeconds) + ','
		lines += str(timeSinceLastSample) + ','
		lines += str(height) + ','
		lines += str(tipStatus) + ','
		lines += str(tipIsStale) + ','
		lines += str(getblock['time']) + ','
		lines += str(getblock['mediantime']) + ',' # Same as getblockstats['mediantime']
		if 'txrate' in getchaintxstats: lines += str(getchaintxstats['txrate']) + ','
		else: lines += ','
		lines += str(getblock['confirmations']) + ','
		lines += str(blockHash) + ','
		if 'previousblockhash' in getblockstats: lines += str(getblockstats['previousblockhash']) + ','
		else: lines += ','
		if 'nextblockhash' in getblockstats: lines += str(getblockstats['nextblockhash']) + ','
		else: lines += ','

		lines += str(getblock['size']) + ','
		lines += str(getblockstats['total_size']) + ','
		lines += str(getblock['strippedsize']) + ','
		lines += str(getblock['difficulty']) + ','
		lines += str(getblock['chainwork']) + ','
		lines += str(getblock['weight']) + ','
		lines += str(getblock['version']) + ','
		lines += str(getblock['nonce']) + ','
		if 'subsidy' in getblockstats: lines += str(getblockstats['subsidy']) + ','
		else: lines += ','
		lines += str(gettxout['value'] * 100000000) + ',' # Same as getblockstats['subsidy'] + getblockstats['totalfee']
		if 'address' in gettxout['scriptPubKey']: lines += str(gettxout['scriptPubKey']['address']) + ','
		else: lines += ','
		lines += str(gettxout['scriptPubKey']['type']) + ','
		lines += str(gettxout['scriptPubKey']['asm']) + ','
		lines += str(getblock['nTx']) + ',' # Same as getblockstats['txs']
		if 'ins' in getblockstats: lines += str(getblockstats['ins']) + ','
		else: lines += ','
		if 'outs' in getblockstats: lines += str(getblockstats['outs']) + ','
		else: lines += ','
		if 'total_out' in getblockstats: lines += str(getblockstats['total_out']) + ','
		else: lines += ','
		if 'totalfee' in getblockstats: lines += str(getblockstats['totalfee']) + ','
		else: lines += ','
		if 'avgtxsize' in getblockstats: lines += str(getblockstats['avgtxsize']) + ','
		else: lines += ','
		if 'mediantxsize' in getblockstats: lines += str(getblockstats['mediantxsize']) + ','
		else: lines += ','
		if 'mintxsize' in getblockstats: lines += str(getblockstats['mintxsize']) + ','
		else: lines += ','
		if 'maxtxsize' in getblockstats: lines += str(getblockstats['maxtxsize']) + ','
		else: lines += ','
		if 'avgfee' in getblockstats: lines += str(getblockstats['avgfee']) + ','
		else: lines += ','
		if 'medianfee' in getblockstats: lines += str(getblockstats['medianfee']) + ','
		else: lines += ','
		if 'minfee' in getblockstats: lines += str(getblockstats['minfee']) + ','
		else: lines += ','
		if 'maxfee' in getblockstats: lines += str(getblockstats['maxfee']) + ','
		else: lines += ','
		if 'avgfeerate' in getblockstats: lines += str(getblockstats['avgfeerate']) + ','
		else: lines += ','
		if 'feerate_percentiles' in getblockstats:
			lines += str(getblockstats['feerate_percentiles'][0]) + ','
			lines += str(getblockstats['feerate_percentiles'][1]) + ','
			lines += str(getblockstats['feerate_percentiles'][2]) + ','
			lines += str(getblockstats['feerate_percentiles'][3]) + ','
			lines += str(getblockstats['feerate_percentiles'][4]) + ','
		else: lines += ',,,,,'
		if 'minfeerate' in getblockstats: lines += str(getblockstats['minfeerate']) + ','
		else: lines += ','
		if 'maxfeerate' in getblockstats: lines += str(getblockstats['maxfeerate']) + ','
		else: lines += ','
		if 'swtxs' in getblockstats: lines += str(getblockstats['swtxs']) + ','
		else: lines += ','
		if 'swtotal_size' in getblockstats: lines += str(getblockstats['swtotal_size']) + ','
		else: lines += ','
		if 'swtotal_weight' in getblockstats: lines += str(getblockstats['swtotal_weight']) + ','
		else: lines += ','
		lines += '\n'

	# Finally, write the blockchain info to the output file
	file.write(lines)

	# Update the previous block info
	prevBlockHash = activeTip['hash']
	prevBlockHeight = activeTip['height']
	return

# Check if the Bitcoin Core instance is up
def bitcoinUp():
	return terminal('ps -A | grep bitcoind').strip() != ''

# Start the Bitcoin Core instance
def startBitcoin():
	print('Starting Bitcoin...')
	subprocess.Popen(['gnome-terminal -t "Bitcoin Core Instance" -- bash ./run.sh'], shell=True)
	rpcReady = False
	while rpcReady is False:
		time.sleep(1)
		try:
			blockHeight = int(bitcoin('getblockcount'))
			rpcReady = True
		except: pass
	print('Bitcoin is up and ready to go')

# Stop the Bitcoin Core instance
def stopBitcoin():
	print('Stopping Bitcoin...')
	secondCount = 0
	while bitcoinUp():
		bitcoin('stop')
		time.sleep(5)
		secondCount += 5
		if secondCount >= 60 * 5: # After five minutes, use a harder stop
			terminal('pkill -SIGTERM bitcoind')
			time.sleep(5)
			secondCount += 5

		if secondCount >= 60 * 10: # After ten minutes, force shutdown
			terminal('pkill -SIGKILL bitcoind')
			time.sleep(5)
			secondCount += 5

# Restart the Bitcoin Core instance
def restartBitcoin():
	print('Restarting Bitcoin...')
	stopBitcoin()
	while not bitcoinUp():
		startBitcoin()

# Generate the machine info CSV header line
def writeInitialMachineInfo(timestamp, directory):
	contents = 'Directory Creation Time (date):\n'
	contents += '\t' + str(timestamp) + '\n'
	contents += '\nOperating System (lsb_release -idrc):\n'
	contents += '\t' + terminal('lsb_release -idrc').strip().replace('\n', '\n\t') + '\n'
	contents += '\nProcessor (lscpu):\n'
	contents += '\t' + terminal('lscpu').strip().replace('\n', '\n\t') + '\n'
	contents += '\nNetwork (ifconfig):\n'
	contents += '\t' + terminal('ifconfig').strip().replace('\n', '\n\t') + '\n'
	contents += '\nMemory (cat /proc/meminfo):\n'
	contents += '\t' + terminal('cat /proc/meminfo').strip().replace('\n', '\n\t') + '\n'
	contents += '\nPython (python3 --version):\n'
	contents += '\t' + terminal('python3 --version').strip().replace('\n', '\n\t') + '\n'
	file = open(os.path.join(directory, 'machine_info.txt'), 'w')
	file.write(contents)
	file.close()

# Generate the main peer CSV header line
def makeMainPeerHeader():
	line = 'Timestamp,'
	line += 'Timestamp (UNIX epoch),'
	line += 'Time Since Last Sample (seconds),'
	line += 'Address,'
	line += 'Port,'
	line += 'Connection ID,'
	line += 'Connection Count,'
	line += 'Connection Duration (seconds),'
	line += 'Number of New Unique Blocks Received,'
	line += 'Number of New Unique Transactions Received,'
	line += 'Aggregate of New Unique Transaction Fees (satoshi),'
	line += 'Aggregate of New Unique Transaction Sizes (bytes),'
	line += 'Peer Banscore (accumulated misbehavior score for this peer),'
	line += 'Addrman fChance Score (the relative chance that this entry should be given when selecting nodes to connect to),'
	line += 'Addrman isTerrible Rating (if the statistics about this entry are bad enough that it can just be deleted),'
	line += 'Node Time Offset (seconds),'
	line += 'Ping Round Trip Time (milliseconds),'
	line += 'Minimum Ping Round Trip Time (milliseconds),'
	line += 'Ping Wait Time for an Outstanding Ping (milliseconds),'
	line += 'Address/Network Type,'
	line += 'Prototol Version,'
	line += 'Bitcoin Software Version,'
	line += '"Connection Type (outbound-full-relay, block-relay-only, inbound, manual, addr-fetch, or feeler)",'
	line += 'Is Outbound Connection,'
	line += 'Enabled Services,'
	line += 'Enabled Services (Encoded Integer),'
	line += 'Special Permissions,'
	line += 'Is Transaction Relay Enabled,'
	line += 'Is Address Relay Enabled,'
	line += 'Number of Addresses Accepted,'
	line += 'Number of Addresses Dropped From Rate-limiting,'
	line += 'Minimum Accepted Transaction Fee (BIP 133) (satoshi/kilobyte),'
	line += 'Is SendCMPCT Enabled To Them,'
	line += 'Is SendCMPCT Enabled From Them,'
	line += 'Last Message Send Time (UNIX epoch),'
	line += 'Number of Bytes Sent,'
	line += 'Distribution of Bytes Sent,'
	line += 'Last Message Receive Time (UNIX epoch),'
	line += 'Number of Bytes Received,'
	line += 'Distribution of Bytes Received,'
	line += 'Last Valid Transaction Received Time (UNIX epoch),'
	line += 'Last Valid Block Received Time (UNIX epoch),'
	line += 'Starting Block Height,'
	line += 'Current Block Height In Common,'
	line += 'Current Header Height In Common,'
	line += 'New ADDRs Received (count),'
	line += 'Size ADDR (bytes),'
	line += 'Max Size ADDR (bytes),'
	line += 'Time ADDR (milliseconds),'
	line += 'Max Time ADDR (milliseconds),'
	line += 'New ADDRV2s Received (count),'
	line += 'Size ADDRV2 (bytes),'
	line += 'Max Size ADDRV2 (bytes),'
	line += 'Time ADDRV2 (milliseconds),'
	line += 'Max Time ADDRV2 (milliseconds),'
	line += 'New BLOCKs Received (count),'
	line += 'Size BLOCK (bytes),'
	line += 'Max Size BLOCK (bytes),'
	line += 'Time BLOCK (milliseconds),'
	line += 'Max Time BLOCK (milliseconds),'
	line += 'New BLOCKTXNs Received (count),'
	line += 'Size BLOCKTXN (bytes),'
	line += 'Max Size BLOCKTXN (bytes),'
	line += 'Time BLOCKTXN (milliseconds),'
	line += 'Max Time BLOCKTXN (milliseconds),'
	line += 'New CFCHECKPTs Received (count),'
	line += 'Size CFCHECKPT (bytes),'
	line += 'Max Size CFCHECKPT (bytes),'
	line += 'Time CFCHECKPT (milliseconds),'
	line += 'Max Time CFCHECKPT (milliseconds),'
	line += 'New CFHEADERSs Received (count),'
	line += 'Size CFHEADERS (bytes),'
	line += 'Max Size CFHEADERS (bytes),'
	line += 'Time CFHEADERS (milliseconds),'
	line += 'Max Time CFHEADERS (milliseconds),'
	line += 'New CFILTERs Received (count),'
	line += 'Size CFILTER (bytes),'
	line += 'Max Size CFILTER (bytes),'
	line += 'Time CFILTER (milliseconds),'
	line += 'Max Time CFILTER (milliseconds),'
	line += 'New CMPCTBLOCKs Received (count),'
	line += 'Size CMPCTBLOCK (bytes),'
	line += 'Max Size CMPCTBLOCK (bytes),'
	line += 'Time CMPCTBLOCK (milliseconds),'
	line += 'Max Time CMPCTBLOCK (milliseconds),'
	line += 'New FEEFILTERs Received (count),'
	line += 'Size FEEFILTER (bytes),'
	line += 'Max Size FEEFILTER (bytes),'
	line += 'Time FEEFILTER (milliseconds),'
	line += 'Max Time FEEFILTER (milliseconds),'
	line += 'New FILTERADDs Received (count),'
	line += 'Size FILTERADD (bytes),'
	line += 'Max Size FILTERADD (bytes),'
	line += 'Time FILTERADD (milliseconds),'
	line += 'Max Time FILTERADD (milliseconds),'
	line += 'New FILTERCLEARs Received (count),'
	line += 'Size FILTERCLEAR (bytes),'
	line += 'Max Size FILTERCLEAR (bytes),'
	line += 'Time FILTERCLEAR (milliseconds),'
	line += 'Max Time FILTERCLEAR (milliseconds),'
	line += 'New FILTERLOADs Received (count),'
	line += 'Size FILTERLOAD (bytes),'
	line += 'Max Size FILTERLOAD (bytes),'
	line += 'Time FILTERLOAD (milliseconds),'
	line += 'Max Time FILTERLOAD (milliseconds),'
	line += 'New GETADDRs Received (count),'
	line += 'Size GETADDR (bytes),'
	line += 'Max Size GETADDR (bytes),'
	line += 'Time GETADDR (milliseconds),'
	line += 'Max Time GETADDR (milliseconds),'
	line += 'New GETBLOCKSs Received (count),'
	line += 'Size GETBLOCKS (bytes),'
	line += 'Max Size GETBLOCKS (bytes),'
	line += 'Time GETBLOCKS (milliseconds),'
	line += 'Max Time GETBLOCKS (milliseconds),'
	line += 'New GETBLOCKTXNs Received (count),'
	line += 'Size GETBLOCKTXN (bytes),'
	line += 'Max Size GETBLOCKTXN (bytes),'
	line += 'Time GETBLOCKTXN (milliseconds),'
	line += 'Max Time GETBLOCKTXN (milliseconds),'
	line += 'New GETCFCHECKPTs Received (count),'
	line += 'Size GETCFCHECKPT (bytes),'
	line += 'Max Size GETCFCHECKPT (bytes),'
	line += 'Time GETCFCHECKPT (milliseconds),'
	line += 'Max Time GETCFCHECKPT (milliseconds),'
	line += 'New GETCFHEADERSs Received (count),'
	line += 'Size GETCFHEADERS (bytes),'
	line += 'Max Size GETCFHEADERS (bytes),'
	line += 'Time GETCFHEADERS (milliseconds),'
	line += 'Max Time GETCFHEADERS (milliseconds),'
	line += 'New GETCFILTERSs Received (count),'
	line += 'Size GETCFILTERS (bytes),'
	line += 'Max Size GETCFILTERS (bytes),'
	line += 'Time GETCFILTERS (milliseconds),'
	line += 'Max Time GETCFILTERS (milliseconds),'
	line += 'New GETDATAs Received (count),'
	line += 'Size GETDATA (bytes),'
	line += 'Max Size GETDATA (bytes),'
	line += 'Time GETDATA (milliseconds),'
	line += 'Max Time GETDATA (milliseconds),'
	line += 'New GETHEADERSs Received (count),'
	line += 'Size GETHEADERS (bytes),'
	line += 'Max Size GETHEADERS (bytes),'
	line += 'Time GETHEADERS (milliseconds),'
	line += 'Max Time GETHEADERS (milliseconds),'
	line += 'New HEADERSs Received (count),'
	line += 'Size HEADERS (bytes),'
	line += 'Max Size HEADERS (bytes),'
	line += 'Time HEADERS (milliseconds),'
	line += 'Max Time HEADERS (milliseconds),'
	line += 'New INVs Received (count),'
	line += 'Size INV (bytes),'
	line += 'Max Size INV (bytes),'
	line += 'Time INV (milliseconds),'
	line += 'Max Time INV (milliseconds),'
	line += 'New MEMPOOLs Received (count),'
	line += 'Size MEMPOOL (bytes),'
	line += 'Max Size MEMPOOL (bytes),'
	line += 'Time MEMPOOL (milliseconds),'
	line += 'Max Time MEMPOOL (milliseconds),'
	line += 'New MERKLEBLOCKs Received (count),'
	line += 'Size MERKLEBLOCK (bytes),'
	line += 'Max Size MERKLEBLOCK (bytes),'
	line += 'Time MERKLEBLOCK (milliseconds),'
	line += 'Max Time MERKLEBLOCK (milliseconds),'
	line += 'New NOTFOUNDs Received (count),'
	line += 'Size NOTFOUND (bytes),'
	line += 'Max Size NOTFOUND (bytes),'
	line += 'Time NOTFOUND (milliseconds),'
	line += 'Max Time NOTFOUND (milliseconds),'
	line += 'New PINGs Received (count),'
	line += 'Size PING (bytes),'
	line += 'Max Size PING (bytes),'
	line += 'Time PING (milliseconds),'
	line += 'Max Time PING (milliseconds),'
	line += 'New PONGs Received (count),'
	line += 'Size PONG (bytes),'
	line += 'Max Size PONG (bytes),'
	line += 'Time PONG (milliseconds),'
	line += 'Max Time PONG (milliseconds),'
	line += 'New REJECTs Received (count),'
	line += 'Size REJECT (bytes),'
	line += 'Max Size REJECT (bytes),'
	line += 'Time REJECT (milliseconds),'
	line += 'Max Time REJECT (milliseconds),'
	line += 'New SENDADDRV2s Received (count),'
	line += 'Size SENDADDRV2 (bytes),'
	line += 'Max Size SENDADDRV2 (bytes),'
	line += 'Time SENDADDRV2 (milliseconds),'
	line += 'Max Time SENDADDRV2 (milliseconds),'
	line += 'New SENDCMPCTs Received (count),'
	line += 'Size SENDCMPCT (bytes),'
	line += 'Max Size SENDCMPCT (bytes),'
	line += 'Time SENDCMPCT (milliseconds),'
	line += 'Max Time SENDCMPCT (milliseconds),'
	line += 'New SENDHEADERSs Received (count),'
	line += 'Size SENDHEADERS (bytes),'
	line += 'Max Size SENDHEADERS (bytes),'
	line += 'Time SENDHEADERS (milliseconds),'
	line += 'Max Time SENDHEADERS (milliseconds),'
	line += 'New SENDTXRCNCLs Received (count),'
	line += 'Size SENDTXRCNCL (bytes),'
	line += 'Max Size SENDTXRCNCL (bytes),'
	line += 'Time SENDTXRCNCL (milliseconds),'
	line += 'Max Time SENDTXRCNCL (milliseconds),'
	line += 'New TXs Received (count),'
	line += 'Size TX (bytes),'
	line += 'Max Size TX (bytes),'
	line += 'Time TX (milliseconds),'
	line += 'Max Time TX (milliseconds),'
	line += 'New VERACKs Received (count),'
	line += 'Size VERACK (bytes),'
	line += 'Max Size VERACK (bytes),'
	line += 'Time VERACK (milliseconds),'
	line += 'Max Time VERACK (milliseconds),'
	line += 'New VERSIONs Received (count),'
	line += 'Size VERSION (bytes),'
	line += 'Max Size VERSION (bytes),'
	line += 'Time VERSION (milliseconds),'
	line += 'Max Time VERSION (milliseconds),'
	line += 'New WTXIDRELAYs Received (count),'
	line += 'Size WTXIDRELAY (bytes),'
	line += 'Max Size WTXIDRELAY (bytes),'
	line += 'Time WTXIDRELAY (milliseconds),'
	line += 'Max Time WTXIDRELAY (milliseconds),'
	line += 'New [UNDOCUMENTED]s Received (count),'
	line += 'Size [UNDOCUMENTED] (bytes),'
	line += 'Max Size [UNDOCUMENTED] (bytes),'
	line += 'Time [UNDOCUMENTED] (milliseconds),'
	line += 'Max Time [UNDOCUMENTED] (milliseconds),'
	return line

# Generate the machine state CSV header line
def makeMachineStateHeader():
	line = 'Timestamp,'
	line += 'Timestamp (UNIX epoch),'
	line += 'Time Since Last Sample (seconds),'
	line += 'Platform,'
	line += 'Processor,'
	line += 'Processor Cores,'
	line += 'RAM,'
	line += 'Network Interface,'
	line += 'Network Bytes Sent (bytes),'
	line += 'Network Bytes Received (bytes),'
	line += 'Network Packets Sent (packets),'
	line += 'Network Packets Received (packets),'
	line += 'Current Machine CPU (percent),'
	line += 'Current Machine CPU Frequency (megahertz),'
	line += 'Current Machine Virtual Memory (percent),'
	line += 'Current Machine Virtual Memory (bytes),'
	line += 'Current Machine Swap Memory (percent),'
	line += 'Current Machine Swap Memory (bytes),'
	line += 'Current Machine Disk Usage (percent),'
	line += 'Current Machine Disk Usage (bytes),'
	line += 'Bitcoin Process ID,'
	line += 'Bitcoin Process Virtual Memory (bytes),'
	line += 'Bitcoin Process Memory (bytes),'
	line += 'Bitcoin Process Shared Memory (bytes),'
	line += 'Bitcoin Process Memory (percent),'
	line += 'Bitcoin Process CPU (percent),'
	return line

# Given a raw memory string from the linux "top" command, return the number of bytes
# 1 EiB = 1024 * 1024 * 1024 * 1024 * 1024 * 1024 bytes
# 1 PiB = 1024 * 1024 * 1024 * 1024 * 1024 bytes
# 1 GiB = 1024 * 1024 * 1024 * 1024 bytes
# 1 MiB = 1024 * 1024 * 1024 bytes
# 1 KiB = 1024 * 1024 bytes
def topMemToBytes(mem):
	if mem.endswith('e'): return float(mem[:-1]) * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 # exbibytes to bytes
	elif mem.endswith('p'): return float(mem[:-1]) * 1024 * 1024 * 1024 * 1024 * 1024 # gibibytes to bytes
	elif mem.endswith('t'): return float(mem[:-1]) * 1024 * 1024 * 1024 * 1024 # tebibytes to bytes
	elif mem.endswith('g'): return float(mem[:-1]) * 1024 * 1024 * 1024 # gibabytes to bytes
	elif mem.endswith('m'): return float(mem[:-1]) * 1024 * 1024 # mebibytes to bytes
	else: return float(mem) * 1024 # kibibytes to bytes

# Given a process name, return the specs for the process
def logIndividualProcess(process_id):
	raw = terminal('top -b -n 1 |grep ' + process_id).strip().split()
	while len(raw) < 12: raw.append('0') # Fill in with zeros for any missing values
	output = {
	'process_ID': raw[0],
	'user': raw[1],
	'priority': raw[2],
	'nice_value': raw[3],
	'virtual_memory': str(topMemToBytes(raw[4])),
	'memory': str(topMemToBytes(raw[5])),
	'shared_memory': str(topMemToBytes(raw[6])),
	'state': raw[7],
	'cpu_percent': raw[8],
	'memory_percent': raw[9],
	'time': raw[10],
	'process_name': raw[11],
	}
	return output

# Reads /proc/net/dev to get networking bytes/packets sent/received
def getNetworkData():
	raw = terminal('awk \'/:/ { print($1, $2, $3, $10, $11) }\' < /proc/net/dev -').strip().split('\n')
	selected_interface = ''
	for interface in raw:
		if not interface.startswith('lo:'):
			selected_interface = interface
			break
	data = selected_interface.strip().split()
	if selected_interface != '' and len(data) == 5:
		if data[0].endswith(':'): data[0] = data[0][:-1]
		# Differentiate between error and no error
		if data[0] == '': data[0] == ' '
		try:
			return {
			'interface': data[0],
			'bytes_sent': int(data[3]),
			'bytes_received': int(data[1]),
			'packets_sent': int(data[4]),
			'packets_received': int(data[2]),
			}
		except:
			pass
	return {
		'interface': '',
		'bytes_sent': '',
		'bytes_received': '',
		'packets_sent': '',
		'packets_received': '',
	}

# Processes the syntax of the RPC command: getmsginfo
def parseGetMsgInfoMessage(rawString, clocksPerSecond):
	# rawString is in the format "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts"
	count = int(re.findall(r'([0-9\.]+) msgs', rawString)[0])
	matches = re.findall(r'\[[0-9\., ]+\]', rawString)
	clocksMatch = json.loads(matches[0])
	# clocks / clocksPerSecond * 1000 --> milliseconds
	clocksSum = int(clocksMatch[0]) / clocksPerSecond * 1000
	if count != 0: clocksAvg = clocksSum / count
	else: clocksAvg = 0
	clocksMax = int(clocksMatch[2]) / clocksPerSecond * 1000
	bytesMatch = json.loads(matches[1])
	bytesSum = int(bytesMatch[0])
	if count != 0: bytesAvg = bytesSum / count
	else: bytesAvg = 0
	bytesMax = int(bytesMatch[2])
	return count, bytesAvg, bytesMax, clocksAvg, clocksMax

# Given a combined address and port, return the individual address and port 
def splitAddress(address):
	split = address.split(':')
	port = split.pop()
	address = ':'.join(split)
	return address, port

# Log the state of the machine to file, returns the sample number
def logMachineState(timestamp, directory):
	filePath = os.path.join(directory, 'machine_state_info.csv')
	if not os.path.exists(filePath):
		print(f'Creating machine state file')
		file = open(filePath, 'w')
		file.write(makeMachineStateHeader() + '\n')
		prevLine = ''
		numPrevLines = 1
	else:
		# Read the last line from the file
		with open(filePath, 'r') as f:
			prevLines = f.readlines()
			if len(prevLines) > 1: prevLine = prevLines[-1].split(',')
			else: prevLine = ''
			numPrevLines = len(prevLines)
		# Try to open the file for appending, loop until successful
		attempts = 0
		file = None
		while file is None:
			try:
				attempts += 1
				file = open(filePath, 'a')
			except PermissionError as e:
				print(f'{e}, attempt {attempts}')
				time.sleep(1)
 
	timestampSeconds = (timestamp - datetime.datetime(1970, 1, 1)).total_seconds()
	if prevLine == '':
		timeSinceLastSample = ''
	else: 
		timeSinceLastSample = timestampSeconds - float(prevLine[1])
	cpuPercent = psutil.cpu_percent()
	cpuFrequency = 0
	try:
		cpuFrequency = psutil.cpu_freq().current
	except: pass
	virtualMemoryPercent = psutil.virtual_memory().percent
	virtualMemory = psutil.virtual_memory().used
	swapMemoryPercent = psutil.swap_memory().percent
	swapMemory = psutil.swap_memory().used
	diskUsagePercent = psutil.disk_usage('/').percent
	diskUsage = psutil.disk_usage('/').used
	networkData = getNetworkData()
	individualProcessData = logIndividualProcess('bitcoind')

	line = str(timestamp) + ','
	line += str(timestampSeconds) + ','
	line += str(timeSinceLastSample) + ','
	line += '"' + str(platform.platform()) + '",'
	line += '"' + str(platform.processor()) + '",'
	line += str(psutil.cpu_count()) + ','
	line += str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + ' GB,'
	line += '"' + str(networkData['interface']) + '",'
	line += str(networkData['bytes_sent']) + ','
	line += str(networkData['bytes_received']) + ','
	line += str(networkData['packets_sent']) + ','
	line += str(networkData['packets_received']) + ','
	line += str(cpuPercent) + ','
	line += str(cpuFrequency) + ','
	line += str(virtualMemoryPercent) + ','
	line += str(virtualMemory) + ','
	line += str(swapMemoryPercent) + ','
	line += str(swapMemory) + ','
	line += str(diskUsagePercent) + ','
	line += str(diskUsage) + ','
	line += str(individualProcessData['process_ID']) + ','
	line += str(individualProcessData['virtual_memory']) + ','
	line += str(individualProcessData['memory']) + ','
	line += str(individualProcessData['shared_memory']) + ','
	line += str(individualProcessData['memory_percent']) + ','
	line += str(individualProcessData['cpu_percent']) + ','
	file.write(line + '\n')
	return numPrevLines

# Log the state of the node to file, returns the sample number
def logNode(address, timestamp, directory, updateInfo):
	filePath = os.path.join(directory, re.sub('[^A-Za-z0-9\.]', '-', address)) + '.csv'
	if not os.path.exists(filePath):
		# Create a new file
		prevLine = ''
		numPrevLines = 1
		print(f'	Logging {address} ({numPrevLines} sample)')
		file = open(filePath, 'w')
		file.write(makeMainPeerHeader() + '\n')
	else:
		# Read the last line from the file
		with open(filePath, 'r') as f:
			prevLines = f.readlines()
			# Don't let prevLine contain the header; data only
			if len(prevLines) > 1: prevLine = prevLines[-1].split(',')
			else: prevLine = ''
			numPrevLines = len(prevLines)
		print(f'	Logging {address} ({numPrevLines} samples)')

		# Try to open the file for appending, loop until successful
		attempts = 0
		file = None
		while file is None:
			try:
				attempts += 1
				file = open(filePath, 'a')
			except PermissionError as e:
				print(f'{e}, attempt {attempts}')
				time.sleep(1)

	timestampSeconds = (timestamp - datetime.datetime(1970, 1, 1)).total_seconds()
	if prevLine == '':
		timeSinceLastSample = ''
		connectionCount = 1
	else: 
		timeSinceLastSample = timestampSeconds - float(prevLine[1])
		connectionCount = int(prevLine[5])
		# Check if this is the same connection or a new connection
		if updateInfo['port'] != int(prevLine[4]) or updateInfo['connectionID'] != int(prevLine[5]) or int(updateInfo['connectionDuration']) < int(prevLine[7]):
			connectionCount += 1

	line = str(timestamp) + ','
	line += str(timestampSeconds) + ','
	line += str(timeSinceLastSample) + ','
	line += str(address) + ','
	line += str(updateInfo['port']) + ','
	line += str(updateInfo['connectionID']) + ','
	line += str(connectionCount) + ','
	line += str(updateInfo['connectionDuration']) + ','
	line += str(updateInfo['newBlocksReceivedCount']) + ','
	line += str(updateInfo['newTransactionsReceivedCount']) + ','
	line += str(updateInfo['newTransactionsReceivedFee']) + ','
	line += str(updateInfo['newTransactionsReceivedSize']) + ','
	line += str(updateInfo['banscore']) + ','
	line += str(updateInfo['fChance']) + ','
	line += str(updateInfo['isTerrible']) + ','
	line += str(updateInfo['secondsOffset']) + ','
	line += str(updateInfo['pingRoundTripTime']) + ','
	line += str(updateInfo['pingMinRoundTripTime']) + ','
	line += str(updateInfo['pingWaitTime']) + ','
	line += str(updateInfo['addressType']) + ','
	line += str(updateInfo['prototolVersion']) + ','
	line += str(updateInfo['softwareVersion']) + ','
	line += str(updateInfo['connectionType']) + ','
	line += str(updateInfo['isOutboundConnection']) + ','
	line += str(updateInfo['services']) + ','
	line += str(updateInfo['servicesEncodedInt']) + ','
	line += str(updateInfo['specialPermissions']) + ','
	line += str(updateInfo['willRelayTransactions']) + ','
	line += str(updateInfo['willRelayAddrs']) + ','
	line += str(updateInfo['numAddrsAccepted']) + ','
	line += str(updateInfo['numAddrsDroppedFromRateLimit']) + ','
	line += str(updateInfo['minTransactionFeeAccepted']) + ','
	line += str(updateInfo['sendCmpctEnabledToThem']) + ','
	line += str(updateInfo['sendCmpctEnabledFromThem']) + ','
	line += str(updateInfo['lastSendTime']) + ','
	line += str(updateInfo['bytesSent']) + ','
	line += str(updateInfo['bytesSentDistribution']) + ','
	line += str(updateInfo['lastReceiveTime']) + ','
	line += str(updateInfo['bytesReceived']) + ','
	line += str(updateInfo['bytesReceivedDistribution']) + ','
	line += str(updateInfo['lastTransactionTime']) + ','
	line += str(updateInfo['lastBlockTime']) + ','
	line += str(updateInfo['startingBlockHeight']) + ','
	line += str(updateInfo['currentBlockHeightInCommon']) + ','
	line += str(updateInfo['currentHeaderHeightInCommon']) + ','
	line += str(updateInfo['New_ADDRs_Received (count)']) + ','
	line += str(updateInfo['Size_ADDR (bytes)']) + ','
	line += str(updateInfo['MaxSize_ADDR (bytes)']) + ','
	line += str(updateInfo['Time_ADDR (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_ADDR (milliseconds)']) + ','
	line += str(updateInfo['New_ADDRV2s_Received (count)']) + ','
	line += str(updateInfo['Size_ADDRV2 (bytes)']) + ','
	line += str(updateInfo['MaxSize_ADDRV2 (bytes)']) + ','
	line += str(updateInfo['Time_ADDRV2 (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_ADDRV2 (milliseconds)']) + ','
	line += str(updateInfo['New_BLOCKs_Received (count)']) + ','
	line += str(updateInfo['Size_BLOCK (bytes)']) + ','
	line += str(updateInfo['MaxSize_BLOCK (bytes)']) + ','
	line += str(updateInfo['Time_BLOCK (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_BLOCK (milliseconds)']) + ','
	line += str(updateInfo['New_BLOCKTXNs_Received (count)']) + ','
	line += str(updateInfo['Size_BLOCKTXN (bytes)']) + ','
	line += str(updateInfo['MaxSize_BLOCKTXN (bytes)']) + ','
	line += str(updateInfo['Time_BLOCKTXN (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_BLOCKTXN (milliseconds)']) + ','
	line += str(updateInfo['New_CFCHECKPTs_Received (count)']) + ','
	line += str(updateInfo['Size_CFCHECKPT (bytes)']) + ','
	line += str(updateInfo['MaxSize_CFCHECKPT (bytes)']) + ','
	line += str(updateInfo['Time_CFCHECKPT (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_CFCHECKPT (milliseconds)']) + ','
	line += str(updateInfo['New_CFHEADERSs_Received (count)']) + ','
	line += str(updateInfo['Size_CFHEADERS (bytes)']) + ','
	line += str(updateInfo['MaxSize_CFHEADERS (bytes)']) + ','
	line += str(updateInfo['Time_CFHEADERS (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_CFHEADERS (milliseconds)']) + ','
	line += str(updateInfo['New_CFILTERs_Received (count)']) + ','
	line += str(updateInfo['Size_CFILTER (bytes)']) + ','
	line += str(updateInfo['MaxSize_CFILTER (bytes)']) + ','
	line += str(updateInfo['Time_CFILTER (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_CFILTER (milliseconds)']) + ','
	line += str(updateInfo['New_CMPCTBLOCKs_Received (count)']) + ','
	line += str(updateInfo['Size_CMPCTBLOCK (bytes)']) + ','
	line += str(updateInfo['MaxSize_CMPCTBLOCK (bytes)']) + ','
	line += str(updateInfo['Time_CMPCTBLOCK (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_CMPCTBLOCK (milliseconds)']) + ','
	line += str(updateInfo['New_FEEFILTERs_Received (count)']) + ','
	line += str(updateInfo['Size_FEEFILTER (bytes)']) + ','
	line += str(updateInfo['MaxSize_FEEFILTER (bytes)']) + ','
	line += str(updateInfo['Time_FEEFILTER (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_FEEFILTER (milliseconds)']) + ','
	line += str(updateInfo['New_FILTERADDs_Received (count)']) + ','
	line += str(updateInfo['Size_FILTERADD (bytes)']) + ','
	line += str(updateInfo['MaxSize_FILTERADD (bytes)']) + ','
	line += str(updateInfo['Time_FILTERADD (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_FILTERADD (milliseconds)']) + ','
	line += str(updateInfo['New_FILTERCLEARs_Received (count)']) + ','
	line += str(updateInfo['Size_FILTERCLEAR (bytes)']) + ','
	line += str(updateInfo['MaxSize_FILTERCLEAR (bytes)']) + ','
	line += str(updateInfo['Time_FILTERCLEAR (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_FILTERCLEAR (milliseconds)']) + ','
	line += str(updateInfo['New_FILTERLOADs_Received (count)']) + ','
	line += str(updateInfo['Size_FILTERLOAD (bytes)']) + ','
	line += str(updateInfo['MaxSize_FILTERLOAD (bytes)']) + ','
	line += str(updateInfo['Time_FILTERLOAD (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_FILTERLOAD (milliseconds)']) + ','
	line += str(updateInfo['New_GETADDRs_Received (count)']) + ','
	line += str(updateInfo['Size_GETADDR (bytes)']) + ','
	line += str(updateInfo['MaxSize_GETADDR (bytes)']) + ','
	line += str(updateInfo['Time_GETADDR (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_GETADDR (milliseconds)']) + ','
	line += str(updateInfo['New_GETBLOCKSs_Received (count)']) + ','
	line += str(updateInfo['Size_GETBLOCKS (bytes)']) + ','
	line += str(updateInfo['MaxSize_GETBLOCKS (bytes)']) + ','
	line += str(updateInfo['Time_GETBLOCKS (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_GETBLOCKS (milliseconds)']) + ','
	line += str(updateInfo['New_GETBLOCKTXNs_Received (count)']) + ','
	line += str(updateInfo['Size_GETBLOCKTXN (bytes)']) + ','
	line += str(updateInfo['MaxSize_GETBLOCKTXN (bytes)']) + ','
	line += str(updateInfo['Time_GETBLOCKTXN (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_GETBLOCKTXN (milliseconds)']) + ','
	line += str(updateInfo['New_GETCFCHECKPTs_Received (count)']) + ','
	line += str(updateInfo['Size_GETCFCHECKPT (bytes)']) + ','
	line += str(updateInfo['MaxSize_GETCFCHECKPT (bytes)']) + ','
	line += str(updateInfo['Time_GETCFCHECKPT (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_GETCFCHECKPT (milliseconds)']) + ','
	line += str(updateInfo['New_GETCFHEADERSs_Received (count)']) + ','
	line += str(updateInfo['Size_GETCFHEADERS (bytes)']) + ','
	line += str(updateInfo['MaxSize_GETCFHEADERS (bytes)']) + ','
	line += str(updateInfo['Time_GETCFHEADERS (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_GETCFHEADERS (milliseconds)']) + ','
	line += str(updateInfo['New_GETCFILTERSs_Received (count)']) + ','
	line += str(updateInfo['Size_GETCFILTERS (bytes)']) + ','
	line += str(updateInfo['MaxSize_GETCFILTERS (bytes)']) + ','
	line += str(updateInfo['Time_GETCFILTERS (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_GETCFILTERS (milliseconds)']) + ','
	line += str(updateInfo['New_GETDATAs_Received (count)']) + ','
	line += str(updateInfo['Size_GETDATA (bytes)']) + ','
	line += str(updateInfo['MaxSize_GETDATA (bytes)']) + ','
	line += str(updateInfo['Time_GETDATA (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_GETDATA (milliseconds)']) + ','
	line += str(updateInfo['New_GETHEADERSs_Received (count)']) + ','
	line += str(updateInfo['Size_GETHEADERS (bytes)']) + ','
	line += str(updateInfo['MaxSize_GETHEADERS (bytes)']) + ','
	line += str(updateInfo['Time_GETHEADERS (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_GETHEADERS (milliseconds)']) + ','
	line += str(updateInfo['New_HEADERSs_Received (count)']) + ','
	line += str(updateInfo['Size_HEADERS (bytes)']) + ','
	line += str(updateInfo['MaxSize_HEADERS (bytes)']) + ','
	line += str(updateInfo['Time_HEADERS (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_HEADERS (milliseconds)']) + ','
	line += str(updateInfo['New_INVs_Received (count)']) + ','
	line += str(updateInfo['Size_INV (bytes)']) + ','
	line += str(updateInfo['MaxSize_INV (bytes)']) + ','
	line += str(updateInfo['Time_INV (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_INV (milliseconds)']) + ','
	line += str(updateInfo['New_MEMPOOLs_Received (count)']) + ','
	line += str(updateInfo['Size_MEMPOOL (bytes)']) + ','
	line += str(updateInfo['MaxSize_MEMPOOL (bytes)']) + ','
	line += str(updateInfo['Time_MEMPOOL (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_MEMPOOL (milliseconds)']) + ','
	line += str(updateInfo['New_MERKLEBLOCKs_Received (count)']) + ','
	line += str(updateInfo['Size_MERKLEBLOCK (bytes)']) + ','
	line += str(updateInfo['MaxSize_MERKLEBLOCK (bytes)']) + ','
	line += str(updateInfo['Time_MERKLEBLOCK (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_MERKLEBLOCK (milliseconds)']) + ','
	line += str(updateInfo['New_NOTFOUNDs_Received (count)']) + ','
	line += str(updateInfo['Size_NOTFOUND (bytes)']) + ','
	line += str(updateInfo['MaxSize_NOTFOUND (bytes)']) + ','
	line += str(updateInfo['Time_NOTFOUND (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_NOTFOUND (milliseconds)']) + ','
	line += str(updateInfo['New_PINGs_Received (count)']) + ','
	line += str(updateInfo['Size_PING (bytes)']) + ','
	line += str(updateInfo['MaxSize_PING (bytes)']) + ','
	line += str(updateInfo['Time_PING (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_PING (milliseconds)']) + ','
	line += str(updateInfo['New_PONGs_Received (count)']) + ','
	line += str(updateInfo['Size_PONG (bytes)']) + ','
	line += str(updateInfo['MaxSize_PONG (bytes)']) + ','
	line += str(updateInfo['Time_PONG (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_PONG (milliseconds)']) + ','
	line += str(updateInfo['New_REJECTs_Received (count)']) + ','
	line += str(updateInfo['Size_REJECT (bytes)']) + ','
	line += str(updateInfo['MaxSize_REJECT (bytes)']) + ','
	line += str(updateInfo['Time_REJECT (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_REJECT (milliseconds)']) + ','
	line += str(updateInfo['New_SENDADDRV2s_Received (count)']) + ','
	line += str(updateInfo['Size_SENDADDRV2 (bytes)']) + ','
	line += str(updateInfo['MaxSize_SENDADDRV2 (bytes)']) + ','
	line += str(updateInfo['Time_SENDADDRV2 (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_SENDADDRV2 (milliseconds)']) + ','
	line += str(updateInfo['New_SENDCMPCTs_Received (count)']) + ','
	line += str(updateInfo['Size_SENDCMPCT (bytes)']) + ','
	line += str(updateInfo['MaxSize_SENDCMPCT (bytes)']) + ','
	line += str(updateInfo['Time_SENDCMPCT (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_SENDCMPCT (milliseconds)']) + ','
	line += str(updateInfo['New_SENDHEADERSs_Received (count)']) + ','
	line += str(updateInfo['Size_SENDHEADERS (bytes)']) + ','
	line += str(updateInfo['MaxSize_SENDHEADERS (bytes)']) + ','
	line += str(updateInfo['Time_SENDHEADERS (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_SENDHEADERS (milliseconds)']) + ','
	line += str(updateInfo['New_SENDTXRCNCLs_Received (count)']) + ','
	line += str(updateInfo['Size_SENDTXRCNCL (bytes)']) + ','
	line += str(updateInfo['MaxSize_SENDTXRCNCL (bytes)']) + ','
	line += str(updateInfo['Time_SENDTXRCNCL (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_SENDTXRCNCL (milliseconds)']) + ','
	line += str(updateInfo['New_TXs_Received (count)']) + ','
	line += str(updateInfo['Size_TX (bytes)']) + ','
	line += str(updateInfo['MaxSize_TX (bytes)']) + ','
	line += str(updateInfo['Time_TX (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_TX (milliseconds)']) + ','
	line += str(updateInfo['New_VERACKs_Received (count)']) + ','
	line += str(updateInfo['Size_VERACK (bytes)']) + ','
	line += str(updateInfo['MaxSize_VERACK (bytes)']) + ','
	line += str(updateInfo['Time_VERACK (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_VERACK (milliseconds)']) + ','
	line += str(updateInfo['New_VERSIONs_Received (count)']) + ','
	line += str(updateInfo['Size_VERSION (bytes)']) + ','
	line += str(updateInfo['MaxSize_VERSION (bytes)']) + ','
	line += str(updateInfo['Time_VERSION (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_VERSION (milliseconds)']) + ','
	line += str(updateInfo['New_WTXIDRELAYs_Received (count)']) + ','
	line += str(updateInfo['Size_WTXIDRELAY (bytes)']) + ','
	line += str(updateInfo['MaxSize_WTXIDRELAY (bytes)']) + ','
	line += str(updateInfo['Time_WTXIDRELAY (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_WTXIDRELAY (milliseconds)']) + ','
	line += str(updateInfo['New_[UNDOCUMENTED]s_Received (count)']) + ','
	line += str(updateInfo['Size_[UNDOCUMENTED] (bytes)']) + ','
	line += str(updateInfo['MaxSize_[UNDOCUMENTED] (bytes)']) + ','
	line += str(updateInfo['Time_[UNDOCUMENTED] (milliseconds)']) + ','
	line += str(updateInfo['MaxTime_[UNDOCUMENTED] (milliseconds)']) + ','

	file.write(line + '\n')
	file.close()

def getPeerInfoTemplate():
	return {
		# Start of listnewbroadcastsandclear
		'newBlocksReceivedCount': '0',
		'newTransactionsReceivedCount': '0',
		'newTransactionsReceivedFee': '0',
		'newTransactionsReceivedSize': '0',
		# End of listnewbroadcastsandclear
		# Start of getpeerinfo
		'banscore': '',
		'fChance': '',
		'isTerrible': '',
		'port': '',
		'connectionID': '',
		'connectionDuration': '',
		'secondsOffset': '',
		'pingRoundTripTime': '',
		'pingMinRoundTripTime': '',
		'pingWaitTime': '',
		'addressType': '',
		'prototolVersion': '',
		'softwareVersion': '',
		'connectionType': '',
		'isOutboundConnection': '',
		'services': '',
		'servicesEncodedInt': '',
		'specialPermissions': '',
		'willRelayTransactions': '',
		'willRelayAddrs': '',
		'numAddrsAccepted': '',
		'numAddrsDroppedFromRateLimit': '',
		'minTransactionFeeAccepted': '',
		'sendCmpctEnabledToThem': '',
		'sendCmpctEnabledFromThem': '',
		'lastSendTime': '',
		'bytesSent': '',
		'bytesSentDistribution': '',
		'lastReceiveTime': '',
		'bytesReceived': '',
		'bytesReceivedDistribution': '',
		'lastTransactionTime': '',
		'lastBlockTime': '',
		'startingBlockHeight': '',
		'currentBlockHeightInCommon': '',
		'currentHeaderHeightInCommon': '',
		# End of getpeerinfo
		# Start of getpeersmsginfoandclear
		'New_ADDRs_Received (count)': '0',
		'Size_ADDR (bytes)': '0',
		'MaxSize_ADDR (bytes)': '0',
		'Time_ADDR (milliseconds)': '0',
		'MaxTime_ADDR (milliseconds)': '0',
		'New_ADDRV2s_Received (count)': '0',
		'Size_ADDRV2 (bytes)': '0',
		'MaxSize_ADDRV2 (bytes)': '0',
		'Time_ADDRV2 (milliseconds)': '0',
		'MaxTime_ADDRV2 (milliseconds)': '0',
		'New_BLOCKs_Received (count)': '0',
		'Size_BLOCK (bytes)': '0',
		'MaxSize_BLOCK (bytes)': '0',
		'Time_BLOCK (milliseconds)': '0',
		'MaxTime_BLOCK (milliseconds)': '0',
		'New_BLOCKTXNs_Received (count)': '0',
		'Size_BLOCKTXN (bytes)': '0',
		'MaxSize_BLOCKTXN (bytes)': '0',
		'Time_BLOCKTXN (milliseconds)': '0',
		'MaxTime_BLOCKTXN (milliseconds)': '0',
		'New_CFCHECKPTs_Received (count)': '0',
		'Size_CFCHECKPT (bytes)': '0',
		'MaxSize_CFCHECKPT (bytes)': '0',
		'Time_CFCHECKPT (milliseconds)': '0',
		'MaxTime_CFCHECKPT (milliseconds)': '0',
		'New_CFHEADERSs_Received (count)': '0',
		'Size_CFHEADERS (bytes)': '0',
		'MaxSize_CFHEADERS (bytes)': '0',
		'Time_CFHEADERS (milliseconds)': '0',
		'MaxTime_CFHEADERS (milliseconds)': '0',
		'New_CFILTERs_Received (count)': '0',
		'Size_CFILTER (bytes)': '0',
		'MaxSize_CFILTER (bytes)': '0',
		'Time_CFILTER (milliseconds)': '0',
		'MaxTime_CFILTER (milliseconds)': '0',
		'New_CMPCTBLOCKs_Received (count)': '0',
		'Size_CMPCTBLOCK (bytes)': '0',
		'MaxSize_CMPCTBLOCK (bytes)': '0',
		'Time_CMPCTBLOCK (milliseconds)': '0',
		'MaxTime_CMPCTBLOCK (milliseconds)': '0',
		'New_FEEFILTERs_Received (count)': '0',
		'Size_FEEFILTER (bytes)': '0',
		'MaxSize_FEEFILTER (bytes)': '0',
		'Time_FEEFILTER (milliseconds)': '0',
		'MaxTime_FEEFILTER (milliseconds)': '0',
		'New_FILTERADDs_Received (count)': '0',
		'Size_FILTERADD (bytes)': '0',
		'MaxSize_FILTERADD (bytes)': '0',
		'Time_FILTERADD (milliseconds)': '0',
		'MaxTime_FILTERADD (milliseconds)': '0',
		'New_FILTERCLEARs_Received (count)': '0',
		'Size_FILTERCLEAR (bytes)': '0',
		'MaxSize_FILTERCLEAR (bytes)': '0',
		'Time_FILTERCLEAR (milliseconds)': '0',
		'MaxTime_FILTERCLEAR (milliseconds)': '0',
		'New_FILTERLOADs_Received (count)': '0',
		'Size_FILTERLOAD (bytes)': '0',
		'MaxSize_FILTERLOAD (bytes)': '0',
		'Time_FILTERLOAD (milliseconds)': '0',
		'MaxTime_FILTERLOAD (milliseconds)': '0',
		'New_GETADDRs_Received (count)': '0',
		'Size_GETADDR (bytes)': '0',
		'MaxSize_GETADDR (bytes)': '0',
		'Time_GETADDR (milliseconds)': '0',
		'MaxTime_GETADDR (milliseconds)': '0',
		'New_GETBLOCKSs_Received (count)': '0',
		'Size_GETBLOCKS (bytes)': '0',
		'MaxSize_GETBLOCKS (bytes)': '0',
		'Time_GETBLOCKS (milliseconds)': '0',
		'MaxTime_GETBLOCKS (milliseconds)': '0',
		'New_GETBLOCKTXNs_Received (count)': '0',
		'Size_GETBLOCKTXN (bytes)': '0',
		'MaxSize_GETBLOCKTXN (bytes)': '0',
		'Time_GETBLOCKTXN (milliseconds)': '0',
		'MaxTime_GETBLOCKTXN (milliseconds)': '0',
		'New_GETCFCHECKPTs_Received (count)': '0',
		'Size_GETCFCHECKPT (bytes)': '0',
		'MaxSize_GETCFCHECKPT (bytes)': '0',
		'Time_GETCFCHECKPT (milliseconds)': '0',
		'MaxTime_GETCFCHECKPT (milliseconds)': '0',
		'New_GETCFHEADERSs_Received (count)': '0',
		'Size_GETCFHEADERS (bytes)': '0',
		'MaxSize_GETCFHEADERS (bytes)': '0',
		'Time_GETCFHEADERS (milliseconds)': '0',
		'MaxTime_GETCFHEADERS (milliseconds)': '0',
		'New_GETCFILTERSs_Received (count)': '0',
		'Size_GETCFILTERS (bytes)': '0',
		'MaxSize_GETCFILTERS (bytes)': '0',
		'Time_GETCFILTERS (milliseconds)': '0',
		'MaxTime_GETCFILTERS (milliseconds)': '0',
		'New_GETDATAs_Received (count)': '0',
		'Size_GETDATA (bytes)': '0',
		'MaxSize_GETDATA (bytes)': '0',
		'Time_GETDATA (milliseconds)': '0',
		'MaxTime_GETDATA (milliseconds)': '0',
		'New_GETHEADERSs_Received (count)': '0',
		'Size_GETHEADERS (bytes)': '0',
		'MaxSize_GETHEADERS (bytes)': '0',
		'Time_GETHEADERS (milliseconds)': '0',
		'MaxTime_GETHEADERS (milliseconds)': '0',
		'New_HEADERSs_Received (count)': '0',
		'Size_HEADERS (bytes)': '0',
		'MaxSize_HEADERS (bytes)': '0',
		'Time_HEADERS (milliseconds)': '0',
		'MaxTime_HEADERS (milliseconds)': '0',
		'New_INVs_Received (count)': '0',
		'Size_INV (bytes)': '0',
		'MaxSize_INV (bytes)': '0',
		'Time_INV (milliseconds)': '0',
		'MaxTime_INV (milliseconds)': '0',
		'New_MEMPOOLs_Received (count)': '0',
		'Size_MEMPOOL (bytes)': '0',
		'MaxSize_MEMPOOL (bytes)': '0',
		'Time_MEMPOOL (milliseconds)': '0',
		'MaxTime_MEMPOOL (milliseconds)': '0',
		'New_MERKLEBLOCKs_Received (count)': '0',
		'Size_MERKLEBLOCK (bytes)': '0',
		'MaxSize_MERKLEBLOCK (bytes)': '0',
		'Time_MERKLEBLOCK (milliseconds)': '0',
		'MaxTime_MERKLEBLOCK (milliseconds)': '0',
		'New_NOTFOUNDs_Received (count)': '0',
		'Size_NOTFOUND (bytes)': '0',
		'MaxSize_NOTFOUND (bytes)': '0',
		'Time_NOTFOUND (milliseconds)': '0',
		'MaxTime_NOTFOUND (milliseconds)': '0',
		'New_PINGs_Received (count)': '0',
		'Size_PING (bytes)': '0',
		'MaxSize_PING (bytes)': '0',
		'Time_PING (milliseconds)': '0',
		'MaxTime_PING (milliseconds)': '0',
		'New_PONGs_Received (count)': '0',
		'Size_PONG (bytes)': '0',
		'MaxSize_PONG (bytes)': '0',
		'Time_PONG (milliseconds)': '0',
		'MaxTime_PONG (milliseconds)': '0',
		'New_REJECTs_Received (count)': '0',
		'Size_REJECT (bytes)': '0',
		'MaxSize_REJECT (bytes)': '0',
		'Time_REJECT (milliseconds)': '0',
		'MaxTime_REJECT (milliseconds)': '0',
		'New_SENDADDRV2s_Received (count)': '0',
		'Size_SENDADDRV2 (bytes)': '0',
		'MaxSize_SENDADDRV2 (bytes)': '0',
		'Time_SENDADDRV2 (milliseconds)': '0',
		'MaxTime_SENDADDRV2 (milliseconds)': '0',
		'New_SENDCMPCTs_Received (count)': '0',
		'Size_SENDCMPCT (bytes)': '0',
		'MaxSize_SENDCMPCT (bytes)': '0',
		'Time_SENDCMPCT (milliseconds)': '0',
		'MaxTime_SENDCMPCT (milliseconds)': '0',
		'New_SENDHEADERSs_Received (count)': '0',
		'Size_SENDHEADERS (bytes)': '0',
		'MaxSize_SENDHEADERS (bytes)': '0',
		'Time_SENDHEADERS (milliseconds)': '0',
		'MaxTime_SENDHEADERS (milliseconds)': '0',
		'New_SENDTXRCNCLs_Received (count)': '0',
		'Size_SENDTXRCNCL (bytes)': '0',
		'MaxSize_SENDTXRCNCL (bytes)': '0',
		'Time_SENDTXRCNCL (milliseconds)': '0',
		'MaxTime_SENDTXRCNCL (milliseconds)': '0',
		'New_TXs_Received (count)': '0',
		'Size_TX (bytes)': '0',
		'MaxSize_TX (bytes)': '0',
		'Time_TX (milliseconds)': '0',
		'MaxTime_TX (milliseconds)': '0',
		'New_VERACKs_Received (count)': '0',
		'Size_VERACK (bytes)': '0',
		'MaxSize_VERACK (bytes)': '0',
		'Time_VERACK (milliseconds)': '0',
		'MaxTime_VERACK (milliseconds)': '0',
		'New_VERSIONs_Received (count)': '0',
		'Size_VERSION (bytes)': '0',
		'MaxSize_VERSION (bytes)': '0',
		'Time_VERSION (milliseconds)': '0',
		'MaxTime_VERSION (milliseconds)': '0',
		'New_WTXIDRELAYs_Received (count)': '0',
		'Size_WTXIDRELAY (bytes)': '0',
		'MaxSize_WTXIDRELAY (bytes)': '0',
		'Time_WTXIDRELAY (milliseconds)': '0',
		'MaxTime_WTXIDRELAY (milliseconds)': '0',
		'New_[UNDOCUMENTED]s_Received (count)': '0',
		'Size_[UNDOCUMENTED] (bytes)': '0',
		'MaxSize_[UNDOCUMENTED] (bytes)': '0',
		'Time_[UNDOCUMENTED] (milliseconds)': '0',
		'MaxTime_[UNDOCUMENTED] (milliseconds)': '0',
		# End of getpeersmsginfoandclear
	}

# When a directory is finalized, we can zip it up with maximum compression, and remove the original
def finalizeLogDirectory(directory):
	global outputFilesToTransferPath, outputFilesToTransfer
	print(f'Finalizing {directory}...')
	outputFilePath = directory + '.tar.xz'
	terminal(f'tar cvf - "{directory}" | xz -9 - > "{outputFilePath}"')
	if os.path.exists(outputFilePath):
		if os.path.getsize(outputFilePath) > 0:
			terminal(f'rm -rf "{directory}"')
		else:
			print(f'\tFailed to compress {directory}, keeping original directory')
			terminal(f'rm -rf "{outputFilePath}"')
			outputFilePath = directory
	else:
		outputFilePath = directory
	# Now try to copy over the outputs to our path (preferably an external storage device)
	outputFilesToTransfer.append(outputFilePath)
	if os.path.exists(outputFilesToTransferPath):
		for source in outputFilesToTransfer:
			terminal(f'cp -r "{source}" "{outputFilesToTransferPath}"')
			print(f'\tExported {source} to {outputFilesToTransferPath}.')
		del outputFilesToTransfer[:]
	else:
		for source in outputFilesToTransfer:
			print(f'\tCould not export {source} to {outputFilesToTransferPath}, will retry next cycle.')



def log(targetDateTime, previousDirectory):
	global timerThread
	if not bitcoinUp():
		startBitcoin()
	
	timestamp = datetime.datetime.now()
	getblockchaininfo = json.loads(bitcoin('getblockchaininfo'))

	# Determine the directory to write the logs to
	if getblockchaininfo['initialblockdownload']:
		directory = f'Research_Logs/IBD_Research_Log'
	else:
		month = timestamp.strftime("%b")
		#month = timestamp.strftime("%b") + str(int(timestamp.hour)) # Temporary sample every hour
		#month = timestamp.strftime("%b") + str(int(timestamp.minute / 10) * 10) # Temporary sample every ten minute
		year = timestamp.year
		directory = f'Research_Logs/{month}_{year}_Research_Log'
		# Every month, restart the Bitcoin node to get a new fresh set of peers, along with a fresh new directory
		if len(previousDirectory) > 0 and previousDirectory != directory:
			finalizeLogDirectory(previousDirectory)
			restartBitcoin()
			# Reset the target datetime to accomodate for the time just spent finalizing the sample
			timestamp = targetDateTime = datetime.datetime.now()
			getblockchaininfo = json.loads(bitcoin('getblockchaininfo'))

	if not os.path.exists(directory):
		print('Creating directory:', directory)
		os.makedirs(directory)
		writeInitialMachineInfo(timestamp, directory)
	
	# Call the Bitcoin Core RPC commands for logging
	getpeerinfo = json.loads(bitcoin('getpeerinfo'))
	getpeersmsginfoandclear = json.loads(bitcoin('getpeersmsginfoandclear'))
	listnewbroadcastsandclear = json.loads(bitcoin('listnewbroadcastsandclear'))
	getchaintips = json.loads(bitcoin('getchaintips'))
	peersToUpdate = {}

	for peerEntry in getpeerinfo:
		address, port = splitAddress(peerEntry['addr'])
		if address not in peersToUpdate:
			peersToUpdate[address] = getPeerInfoTemplate()

		if address in listnewbroadcastsandclear['new_block_broadcasts']: peersToUpdate[address]['newBlocksReceivedCount'] = listnewbroadcastsandclear['new_block_broadcasts'][address]
		if address in listnewbroadcastsandclear['new_transaction_broadcasts']: peersToUpdate[address]['newTransactionsReceivedCount'] = listnewbroadcastsandclear['new_transaction_broadcasts'][address]
		if address in listnewbroadcastsandclear['new_transaction_fee_broadcasts']: peersToUpdate[address]['newTransactionsReceivedFee'] = listnewbroadcastsandclear['new_transaction_fee_broadcasts'][address]
		if address in listnewbroadcastsandclear['new_transaction_size_broadcasts']: peersToUpdate[address]['newTransactionsReceivedSize'] = listnewbroadcastsandclear['new_transaction_size_broadcasts'][address]

		bytesSentPerMessage = peerEntry['bytessent_per_msg']
		bytesReceivedPerMessage = peerEntry['bytesrecv_per_msg']
		bytesSentPerMessage = {k: bytesSentPerMessage[k] for k in sorted(bytesSentPerMessage, reverse = True)}
		bytesReceivedPerMessage = {k: bytesReceivedPerMessage[k] for k in sorted(bytesReceivedPerMessage, reverse = True)}

		# Self-extracted out of Bitcoin Core using this custom network logger instance
		peersToUpdate[address]['banscore'] = peerEntry['banscore']
		peersToUpdate[address]['fChance'] = peerEntry['fchance']
		peersToUpdate[address]['isTerrible'] = peerEntry['isterrible'].replace('true', '1').replace('false', '0')

		peersToUpdate[address]['port'] = int(port)
		peersToUpdate[address]['connectionID'] = int(peerEntry['id'])
		peersToUpdate[address]['connectionDuration'] = peerEntry['conntime']
		peersToUpdate[address]['secondsOffset'] = peerEntry['timeoffset']
		if 'pingtime' in peerEntry: peersToUpdate[address]['pingRoundTripTime'] = peerEntry['pingtime']
		if 'minping' in peerEntry: peersToUpdate[address]['pingMinRoundTripTime'] = peerEntry['minping']
		if 'pingwait' in peerEntry: peersToUpdate[address]['pingWaitTime'] = peerEntry['pingwait']
		peersToUpdate[address]['addressType'] = peerEntry['network']
		peersToUpdate[address]['prototolVersion'] = peerEntry['version']
		peersToUpdate[address]['softwareVersion'] = peerEntry['subver']
		peersToUpdate[address]['connectionType'] = peerEntry['connection_type']
		peersToUpdate[address]['isOutboundConnection'] = 0 if peerEntry['inbound'] else 1
		peersToUpdate[address]['services'] = '"' + json.dumps(peerEntry['servicesnames'], separators=(',', ':')).replace('"', "'") + '"'
		peersToUpdate[address]['servicesEncodedInt'] = int(peerEntry['services'], 16)
		peersToUpdate[address]['specialPermissions'] = '"' + json.dumps(peerEntry['permissions'], separators=(',', ':')).replace('"', "'") + '"'
		peersToUpdate[address]['willRelayTransactions'] = 1 if peerEntry['relaytxes'] else 0
		peersToUpdate[address]['willRelayAddrs'] = 1 if peerEntry['addr_relay_enabled'] else 0
		peersToUpdate[address]['numAddrsAccepted'] = peerEntry['addr_processed']
		peersToUpdate[address]['numAddrsDroppedFromRateLimit'] = peerEntry['addr_rate_limited']
		peersToUpdate[address]['minTransactionFeeAccepted'] = peerEntry['minfeefilter']
		peersToUpdate[address]['sendCmpctEnabledToThem'] = 1 if peerEntry['bip152_hb_to'] else 0
		peersToUpdate[address]['sendCmpctEnabledFromThem'] = 1 if peerEntry['bip152_hb_from'] else 0
		peersToUpdate[address]['lastSendTime'] = peerEntry['lastsend'] if peerEntry['lastsend'] != 0 else ''
		peersToUpdate[address]['bytesSent'] = peerEntry['bytessent']
		peersToUpdate[address]['bytesSentDistribution'] = '"' + json.dumps(bytesSentPerMessage, separators=(',', ':')).replace('"', "'") + '"'
		peersToUpdate[address]['lastReceiveTime'] = peerEntry['lastrecv'] if peerEntry['lastrecv'] != 0 else ''
		peersToUpdate[address]['bytesReceived'] = peerEntry['bytesrecv']
		peersToUpdate[address]['bytesReceivedDistribution'] = '"' + json.dumps(bytesReceivedPerMessage, separators=(',', ':')).replace('"', "'") + '"'
		peersToUpdate[address]['lastTransactionTime'] = peerEntry['last_transaction'] if peerEntry['last_transaction'] != 0 else ''
		peersToUpdate[address]['lastBlockTime'] = peerEntry['last_block'] if peerEntry['last_block'] != 0 else ''
		peersToUpdate[address]['startingBlockHeight'] = peerEntry['startingheight']
		peersToUpdate[address]['currentBlockHeightInCommon'] = peerEntry['synced_blocks']
		peersToUpdate[address]['currentHeaderHeightInCommon'] = peerEntry['synced_headers']

		clocksPerSecond = int(getpeersmsginfoandclear['CLOCKS PER SECOND'])
		if address in getpeersmsginfoandclear:
			for msg in getpeersmsginfoandclear[address].keys():
				count, size, sizeMax, time, timeMax = parseGetMsgInfoMessage(getpeersmsginfoandclear[address][msg], clocksPerSecond)
				peersToUpdate[address][f'New_{msg}s_Received (count)'] = count
				peersToUpdate[address][f'Size_{msg} (bytes)'] = size
				peersToUpdate[address][f'MaxSize_{msg} (bytes)'] = sizeMax
				peersToUpdate[address][f'Time_{msg} (milliseconds)'] = time
				peersToUpdate[address][f'MaxTime_{msg} (milliseconds)'] = timeMax

	sampleNumber = logMachineState(timestamp, directory)
	print(f'Adding Sample #{sampleNumber} to {directory}:')

	maybeLogBlock(timestamp, directory, getblockchaininfo, getchaintips)

	for address in peersToUpdate:
		logNode(address, timestamp, directory, peersToUpdate[address])
	print(f'	Sample successfully logged.')
	
	# Compute the time until the next sample will run, then schedule the run
	targetDateTime += datetime.timedelta(seconds = numSecondsPerSample)
	offset = (targetDateTime - datetime.datetime.now()).total_seconds()
	timerThread = Timer(offset, log, [targetDateTime, directory])
	timerThread.daemon = True
	timerThread.start()

if __name__ == '__main__':
	if not bitcoinUp(): startBitcoin()

	# Begin the timer
	targetDateTime = datetime.datetime.now()
	log(targetDateTime, '')

	while True:
		try:
			time.sleep(86400) # Every day
		except KeyboardInterrupt as e:
			print(e)
			timerThread.cancel()
			break

print('Logger terminated by user. Have a nice day!')