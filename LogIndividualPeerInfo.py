#!/usr/bin/env python
'''
This script logs a lot of Bitcoin node information, including the machine
specification, current machine state, blockchain state, state of each peer
connection, and state of the address manager buckets. For the initial block
download, data is written to Research_Logs/Bitcoin_IBD_Log_#/, otherwise,
the logging directory is Research_Logs/Bitcoin_Log_#/, where # counts the
number of directories. Every 10 seconds a sample is created, and every
directory has 10000 samples. The bucket logger makes a row every 100 samples.
'''

__author__ = 'Simeon Wuthier'
__contact__ = 'swuthier@uccs.edu'
__date__ = '2023/06/09'

from threading import Timer
import atexit
import concurrent.futures
import datetime
import json
import logging
import os
import platform
import psutil
import re
import shutil
import subprocess
import sys
import time
import traceback

# The logger will take one sample for every numSecondsPerSample interval
numSecondsPerSample = 10
numSamplesPerDirectory = 100 # 100*10/60 = 16.6 minutes
numSamplesPerAddressManagerBucketLog = 100

user = os.getenv('SUDO_USER')
if user is None: user = os.getenv('USER')

# The path to copy over the finalized output files (preferably an external storage device)
outputFilesToTransferPath = f'/home/{user}/Desktop/TempLogs'
if os.path.exists(f'/media/{user}/BTC'):
	outputFilesToTransferPath = f'/media/{user}/BTC/Official_Research_Logs'
elif os.path.exists('/media/sf_Shared_Folder'):
	outputFilesToTransferPath = '/media/sf_Shared_Folder/Official_Research_Logs'

# The path where the Bitcoin blockchain is stored
bitcoinDirectory = f'/home/{user}/.bitcoin'
if os.path.exists(f'/home/{user}/BitcoinFullLedger'):
	numSamplesPerDirectory = 10000 # 10000*10/60/60 = 27.7 hours
	bitcoinDirectory = f'/home/{user}/BitcoinFullLedger'


# Keep three decimal points for timestamps and time durations
timePrecision = 1000000


# Initialize the global Bitcoin-related variables
prevBlockHeight = None
prevBlockHash = None
isInStartupDownload = True
outputFilesToTransfer = []
globalNumSamples = 0
globalNumForksSeen = 0
globalMaxForkLength = 0
globalLoggingStartTimestamp = datetime.datetime.now()
globalPrevNewBuckets = {}
globalPrevTriedBuckets = {}
globalBitcoinPingTimes = {}
globalIcmpPingTimes = {}

EnabledIPv4 = False
EnabledIPv6 = False
EnabledTor = False
EnabledI2P = False
EnabledCJDNS = False

# Main function loop
def main():
	global EnabledIPv4, EnabledIPv6, EnabledTor, EnabledI2P, EnabledCJDNS, outputFilesToTransferPath, bitcoinDirectory
	os.system('clear')
	atexit.register(onExit)

	print('Which networks would you like enabled?')
	print('\t1. IPv4')
	print('\t2. IPv6')
	print('\t3. Tor')
	print('\t4. I2P')
	print('\t9. CJDNS (NOT RECOMMENDED -- REQUIRES ROOT)')
	print()
	try:
		networks = [int(i) for i in input('Separate your selections with a comma, e.g., "1,3,4": ').replace(' ', '').split(',')]
	except:
		print('You must select at least one network to operate in.')
		sys.exit()

	EnabledIPv4 = 1 in networks
	EnabledIPv6 = 2 in networks
	EnabledTor = 3 in networks
	EnabledI2P = 4 in networks
	EnabledCJDNS = 9 in networks
	if int(EnabledIPv4) + int(EnabledIPv6) + int(EnabledTor) + int(EnabledI2P) + int(EnabledCJDNS) == 0:
		print('You must select at least one network to operate in.')
		sys.exit()

	directoryTag = ''
	if int(EnabledIPv4) + int(EnabledIPv6) + int(EnabledTor) + int(EnabledI2P) == 4:
		directoryTag += '_Hybrid'
	else:
		if EnabledIPv4: directoryTag += '_IPv4'
		if EnabledIPv6: directoryTag += '_IPv6'
		if EnabledTor: directoryTag += '_Tor'
		if EnabledI2P: directoryTag += '_I2P'
	outputFilesToTransferPath += directoryTag

	if not os.path.exists(outputFilesToTransferPath):
		print(f'Note: "{outputFilesToTransferPath}" does not exist, please create it, then retry.')
		sys.exit()

	if not os.path.exists(bitcoinDirectory):
		print(f'Note: "{bitcoinDirectory}" does not exist, please create it, then retry.')
		sys.exit()

	if EnabledCJDNS:
		if os.geteuid() != 0:
			print("This script must be run as root! Use 'sudo'.")
			sys.exit(1)

	if os.path.exists(os.path.join(bitcoinDirectory, 'debug.log')):
		print('Removing debug.log from previous session...')
		terminal(f'rm -rf {os.path.join(bitcoinDirectory, "debug.log")}')

	if isTorUp(): stopTor()
	if isI2PUp(): stopI2P()
	if isCJDNSUp(): stopCJDNS()
	if isBitcoinUp(): stopBitcoin()

	if EnabledTor and not isTorUp():
		startTor()
	if EnabledI2P and not isI2PUp():
		startI2P()
	if EnabledCJDNS and not isCJDNSUp():
		startCJDNS()
	if not isBitcoinUp():
		startBitcoin()

	# Begin the timer
	targetDateTime = datetime.datetime.now()
	log(targetDateTime, '', True)

	while True:
		try:
			# Loop once every day just to ensure that the threads are active and running
			time.sleep(86400)
		except KeyboardInterrupt as e:
			print(e)
			timerThread.cancel()
			break

	print('Logger terminated by user.')

def onExit():
	if isTorUp(): stopTor()
	if isI2PUp(): stopI2P()
	if isCJDNSUp(): stopCJDNS()
	if isBitcoinUp(): stopBitcoin()
	print()
	print('Have a nice day!')

# Send a command to the Linux terminal
def terminal(cmd):
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	stdout, _ = process.communicate()
	return stdout.decode('utf-8')

# Send a command to the Bitcoin console
def bitcoin(cmd, isJSON = False):
	response = terminal('./src/bitcoin-cli -rpcuser=cybersec -rpcpassword=kZIdeN4HjZ3fp9Lge4iezt0eJrbjSi8kuSuOHeUkEUbQVdf09JZXAAGwF3R5R2qQkPgoLloW91yTFuufo7CYxM2VPT7A5lYeTrodcLWWzMMwIrOKu7ZNiwkrKOQ95KGW8kIuL1slRVFXoFpGsXXTIA55V3iUYLckn8rj8MZHBpmdGQjLxakotkj83ZlSRx1aOJ4BFxdvDNz0WHk1i2OPgXL4nsd56Ph991eKNbXVJHtzqCXUbtDELVf4shFJXame -rpcport=8332 ' + str(cmd)).strip()
	if not isJSON: return response
	return json.loads(response)

# Check if Tor instance is up
def isTorUp():
	return terminal('ps -A | grep tor').strip() != ''

# Check if I2P instance is up
def isI2PUp():
	return terminal('ps -A | grep i2pd').strip() != ''

# Check if CJDNS instance is up
def isCJDNSUp():
	return terminal('ps -A | grep cjdroute').strip() != ''

# Check if the Bitcoin Core instance is up
def isBitcoinUp():
	return terminal('ps -A | grep bitcoind').strip() != ''

# Start Tor instance
def startTor():
	if not isTorUp():
		subprocess.Popen(['gnome-terminal -t "Tor Instance" -- bash -c "cd tor-researcher && ./run.sh"'], shell=True)
		time.sleep(1)

# Start I2P instance
def startI2P():
	if not isI2PUp():
		subprocess.Popen(['gnome-terminal -t "I2P Instance" -- bash -c "cd i2pd-researcher && ./run.sh"'], shell=True)
		time.sleep(1)

# Start CJDNS instance
def startCJDNS():
	if not isCJDNSUp():
		subprocess.Popen(['gnome-terminal -t "CJDNS Instance" -- bash -c "cd cjdns-researcher && ./run.sh"'], shell=True)
		time.sleep(1)

# Start the Bitcoin Core instance
def startBitcoin():
	global isInStartupDownload
	if not isBitcoinUp():
		# If Bitcoin crashed for whatever reason before, remove the PID that would prevent it from starting again
		terminal(f'rm -rf {os.path.join(bitcoinDirectory, "bitcoind.pid")}')

	networkParams = ''
	if EnabledIPv4:
		networkParams += ' -onlynet=ipv4'
	if EnabledIPv6:
		networkParams += ' -onlynet=ipv6'
	if EnabledTor:
		networkParams += ' -onion=127.0.0.1:9050 -onlynet=onion'
	if EnabledI2P:
		networkParams += ' -i2psam=127.0.0.1:7656 -onlynet=i2p'
	if EnabledCJDNS:
		networkParams += ' -cjdnsreachable=1 -onlynet=cjdns'

	print('Starting Bitcoin...')
	rpcReady = False
	while rpcReady is False:
		if not isBitcoinUp():
			subprocess.Popen([f'gnome-terminal -t "Bitcoin Core Instance" -- bash ./run.sh noconsole{networkParams} --daemon --debug=all --donotlogtoconsole'], shell=True)
			time.sleep(5)

		time.sleep(1)
		try:
			blockHeight = int(bitcoin('getblockcount', False))
			rpcReady = True
		except: pass
	isInStartupDownload = True
	print('Bitcoin is up and ready to go')

# Stop the Tor instance
def stopTor():
	print('Stopping Tor...')
	secondCount = 0
	terminal('pkill -SIGTERM tor')
	time.sleep(1)
	while isTorUp():
		terminal('pkill -SIGTERM tor')
		time.sleep(3)
		secondCount += 3
		if secondCount >= 60: # After one minute, force shutdown
			terminal('pkill -SIGKILL tor')
			time.sleep(3)
			secondCount += 3

# Stop the I2P instance
def stopI2P():
	print('Stopping I2P...')
	secondCount = 0
	terminal('pkill -SIGTERM i2pd')
	time.sleep(1)
	while isI2PUp():
		terminal('pkill -SIGTERM i2pd')
		time.sleep(3)
		secondCount += 3
		if secondCount >= 3: # After two tries, force shutdown (I2P doesn't respond)
			terminal('pkill -SIGKILL i2pd')
			time.sleep(3)
			secondCount += 3

# Stop the CJDNS instance
def stopCJDNS():
	print('Stopping CJDNS...')
	secondCount = 0
	terminal('pkill -SIGTERM cjdroute')
	time.sleep(1)
	while isCJDNSUp():
		terminal('pkill -SIGTERM cjdroute')
		time.sleep(3)
		secondCount += 3
		if secondCount >= 60: # After one minute, force shutdown
			terminal('pkill -SIGKILL cjdroute')
			time.sleep(3)
			secondCount += 3


# Stop the Bitcoin Core instance
def stopBitcoin():
	print('Stopping Bitcoin...')
	secondCount = 0
	while isBitcoinUp():
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
	global isInStartupDownload
	stopBitcoin()
	while not isBitcoinUp():
		startBitcoin()
	isInStartupDownload = True

# Convert a UNIX epoch timestamp into a human readable format, example: Friday, Jun 09 2023, 11:11:11 PM MDT
def getHumanReadableDateTime(timestamp):
	return timestamp.strftime('%A, %b %d %Y, %-I:%M:%S %p ') + time.tzname[time.localtime().tm_isdst]

# Generate the block information CSV header line
def makeBlockStateHeader():
	line = 'Timestamp,'
	line += 'Timestamp (UNIX epoch),'
	line += 'Block Height,'
	line += '"Block Status (active, headers-only, valid-fork, valid-headers, valid-headers-fork, checkpoint, assume-valid)",'
	line += 'Is Fork,'
	line += 'Fork Length,'
	line += 'Block Timestamp (UNIX epoch),'
	line += 'Number of Confirmations,'
	line += 'Block Hash,'
	line += 'Block Size (bytes),'
	line += 'Block Size Including Segregated Witnesses (bytes),'
	line += 'Stripped Size (excluding witness data) (bytes),'
	line += 'Propagation Time Duration (using system time) (milliseconds),'
	line += 'Network Adjusted Block Propagation Time Duration (milliseconds),'
	line += 'Received By,'
	line += 'Difficulty,'
	line += 'Chainwork,'
	line += 'Weight (BIP 141),'
	line += 'Version,'
	line += 'Nonce,'
	line += 'Number of Transactions (tx),'
	line += 'Tx Rate (tx/second),'
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
	line += 'Coinbase Subsidy Reward Without Fees (satoshi),'
	line += 'Coinbase Subsidy Reward With Fees (satoshi),'
	line += 'Coinbase Address (Block Solver),'
	line += 'Coinbase Transaction Type,'
	line += 'Coinbase Transaction Assembly,'
	return line

# If any new blocks exist, log them
def maybeLogBlockState(timestamp, directory, getblockchaininfo, getchaintips, newblockbroadcastsblockinformation, newheaderbroadcastsblockinformation):
	global prevBlockHeight, prevBlockHash, isInStartupDownload, globalNumForksSeen, globalMaxForkLength

	# Quickly check if any new blocks have arrived, if they haven't 
	if prevBlockHash is not None:
		for i, tip in enumerate(getchaintips):
			if tip['status'] == 'active':
				# No new block has been received, return
				if prevBlockHash == tip['hash']: return
				break

	filePath = os.path.join(directory, 'blockchain_state_info.csv')
	if not os.path.exists(filePath):
		print(f'Creating blockchain state file')
		file = open(filePath, 'w')
		file.write(makeBlockStateHeader() + '\n')
		prevLine = ''
	else:
		# Read the last line from the file
		with open(filePath, 'r') as f:
			prevLines = f.readlines()
			if len(prevLines) > 1: prevLine = splitIndividualCsvLine(prevLines[-1])
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
 
	# If the logger has restarted, restore the previous values and check for changes
	if prevBlockHash is None and len(prevLine) > 0:
		prevBlockHeight = prevLine[2]
		prevBlockHash = prevLine[8]
		for i, tip in enumerate(getchaintips):
			if tip['status'] == 'active':
				# No new block has been received, return
				if prevBlockHash == tip['hash']: return
				break

	timestampSeconds = int(getTimestampEpoch(timestamp) * timePrecision) / timePrecision

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
	if prevBlockHeight is None or allowSkippedBlocks or isInStartupDownload:
		prevBlockHeight = activeTip['height']

	# Construct an array of all the tips we want to process
	numBlocks = activeTip['height'] - prevBlockHeight + 1
	# maxNumPreviousBlocksToProcess = 12 # If we're more than this many blocks behind, we only download the most recent ones
	# if numBlocks > maxNumPreviousBlocksToProcess:
	# 	prevBlockHeight = activeTip['height'] - maxNumPreviousBlocksToProcess + 1
	# 	numBlocks = maxNumPreviousBlocksToProcess

	tipsToProcess = []
	for height in range(prevBlockHeight + 1, activeTip['height']):
		tipsToProcess.append({
			'height': height,
			'hash': '',
			'status': activeTip['status'],
			'isFork': '1' if ('fork' in activeTip['status']) else '0',
			'forkLength': activeTip['branchlen'],
		})
	tipsToProcess.append({
		'height': activeTip['height'],
		'hash': activeTip['hash'],
		'status': activeTip['status'],
		'isFork': '1' if ('fork' in activeTip['status']) else '0',
		'forkLength': activeTip['branchlen'],
	})
	for tip in getchaintips:
		tipsToProcess.append({
			'height': tip['height'],
			'hash': tip['hash'],
			'status': tip['status'],
			'isFork': '1' if ('fork' in tip['status']) else '0',
			'forkLength': tip['branchlen'],
		})

	if len(tipsToProcess) == 1:
		isInStartupDownload = False

	# Now loop through all the tips and log each one as a separate line in the CSV
	lines = ''
	for tip in tipsToProcess:
		height = tip['height']
		tipStatus = tip['status']
		tipIsFork = tip['isFork']
		forkLength = tip['forkLength']
		blockHash = tip['hash']
		try:
			getblockstats = bitcoin(f'getblockstats {height}', True)
			if blockHash == '': blockHash = getblockstats['blockhash']
		except:
			getblockstats = {'avgfee':'','avgfeerate':'','avgtxsize':'','blockhash':'','feerate_percentiles':['','','','',''],'height':'','ins':'','maxfee':'','maxfeerate':'','maxtxsize':'','medianfee':'','mediantime':'','mediantxsize':'','minfee':'','minfeerate':'','mintxsize':'','outs':'','subsidy':'','swtotal_size':'','swtotal_weight':'','swtxs':'','time':'','total_out':'','total_size':'','total_weight':'','totalfee':'','txs':'','utxo_increase':'','utxo_size_inc':'','utxo_increase_actual':'','utxo_size_inc_actual':''}
		
		# During initial block download mode, don't log the target header since we don't have that information
		if blockHash == '' and (allowSkippedBlocks or isInStartupDownload): continue
		
		try:
			getblock = bitcoin(f'getblock {blockHash}', True)
		except:
			if allowSkippedBlocks or isInStartupDownload: continue
			try:
				# If the block doesn't work, try the header instead, it just won't have the transaction info
				getblock = bitcoin(f'getblockheader {blockHash}', True)
				getblockmock = {'hash':'','confirmations':'','height':'','version':'','versionHex':'','merkleroot':'','time':'','mediantime':'','nonce':'','bits':'','difficulty':'','chainwork':'','nTx':'','previousblockhash':'','strippedsize':'','size':'','weight':'','tx':''}
				for key in getblockmock:
					# Fill in the missing fields, such as 'size'
					if key not in getblock:
						getblock[key] = getblockmock[key]
			except:
				getblock = {'hash':'','confirmations':'','height':'','version':'','versionHex':'','merkleroot':'','time':'','mediantime':'','nonce':'','bits':'','difficulty':'','chainwork':'','nTx':'','previousblockhash':'','strippedsize':'','size':'','weight':'','tx':''}

		try:
			coinbaseTransactionHash = getblock['tx'][0]
			gettxout = bitcoin(f'gettxout {coinbaseTransactionHash} 0', True)
		except:
			coinbaseTransactionHash = ''
			gettxout = {'bestblock':'','confirmations':'','value':'','scriptPubKey':{'asm':'','desc':'','hex':'','address':'','type':''},'coinbase':True}

		try:
			getchaintxstats = bitcoin(f'getchaintxstats {numBlocks} "{blockHash}"', True)
		except:
			getchaintxstats = {'time':'','txcount':'','window_final_block_hash':'','window_final_block_height':'','window_block_count':'','window_tx_count':'','window_interval':'','txrate':''}

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

		# If there is a hash match, then include the block propagation time information
		if blockHash != '' and newblockbroadcastsblockinformation['hash'] == blockHash:
			blockPropTime = newblockbroadcastsblockinformation['propagation_time']
			blockMedPropTime = newblockbroadcastsblockinformation['propagation_time_median_of_peers']
			blockReceivedBy = newblockbroadcastsblockinformation['node_received_by']
		else:
			blockPropTime = ''
			blockMedPropTime = ''
			blockReceivedBy = ''

		lines += '"' + getHumanReadableDateTime(timestamp) + '",'
		lines += str(timestampSeconds) + ','
		lines += str(height) + ','
		lines += str(tipStatus) + ','
		lines += str(tipIsFork) + ','
		lines += str(forkLength) + ','
		lines += str(getblock['time']) + ','
		lines += str(getblock['confirmations']) + ','
		lines += str(blockHash) + ','
		lines += str(getblock['size']) + ','
		lines += str(getblockstats['total_size']) + ','
		lines += str(getblock['strippedsize']) + ','
		lines += str(blockPropTime) + ','
		lines += str(blockMedPropTime) + ','
		lines += str(blockReceivedBy) + ','
		lines += str(getblock['difficulty']) + ','
		lines += str(getblock['chainwork']) + ','
		lines += str(getblock['weight']) + ','
		lines += str(getblock['version']) + ','
		lines += str(getblock['nonce']) + ','
		lines += str(getblock['nTx']) + ',' # Same as getblockstats['txs']
		if 'txrate' in getchaintxstats: lines += str(getchaintxstats['txrate']) + ','
		else: lines += ','

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
		if 'subsidy' in getblockstats: lines += str(getblockstats['subsidy']) + ','
		else: lines += ','
		lines += str(gettxout['value'] * 100000000) + ',' # Same as getblockstats['subsidy'] + getblockstats['totalfee']
		if 'address' in gettxout['scriptPubKey']: lines += str(gettxout['scriptPubKey']['address']) + ','
		else: lines += ','
		lines += str(gettxout['scriptPubKey']['type']) + ','
		lines += str(gettxout['scriptPubKey']['asm']) + ','
		lines += '\n'
		
		print(f'\tLogged {tipStatus} block at height {height}.')
		# Update the previous block info
		if tipStatus == 'active':
			prevBlockHash = blockHash
			prevBlockHeight = height
		
		if tipIsFork == '1' and forkLength > 0:
			globalNumForksSeen += 1
			if forkLength > globalMaxForkLength:
				globalMaxForkLength = forkLength

	# Finally, write the blockchain info to the output file
	file.write(lines)
	file.close()
	return

# Return the size of a directory
def getDirectorySize(directory):
	output = terminal(f'du --summarize --bytes {directory}').split()
	if len(output) == 0: return ''
	return output[0]

# Generate the machine info CSV header line
def writeInitialMachineInfo(timestamp, directory):
	contents = 'Bitcoin Core Version (./src/bitcoind --version | head -2):\n'
	contents += '\t' + terminal('./src/bitcoin-cli --version | head -2').strip().replace('\n', '\n\t') + '\n'
	contents += '\nLink to Git Version (git config --get remote.origin.url and git rev-parse HEAD):\n'
	contents += '\t' + terminal('git config --get remote.origin.url').strip().replace('.git', '').replace('\n', '\n\t') + '/tree/' + terminal('git rev-parse HEAD').strip().replace('\n', '\n\t') + '\n'
	contents += '\nPython (python3 --version):\n'
	contents += '\t' + terminal('python3 --version').strip().replace('\n', '\n\t') + '\n'
	contents += '\nOperating System (lsb_release -idrc):\n'
	contents += '\t' + terminal('lsb_release -idrc').strip().replace('\n', '\n\t') + '\n'
	contents += '\nProcessor (lscpu):\n'
	contents += '\t' + terminal('lscpu').strip().replace('\n', '\n\t') + '\n'
	contents += '\nNetwork (ifconfig):\n'
	contents += '\t' + terminal('ifconfig').strip().replace('\n', '\n\t') + '\n'
	contents += '\nMemory (cat /proc/meminfo):\n'
	contents += '\tRAM:' + (str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + ' GB').rjust(23) + '\n'
	contents += '\t' + terminal('cat /proc/meminfo').strip().replace('\n', '\n\t') + '\n'
	contents += '\nDirectory Creation Time (date):\n'
	contents += '\t' + str(timestamp) + '\n'
	file = open(os.path.join(directory, 'machine_info.txt'), 'w')
	file.write(contents)
	file.close()

# Given a raw memory string from the Linux "top" command, return the number of bytes
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

# Split an individual line within a CSV, considering both quoted string tokens and blank cells
def splitIndividualCsvLine(line):
	split_pattern = re.compile(r'(?:"([^"]*)"|([^,]*))(?:,|$)')
	split_tokens = split_pattern.findall(line)
	tokens = []
	for token in split_tokens:
		if token[0] != '':
			tokens.append(token[0])
		else:
			tokens.append(token[1])
	return tokens

# Generate the machine state CSV header line
def makeMachineStateHeader():
	line = 'Timestamp,'
	line += 'Timestamp (UNIX epoch),'
	line += 'Difference from Network Adjusted Timestamp (milliseconds),'
	line += 'Number of Inbound Peer Connections,'
	line += 'Number of Outbound Peer Connections,'
	line += 'Active Peer Connection File Names,'
	
	line += 'Block Propagation Time Duration (using system time) (milliseconds),'
	line += 'Block Propagation Time Duration (using network adjusted time) (milliseconds),'
	line += 'Last Block Hash,'
	line += 'Last Block Received By,'
	line += 'Header Propagation Time Duration (using system time) (milliseconds),'
	line += 'Header Propagation Time Duration (using network adjusted time) (milliseconds),'
	line += 'Last Header Hash,'
	line += 'Last Header Received By,'

	line += 'Blockchain Warning Message,'
	line += 'Is Blockchain in Initial Block Download,'
	line += 'Blockchain Verification Progress (percent),'
	line += 'Blockchain Number of Blocks,'
	line += 'Blockchain Number of Headers,'
	line += 'Blockchain Size (bytes),'
	line += 'Is Blockchain Pruned,'
	line += 'Maximum Pruned Blockchain Size (bytes),'
	line += 'Pruned Block Height,'
	line += 'Bitcoin Directory Size (bytes),'
	line += 'Is Mempool Fully Loaded,'
	line += 'Number of Mempool Transactions,'
	line += 'Mempool Transaction Sizes (BIP 141) (bytes),'
	line += 'Total Mempool Size (bytes),'
	line += 'Maximum Total Mempool Size (bytes),'
	line += 'Minimum Tx Fee to be Accepted (satoshi/byte),'
	line += 'Network Bytes Sent (bytes),'
	line += 'Network Bytes Received (bytes),'
	line += 'Network Packets Sent (packets),'
	line += 'Network Packets Received (packets),'
	line += 'Bitcoin Process ID,'
	line += 'Bitcoin Process Virtual Memory (bytes),'
	line += 'Bitcoin Process Memory (bytes),'
	line += 'Bitcoin Process Shared Memory (bytes),'
	line += 'Bitcoin Process Memory (percent),'
	line += 'Bitcoin Process CPU (percent),'
	line += 'Machine CPU (percent),'
	line += 'Machine CPU Frequency (megahertz),'
	line += 'Machine Virtual Memory (percent),'
	line += 'Machine Virtual Memory (bytes),'
	line += 'Machine Swap Memory (percent),'
	line += 'Machine Swap Memory (bytes),'
	line += 'Machine Disk Usage (percent),'
	line += 'Machine Disk Usage (bytes),'
	return line

# Convert a datetime object to a UNIX epoch
def getTimestampEpoch(datetimeObject):
	return datetimeObject.astimezone(datetime.timezone.utc).timestamp()

# Convert a UNIX epoch to a datetime object
def getDatetimeFromEpoch(timestampSeconds):
	return datetime.datetime.fromtimestamp(timestampSeconds)

# Log the state of the machine to file, returns the sample number, or -1 to terminate the sample
def logMachineState(timestamp, directory, getpeerinfo, getblockchaininfo, getmempoolinfo, newblockbroadcastsblockinformation, newheaderbroadcastsblockinformation, timestampMedianDifference):
	global targetDateTime
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
			if len(prevLines) > 1: prevLine = splitIndividualCsvLine(prevLines[-1])
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
 
	timestampSeconds = int(getTimestampEpoch(timestamp) * timePrecision) / timePrecision
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

	numInboundPeers = 0
	numOutboundPeers = 0
	activePeerConnectionFiles = ''
	for peerEntry in getpeerinfo:
		if peerEntry['inbound']: numInboundPeers += 1
		else: numOutboundPeers += 1
		address, port = splitAddress(peerEntry['addr'])
		activePeerConnectionFiles += getFileNameFromAddress(address) + ' '

	line = '"' + getHumanReadableDateTime(timestamp) + '",'
	line += str(timestampSeconds) + ','
	line += str(timestampMedianDifference) + ','
	line += str(numInboundPeers) + ','
	line += str(numOutboundPeers) + ','
	line += '"' + str(activePeerConnectionFiles.strip()) + '",'
	line += str(newblockbroadcastsblockinformation['propagation_time']) + ','
	line += str(newblockbroadcastsblockinformation['propagation_time_median_of_peers']) + ','
	line += str(newblockbroadcastsblockinformation['hash']) + ','
	line += str(newblockbroadcastsblockinformation['node_received_by']) + ','
	line += str(newheaderbroadcastsblockinformation['propagation_time']) + ','
	line += str(newheaderbroadcastsblockinformation['propagation_time_median_of_peers']) + ','
	line += str(newheaderbroadcastsblockinformation['hash']) + ','
	line += str(newheaderbroadcastsblockinformation['node_received_by']) + ','
	line += str(getblockchaininfo['warnings']) + ','
	line += str(1 if getblockchaininfo['initialblockdownload'] else 0) + ','
	line += str(getblockchaininfo['verificationprogress'] * 100) + ','
	line += str(getblockchaininfo['blocks']) + ','
	line += str(getblockchaininfo['headers']) + ','
	line += str(getblockchaininfo['size_on_disk']) + ','
	line += str(1 if getblockchaininfo['pruned'] else 0) + ','
	if 'prune_target_size' in getblockchaininfo:
		line += str(getblockchaininfo['prune_target_size']) + ','
	else: line += ','
	if 'pruneheight' in getblockchaininfo:
		line += str(getblockchaininfo['pruneheight']) + ','
	else: line += ','
	line += str(getDirectorySize(bitcoinDirectory)) + ','
	line += str(1 if getmempoolinfo['loaded'] else 0) + ','
	line += str(getmempoolinfo['size']) + ','
	line += str(getmempoolinfo['bytes']) + ','
	line += str(getmempoolinfo['usage']) + ','
	line += str(getmempoolinfo['maxmempool']) + ','
	line += str(getmempoolinfo['mempoolminfee'] * 100000000/1024) + ',' # Converts from BTC/kilobyte to satoshi/byte
	line += str(networkData['bytes_sent']) + ','
	line += str(networkData['bytes_received']) + ','
	line += str(networkData['packets_sent']) + ','
	line += str(networkData['packets_received']) + ','
	line += str(individualProcessData['process_ID']) + ','
	line += str(individualProcessData['virtual_memory']) + ','
	line += str(individualProcessData['memory']) + ','
	line += str(individualProcessData['shared_memory']) + ','
	line += str(individualProcessData['memory_percent']) + ','
	line += str(individualProcessData['cpu_percent']) + ','
	line += str(cpuPercent) + ','
	line += str(cpuFrequency) + ','
	line += str(virtualMemoryPercent) + ','
	line += str(virtualMemory) + ','
	line += str(swapMemoryPercent) + ','
	line += str(swapMemory) + ','
	line += str(diskUsagePercent) + ','
	line += str(diskUsage) + ','
	file.write(line + '\n')
	file.close()
	return numPrevLines

# Generate the address manager bucket info CSV header line
def makeAddressManagerBucketStateHeader(numNewBuckets, numTriedBuckets):
	line = 'Timestamp,'
	line += 'Timestamp (UNIX epoch),'
	line += 'Number of Tried Entries,'
	line += 'Number of New Entries,'
	line += 'IPv4 New Addresses (count),'
	line += 'IPv4 Tried Addresses (count),'
	line += 'IPv6 New Addresses (count),'
	line += 'IPv6 Tried Addresses (count),'
	line += 'TOR (v2 or v3) New Addresses (count),'
	line += 'TOR (v2 or v3) Tried Addresses (count),'
	line += 'I2P New Addresses (count),'
	line += 'I2P Tried Addresses (count),'
	line += 'CJDNS New Addresses (count),'
	line += 'CJDNS Tried Addresses (count),'
	line += 'Internal New Addresses (count),'
	line += 'Internal Tried Addresses (count),'
	line += 'Unroutable New Addresses (count),'
	line += 'Unroutable Tried Addresses (count),'
	line += 'Timestamp of Last Good Call (move from new to tried),'
	line += 'Number of Tried Buckets,'
	line += 'Number of New Buckets,'
	line += 'Number of Tried Added Entries,'
	line += 'Number of Tried Removed Entries (addresses prefixed with \'removed_\'),'
	line += 'Number of Tried Entry Updates,'
	line += 'Number of New Added Entries,'
	line += 'Number of New Removed Entries (addresses prefixed with \'removed_\'),'
	line += 'Number of New Entry Updates,'
	for i in range(numTriedBuckets):
		if i == 0:
			line += f'"Tried Bucket {i + 1} Changes (JSON: [type (1:IPv4, 2:IPv6, 3:TorV2, 4:TorV3, 5:I2P, 6:CJDNS), fChance, isTerrible, nInstances, nTime, lastTriedTime, nAttempts, lastCountedAttemptTime, lastSuccessTime, sourceAddress])",'
		else:
			line += f'Tried Bucket {i + 1} Changes (JSON),'
	for i in range(numNewBuckets):
		if i == 0:
			line += f'"New Bucket {i + 1} Changes (JSON: [type (1:IPv4, 2:IPv6, 3:TorV2, 4:TorV3, 5:I2P, 6:CJDNS), fChance, isTerrible, nInstances, nTime, lastTriedTime, nAttempts, lastCountedAttemptTime, lastSuccessTime, sourceAddress])",'
		else:
			line += f'New Bucket {i + 1} Changes (JSON),'
	return line

# Log the bucket info, which is a time consuming process so it is ran every numSamplesPerAddressManagerBucketLog samples
def logAddressManagerBucketInfo(timestamp, directory):
	global globalPrevNewBuckets, globalPrevTriedBuckets
	print('\tLogging address manager bucket information...')
	getbucketinfo = bitcoin('getbucketinfo', True)
	numTriedBuckets = 256
	numNewBuckets = 1024

	filePath = os.path.join(directory, 'address_manager_bucket_info.csv')
	if not os.path.exists(filePath):
		print(f'\t\tCreating address manager bucket info file')
		file = open(filePath, 'w')
		file.write(makeAddressManagerBucketStateHeader(numNewBuckets, numTriedBuckets) + '\n')
		prevLine = ''
		numPrevLines = 1
	else:
		# Read the last line from the file
		with open(filePath, 'r') as f:
			prevLines = f.readlines()
			if len(prevLines) > 1: prevLine = splitIndividualCsvLine(prevLines[-1])
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

	# On a logger restart, rather than re-exporting the entire bucket list, assume that no changes have been made
	if len(prevLine) > 0 and globalPrevNewBuckets == {} and globalPrevTriedBuckets == {}:
		globalPrevNewBuckets = getbucketinfo['New buckets']
		globalPrevTriedBuckets = getbucketinfo['Tried buckets']
 
	timestampSeconds = int(getTimestampEpoch(timestamp) * timePrecision) / timePrecision

	line = '"' + getHumanReadableDateTime(timestamp) + '",'
	line += str(timestampSeconds) + ','
	line += str(getbucketinfo['Number of tried entries']) + ','
	line += str(getbucketinfo['Number of (unique) new entries']) + ','
	line += str(getbucketinfo['Number of IPv4 new addresses']) + ','
	line += str(getbucketinfo['Number of IPv4 tried addresses']) + ','
	line += str(getbucketinfo['Number of IPv6 new addresses']) + ','
	line += str(getbucketinfo['Number of IPv6 tried addresses']) + ','
	line += str(getbucketinfo['Number of TOR (v2 or v3) new addresses']) + ','
	line += str(getbucketinfo['Number of TOR (v2 or v3) tried addresses']) + ','
	line += str(getbucketinfo['Number of I2P new addresses']) + ','
	line += str(getbucketinfo['Number of I2P tried addresses']) + ','
	line += str(getbucketinfo['Number of CJDNS new addresses']) + ','
	line += str(getbucketinfo['Number of CJDNS tried addresses']) + ','
	line += str(getbucketinfo['Number of internal new addresses']) + ','
	line += str(getbucketinfo['Number of internal tried addresses']) + ','
	line += str(getbucketinfo['Number of unrouteable new addresses']) + ','
	line += str(getbucketinfo['Number of unrouteable tried addresses']) + ','
	if 'Last time Good was called' in getbucketinfo:
		line += str(getbucketinfo['Last time Good was called']) + ','
	else: line += ','
	line += str(numTriedBuckets) + ','
	line += str(numNewBuckets) + ','
	newBucketsColumns = ''
	triedBucketsColumns = ''
	numAddedNewEntries = 0
	numAddedTriedEntries = 0
	numRemovedNewEntries = 0
	numRemovedTriedEntries = 0
	numNewUpdates = 0
	numTriedUpdates = 0
	
	# Add the bucket entries that don't currently exist
	for i in range(numNewBuckets):
		if str(i) not in getbucketinfo['New buckets']:
			getbucketinfo['New buckets'][str(i)] = {}
	for i in range(numNewBuckets):
		if str(i) not in getbucketinfo['Tried buckets']:
			getbucketinfo['Tried buckets'][str(i)] = {}
	getbucketinfo['New buckets'] = dict(sorted(getbucketinfo['New buckets'].items(), key=lambda item: int(item[0])))
	getbucketinfo['Tried buckets'] = dict(sorted(getbucketinfo['Tried buckets'].items(), key=lambda item: int(item[0])))

	# Loop through each new bucket			
	for i in getbucketinfo['New buckets']:
		changedNewBucketEntries = {}
		# Remove all the address entries that have not changed, that way we only see those that have changed
		for address in getbucketinfo['New buckets'][i]:
			addressHasChanged = False
			if i in globalPrevNewBuckets and address in globalPrevNewBuckets[i]:
				for j in range(7): # [fChance, isTerrible, lastTriedTime, nAttempts, lastAttemptTime, lastSuccessTime, sourceAddress]
					if globalPrevNewBuckets[i][address][j] != getbucketinfo['New buckets'][i][address][j]:
						numNewUpdates += 1
						addressHasChanged = True
						break
			else:
				numAddedNewEntries += 1
				addressHasChanged = True
			if addressHasChanged:
				#print(f'\tUpdating {address} in new bucket #{i + 1}')
				changedNewBucketEntries[address] = getbucketinfo['New buckets'][i][address]
		# Now check for addresses that have been removed from the current bucket
		if i in globalPrevNewBuckets:
			for address in globalPrevNewBuckets[i]:
				if address in getbucketinfo['New buckets'][i]: continue
				changedNewBucketEntries['removed_' + address] = globalPrevNewBuckets[i][address]
				numRemovedNewEntries += 1


		newBucketsColumns += '"' + json.dumps(changedNewBucketEntries, separators=(',', ':')).replace('"', "'") + '",'
	# Loop through each tried bucket
	for i in getbucketinfo['Tried buckets']:
		changedTriedBucketEntries = {}
		# Remove all the address entries that have not changed, that way we only see those that have changed
		for address in getbucketinfo['Tried buckets'][i]:
			addressHasChanged = False
			if i in globalPrevTriedBuckets and address in globalPrevTriedBuckets[i]:
				for j in range(7): # [fChance, isTerrible, lastTriedTime, nAttempts, lastAttemptTime, lastSuccessTime, sourceAddress]
					if globalPrevTriedBuckets[i][address][j] != getbucketinfo['Tried buckets'][i][address][j]:
						numTriedUpdates += 1
						addressHasChanged = True
						break
			else:
				numAddedTriedEntries += 1
				addressHasChanged = True
			if addressHasChanged:
				#print(f'\tUpdating {address} in tried bucket #{i + 1}')
				changedTriedBucketEntries[address] = getbucketinfo['Tried buckets'][i][address]
		# Now check for addresses that have been removed from the current bucket
		if i in globalPrevTriedBuckets:
			for address in globalPrevTriedBuckets[i]:
				if address in getbucketinfo['Tried buckets'][i]: continue
				changedTriedBucketEntries['removed_' + address] = globalPrevTriedBuckets[i][address]
				numRemovedTriedEntries += 1
		triedBucketsColumns += '"' + json.dumps(changedTriedBucketEntries, separators=(',', ':')).replace('"', "'") + '",'
	
	line += str(numAddedTriedEntries) + ','
	line += str(numRemovedTriedEntries) + ','
	line += str(numTriedUpdates) + ','
	line += str(numAddedNewEntries) + ','
	line += str(numRemovedNewEntries) + ','
	line += str(numNewUpdates) + ','
	line += str(triedBucketsColumns) # Already has a comma
	line += str(newBucketsColumns) # Already has a comma
	file.write(line + '\n')
	file.close()

	# Save the bucket info for the next time that we sample it
	globalPrevNewBuckets = getbucketinfo['New buckets']
	globalPrevTriedBuckets = getbucketinfo['Tried buckets']

# Generate the main peer CSV header line
def makeMainPeerHeader(address):
	line = 'Timestamp,'
	line += 'Timestamp (UNIX epoch),'
	line += 'Connection Count,'
	line += 'Connection Duration (seconds),'
	line += f'Port for {address},'
	line += 'Number of Unique Blocks Received,'
	line += 'Number of Unique Transactions Received,'
	line += 'Aggregate of Unique Transaction Fees (satoshi),'
	line += 'Aggregate of Unique Transaction Sizes (bytes),'
	line += 'Number of Redundant Transactions Received,'
	line += 'Aggregate of Redundant Transaction Sizes (bytes),'
	line += 'Peer Banscore (accumulated misbehavior score for this peer),'
	line += 'Addrman fChance Score (the relative chance that this entry should be given when selecting nodes to connect to),'
	line += 'Addrman isTerrible Rating (if the statistics about this entry are bad enough that it can just be deleted),'
	line += 'Node Time Offset (seconds),'
	line += 'Bitcoin Ping Round Trip Time (milliseconds),'
	line += 'ICMP Ping Round Trip Time (milliseconds),'
	line += 'Address/Network Type,'
	line += 'Protocol Version,'
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
	line += 'Minimum Accepted Transaction Fee (BIP 133) (satoshi/byte),'
	line += 'Is SendCMPCT Enabled To Them,'
	line += 'Is SendCMPCT Enabled From Them,'
	line += 'Last Message Send Time (UNIX epoch),'
	line += 'Number of Bytes Sent,'
	line += 'Number of Bytes Received,'
	line += 'Distribution of Bytes Sent,'
	line += 'Distribution of Bytes Received,'
	line += 'Last Message Receive Time (UNIX epoch),'
	line += 'Last Valid Transaction Received Time (UNIX epoch),'
	line += 'Last Valid Block Received Time (UNIX epoch),'
	line += 'Starting Block Height,'
	line += 'Current Block Height In Common,'
	line += 'Current Header Height In Common,'
	line += 'List of Undocumented Messages Received,'
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

# Given an address return the file name
def getFileNameFromAddress(address):
	return re.sub('[^A-Za-z0-9\.]', '-', address) + '.csv'

# Log the state of the node to file, returns the sample number
def logNode(address, timestamp, directory, updateInfo):
	filePath = os.path.join(directory, getFileNameFromAddress(address))
	if not os.path.exists(filePath):
		# Create a new file
		prevLine = ''
		numPrevLines = 1
		print(f'	Logging {address} ({numPrevLines} sample)')
		file = open(filePath, 'w')
		file.write(makeMainPeerHeader(address) + '\n')
	else:
		# Read the last line from the file
		with open(filePath, 'r') as f:
			prevLines = f.readlines()
			# Don't let prevLine contain the header; data only
			if len(prevLines) > 1: prevLine = splitIndividualCsvLine(prevLines[-1])
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

	timestampSeconds = int(getTimestampEpoch(timestamp) * timePrecision) / timePrecision
	connectionCount = 1
	if prevLine != '':
		if prevLine[2] != '':
			connectionCount = int(prevLine[2])
		# Check if this is the same connection or a new connection
		if (prevLine[4] != '' and updateInfo['port'] != int(prevLine[4])) or (prevLine[3] != '' and updateInfo['connectionDuration'] < float(prevLine[3])):
			connectionCount += 1


	line = '"' + getHumanReadableDateTime(timestamp) + '",'
	line += str(timestampSeconds) + ','
	line += str(connectionCount) + ','
	line += str(updateInfo['connectionDuration']) + ','
	line += str(updateInfo['port']) + ','
	line += str(updateInfo['newBlocksReceivedCount']) + ','
	line += str(updateInfo['newTransactionsReceivedCount']) + ','
	line += str(updateInfo['newTransactionsReceivedFee']) + ','
	line += str(updateInfo['newTransactionsReceivedSize']) + ','
	line += str(updateInfo['redundantTransactionsReceivedCount']) + ','
	line += str(updateInfo['redundantTransactionsReceivedSize']) + ','
	line += str(updateInfo['banscore']) + ','
	line += str(updateInfo['fChance']) + ','
	line += str(updateInfo['isTerrible']) + ','
	line += str(updateInfo['secondsOffset']) + ','
	line += str(updateInfo['bitcoinPingRoundTripTime']) + ','
	line += str(updateInfo['icmpPingRoundTripTime']) + ','
	line += str(updateInfo['addressType']) + ','
	line += str(updateInfo['prototolVersion']) + ','
	line += '"' + str(updateInfo['softwareVersion']) + '",'
	line += str(updateInfo['connectionType']) + ','
	line += str(updateInfo['isOutboundConnection']) + ','
	line += str(updateInfo['services']) + ','
	line += str(updateInfo['servicesEncodedInt']) + ','
	line += str(updateInfo['specialPermissions']) + ','
	line += str(updateInfo['willRelayTransactions']) + ','
	line += str(updateInfo['willRelayAddrs']) + ','
	line += str(updateInfo['numAddrsAccepted']) + ','
	line += str(updateInfo['numAddrsDroppedFromRateLimit']) + ','
	try:
		line += str(float(updateInfo['minTransactionFeeAccepted']) / 1024) + ',' # Convert from satoshi/kilobyte to satoshi/byte
	except: line += ','
	line += str(updateInfo['sendCmpctEnabledToThem']) + ','
	line += str(updateInfo['sendCmpctEnabledFromThem']) + ','
	line += str(updateInfo['lastSendTime']) + ','
	line += str(updateInfo['bytesSent']) + ','
	line += str(updateInfo['bytesReceived']) + ','
	line += str(updateInfo['bytesSentDistribution']) + ','
	line += str(updateInfo['bytesReceivedDistribution']) + ','
	line += str(updateInfo['lastReceiveTime']) + ','
	line += str(updateInfo['lastTransactionTime']) + ','
	line += str(updateInfo['lastBlockTime']) + ','
	line += str(updateInfo['startingBlockHeight']) + ','
	line += str(updateInfo['currentBlockHeightInCommon']) + ','
	line += str(updateInfo['currentHeaderHeightInCommon']) + ','
	line += '"' + str(updateInfo['Undocumented_Messages']) + '",'
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

# Returns a blank peer JSON object ready to be filled with information
def getPeerInfoTemplate():
	return {
		# Start of listnewbroadcastsandclear
		'newBlocksReceivedCount': '0',
		'newTransactionsReceivedCount': '0',
		'newTransactionsReceivedFee': '0',
		'newTransactionsReceivedSize': '0',
		'redundantTransactionsReceivedCount': '0',
		'redundantTransactionsReceivedSize': '0',
		# End of listnewbroadcastsandclear
		# Start of getpeerinfo
		'banscore': '',
		'fChance': '',
		'isTerrible': '',
		'port': '',
		'connectionID': '',
		'connectionDuration': '',
		'secondsOffset': '',
		'bitcoinPingRoundTripTime': '',
		'icmpPingRoundTripTime': '',
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
		'Undocumented_Messages': '',
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
	terminal(f'cd "{directory}" && tar -cf - . | xz -9e - > "../{outputFilePath}"')
	#terminal(f'tar -C "{directory}" -cf - . | xz -9e - > "{outputFilePath}"')
	#terminal(f'tar cf - "{directory}" | xz -9e - > "{outputFilePath}"') # Also compresses the directory
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
			print(f'\tExported {source} to {outputFilesToTransferPath}')
		del outputFilesToTransfer[:]
	else:
		for source in outputFilesToTransfer:
			print(f'\tCould not export {source} to {outputFilesToTransferPath}, will retry next cycle.')

# Given a list of addresses, concurrently send an ICMP ping to each of them
def sendIcmpPings(addresses):
	# Create a ThreadPoolExecutor for the ping messages
	executor = concurrent.futures.ThreadPoolExecutor()
	futureDict = {executor.submit(terminal, 'ping -c 1 -W 5 ' + address): address for address in addresses}
	return executor, futureDict

# Resolve the concurrent ICMP ping states, returning the result of each ICMP ping
def resolveIcmpPings(executor, futureDict, backupPingsAddresses):
	result = {}
	for future in concurrent.futures.as_completed(futureDict):
		address = futureDict[future]
		try:
			data = future.result()
			# Find the avg ping latency
			match = re.search('avg/max/mdev = ([\d\.]+)/', data)
			if match:
				result[address] = match.group(1)
			else:
				if address in backupPingsAddresses: result[address] = backupPingsAddresses[address]
				else: result[address] = ''
		except Exception as exc:
			if address in backupPingsAddresses: result[address] = backupPingsAddresses[address]
			else: result[address] = ''
	executor.shutdown(wait=True)
	return result


# Main logger loop responsible for all logging functions
def log(targetDateTime, previousDirectory, isTimeForNewDirectory):
	global timerThread, globalNumSamples, globalLoggingStartTimestamp, globalNumForksSeen, globalMaxForkLength, globalBitcoinPingTimes, globalIcmpPingTimes
	
	if EnabledTor and not isTorUp():
		startTor()
	if EnabledI2P and not isI2PUp():
		startI2P()
	if EnabledCJDNS and not isCJDNSUp():
		startCJDNS()
	if not isBitcoinUp():
		startBitcoin()
	
	timestamp = datetime.datetime.now()
	timestampSeconds = int(getTimestampEpoch(timestamp) * timePrecision) / timePrecision
	directory = previousDirectory
	try:
		getblockchaininfo = bitcoin('getblockchaininfo', True)

		isLastDirectoryIBD = '_IBD_' in previousDirectory
		if isLastDirectoryIBD != getblockchaininfo['initialblockdownload']:
			isTimeForNewDirectory = True

		if isTimeForNewDirectory:
			# Restart the Bitcoin node to get a new fresh set of peers
			if len(previousDirectory) > 0:
				if isTorUp(): stopTor()
				if isI2PUp(): stopI2P()
				if isCJDNSUp(): stopCJDNS()
				stopBitcoin()
				terminal(f'mv {os.path.join(bitcoinDirectory, "debug.log")} {previousDirectory}')
				finalizeLogDirectory(previousDirectory)
				while not isBitcoinUp():
					startBitcoin()

				# Reset the target datetime to accommodate for the time just spent finalizing the sample
				timestamp = targetDateTime = datetime.datetime.now()
				timestampSeconds = int(getTimestampEpoch(timestamp) * timePrecision) / timePrecision
				getblockchaininfo = bitcoin('getblockchaininfo', True)

			sampleNumber = 1
			compressedDirectoryExists = True
			directoryNumber = 0
			while compressedDirectoryExists:
				directoryNumber += 1
				if getblockchaininfo['initialblockdownload']:
					directory = f'Research_Logs/Bitcoin_IBD_Log_{directoryNumber}'
				else:
					directory = f'Research_Logs/Bitcoin_Log_{directoryNumber}'
				compressedDirectoryExists = os.path.exists(directory + '.tar.xz')

			globalBitcoinPingTimes = {}
			globalIcmpPingTimes = {}

			# If a sample terminates prematurely, then it is still uncompressed.
			# Rather than deleting it (like the code below), we let the sample live and get finalized
			# uncompressedDirectoryExists = os.path.exists(directory)
			# if uncompressedDirectoryExists:
			# 	print(f'Detected an incomplete sample directory: {directory}, removing...')
			# 	terminal('rm -rf ' + directory)
			isTimeForNewDirectory = False

		if not os.path.exists(directory):
			# After the node has restarted and is up and running, create the directory
			print('Creating directory:', directory)
			os.makedirs(directory)
			writeInitialMachineInfo(timestamp, directory)
		
		# Call the Bitcoin Core RPC commands for logging
		getpeerinfo = bitcoin('getpeerinfo', True)
		getpeersmsginfoandclear = bitcoin('getpeersmsginfoandclear', True)
		listnewbroadcastsandclear = bitcoin('listnewbroadcastsandclear', True)
		getchaintips = bitcoin('getchaintips', True)
		getmempoolinfo = bitcoin('getmempoolinfo', True)
		peersToUpdate = {}

		newblockbroadcastsblockinformation = {'hash': '', 'propagation_time': '', 'propagation_time_median_of_peers': '', 'node_received_by': ''}
		if 'new_block_broadcasts' in listnewbroadcastsandclear:
			if 'block_information' in listnewbroadcastsandclear['new_block_broadcasts']:
				newblockbroadcastsblockinformation = listnewbroadcastsandclear['new_block_broadcasts']['block_information']
				if newblockbroadcastsblockinformation['hash'] == '':
					newblockbroadcastsblockinformation['propagation_time'] = ''
					newblockbroadcastsblockinformation['propagation_time_median_of_peers'] = ''
					newblockbroadcastsblockinformation['node_received_by'] = ''
				# Clean up so we can iterate through the peer addresses inside new_block_broadcasts
				del listnewbroadcastsandclear['new_block_broadcasts']['block_information']
			if 'header_information' in listnewbroadcastsandclear['new_block_broadcasts']:
				newheaderbroadcastsblockinformation = listnewbroadcastsandclear['new_block_broadcasts']['header_information']
				if newheaderbroadcastsblockinformation['hash'] == '':
					newheaderbroadcastsblockinformation['propagation_time'] = ''
					newheaderbroadcastsblockinformation['propagation_time_median_of_peers'] = ''
					newheaderbroadcastsblockinformation['node_received_by'] = ''
				# Clean up so we can iterate through the peer addresses inside new_block_broadcasts
				del listnewbroadcastsandclear['new_block_broadcasts']['header_information']
		timestampMedianDifference = ''
		if 'timestamps' in listnewbroadcastsandclear:
			timestampMedianDifference = listnewbroadcastsandclear['timestamps']['timestamp'] - listnewbroadcastsandclear['timestamps']['timestamp_median']

		peersNeedingIcmpPingUpdate = []

		for peerEntry in getpeerinfo:
			address, port = splitAddress(peerEntry['addr'])
			if address not in peersToUpdate:
				peersToUpdate[address] = getPeerInfoTemplate()

			if address in listnewbroadcastsandclear['new_block_broadcasts']: peersToUpdate[address]['newBlocksReceivedCount'] = listnewbroadcastsandclear['new_block_broadcasts'][address]
			if address in listnewbroadcastsandclear['new_transaction_broadcasts']: peersToUpdate[address]['newTransactionsReceivedCount'] = listnewbroadcastsandclear['new_transaction_broadcasts'][address]
			if address in listnewbroadcastsandclear['new_transaction_fee_broadcasts']: peersToUpdate[address]['newTransactionsReceivedFee'] = listnewbroadcastsandclear['new_transaction_fee_broadcasts'][address]
			if address in listnewbroadcastsandclear['new_transaction_size_broadcasts']: peersToUpdate[address]['newTransactionsReceivedSize'] = listnewbroadcastsandclear['new_transaction_size_broadcasts'][address]
			if address in listnewbroadcastsandclear['unique_and_redundant_transaction_broadcasts']: peersToUpdate[address]['redundantTransactionsReceivedCount'] = listnewbroadcastsandclear['unique_and_redundant_transaction_broadcasts'][address]
			if address in listnewbroadcastsandclear['unique_and_redundant_transaction_size_broadcasts']: peersToUpdate[address]['redundantTransactionsReceivedSize'] = listnewbroadcastsandclear['unique_and_redundant_transaction_size_broadcasts'][address]

			# Take the total transaction values, and subtract the unique values to get the redundant transaction values
			if address in listnewbroadcastsandclear['new_transaction_broadcasts'] and address in listnewbroadcastsandclear['unique_and_redundant_transaction_broadcasts']: # Count
				peersToUpdate[address]['redundantTransactionsReceivedCount'] -= peersToUpdate[address]['newTransactionsReceivedCount']
			if address in listnewbroadcastsandclear['new_transaction_size_broadcasts'] and address in listnewbroadcastsandclear['unique_and_redundant_transaction_size_broadcasts']: # Size
				peersToUpdate[address]['redundantTransactionsReceivedSize'] -= peersToUpdate[address]['newTransactionsReceivedSize']


			bytesSentPerMessage = peerEntry['bytessent_per_msg']
			bytesReceivedPerMessage = peerEntry['bytesrecv_per_msg']
			bytesSentPerMessage = dict(sorted(bytesSentPerMessage.items(), key=lambda item: item[1], reverse = True))
			bytesReceivedPerMessage = dict(sorted(bytesReceivedPerMessage.items(), key=lambda item: item[1], reverse = True))

			# Self-extracted out of Bitcoin Core using this custom network logger instance
			peersToUpdate[address]['banscore'] = peerEntry['banscore']
			peersToUpdate[address]['fChance'] = peerEntry['fchance']
			peersToUpdate[address]['isTerrible'] = peerEntry['isterrible'].replace('true', '1').replace('false', '0')

			peersToUpdate[address]['port'] = int(port)
			peersToUpdate[address]['connectionID'] = int(peerEntry['id'])
			peersToUpdate[address]['connectionDuration'] = int((timestampSeconds - peerEntry['conntime']) * timePrecision) / timePrecision
			peersToUpdate[address]['secondsOffset'] = peerEntry['timeoffset']
			if 'pingtime' in peerEntry: peersToUpdate[address]['bitcoinPingRoundTripTime'] = peerEntry['pingtime'] * 1000

			# ICMP Ping Handler: Update alongside every Bitcoin PING update
			if peerEntry['network'] == 'ipv4' or peerEntry['network'] == 'ipv6':
				if address not in globalBitcoinPingTimes:
					globalBitcoinPingTimes[address] = ''
				if address not in globalIcmpPingTimes:
					globalIcmpPingTimes[address] = ''

				if globalBitcoinPingTimes[address] != peersToUpdate[address]['bitcoinPingRoundTripTime']:
					peersNeedingIcmpPingUpdate.append(address)
					globalBitcoinPingTimes[address] = peersToUpdate[address]['bitcoinPingRoundTripTime']
				else:
					peersToUpdate[address]['icmpPingRoundTripTime'] = globalIcmpPingTimes[address]

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
			peersToUpdate[address]['bytesReceived'] = peerEntry['bytesrecv']
			peersToUpdate[address]['bytesSentDistribution'] = '"' + json.dumps(bytesSentPerMessage, separators=(',', ':')).replace('"', "'") + '"'
			peersToUpdate[address]['bytesReceivedDistribution'] = '"' + json.dumps(bytesReceivedPerMessage, separators=(',', ':')).replace('"', "'") + '"'
			peersToUpdate[address]['lastReceiveTime'] = peerEntry['lastrecv'] if peerEntry['lastrecv'] != 0 else ''
			peersToUpdate[address]['lastTransactionTime'] = peerEntry['last_transaction'] if peerEntry['last_transaction'] != 0 else ''
			peersToUpdate[address]['lastBlockTime'] = peerEntry['last_block'] if peerEntry['last_block'] != 0 else ''
			peersToUpdate[address]['startingBlockHeight'] = peerEntry['startingheight']
			peersToUpdate[address]['currentBlockHeightInCommon'] = peerEntry['synced_blocks']
			peersToUpdate[address]['currentHeaderHeightInCommon'] = peerEntry['synced_headers']

			clocksPerSecond = int(getpeersmsginfoandclear['CLOCKS PER SECOND'])
			if address in getpeersmsginfoandclear:
				for msg in getpeersmsginfoandclear[address].keys():
					if msg == 'list_of_undocumented_messages':
						peersToUpdate[address][f'Undocumented_Messages'] = getpeersmsginfoandclear[address][msg]
					else:
						count, size, sizeMax, time, timeMax = parseGetMsgInfoMessage(getpeersmsginfoandclear[address][msg], clocksPerSecond)
						peersToUpdate[address][f'New_{msg}s_Received (count)'] = count
						peersToUpdate[address][f'Size_{msg} (bytes)'] = size
						peersToUpdate[address][f'MaxSize_{msg} (bytes)'] = sizeMax
						peersToUpdate[address][f'Time_{msg} (milliseconds)'] = time
						peersToUpdate[address][f'MaxTime_{msg} (milliseconds)'] = timeMax

		# Send ICMP pings in a separate set of threads
		icmpPingExecutor, icmpPingFutureDict = sendIcmpPings(peersNeedingIcmpPingUpdate)

		# If a peer connected then disconnected in between the sample duration, we still want to log it
		for address in listnewbroadcastsandclear['new_block_broadcasts']:
			if address in peersToUpdate: continue
			peersToUpdate[address] = getPeerInfoTemplate()
			print('Logging incomplete block propagation entry for disconnected peer:', address)
			peersToUpdate[address]['newBlocksReceivedCount'] = listnewbroadcastsandclear['new_block_broadcasts'][address]
		for address in listnewbroadcastsandclear['new_transaction_broadcasts']:
			if address in peersToUpdate: continue
			peersToUpdate[address] = getPeerInfoTemplate()
			print('Logging incomplete block propagation entry for disconnected peer:', address)
			peersToUpdate[address]['newTransactionsReceivedCount'] = listnewbroadcastsandclear['new_transaction_broadcasts'][address]
			if address in listnewbroadcastsandclear['new_transaction_fee_broadcasts']: peersToUpdate[address]['newTransactionsReceivedFee'] = listnewbroadcastsandclear['new_transaction_fee_broadcasts'][address]
			if address in listnewbroadcastsandclear['new_transaction_size_broadcasts']: peersToUpdate[address]['newTransactionsReceivedSize'] = listnewbroadcastsandclear['new_transaction_size_broadcasts'][address]

		sampleNumber = logMachineState(timestamp, directory, getpeerinfo, getblockchaininfo, getmempoolinfo, newblockbroadcastsblockinformation, newheaderbroadcastsblockinformation, timestampMedianDifference)
		print(f'Adding Sample #{sampleNumber} to {directory}:')
		
		maybeLogBlockState(timestamp, directory, getblockchaininfo, getchaintips, newblockbroadcastsblockinformation, newheaderbroadcastsblockinformation)
		if (sampleNumber - 1) % numSamplesPerAddressManagerBucketLog == 0:
			logAddressManagerBucketInfo(timestamp, directory)

		# Resolve ICMP pings, and apply the results to the log data
		icmpPingResults = resolveIcmpPings(icmpPingExecutor, icmpPingFutureDict, globalIcmpPingTimes)
		for address in icmpPingResults:
			globalIcmpPingTimes[address] = icmpPingResults[address]
			peersToUpdate[address]['icmpPingRoundTripTime'] = globalIcmpPingTimes[address]

		for address in peersToUpdate:
			logNode(address, timestamp, directory, peersToUpdate[address])


		globalNumSamples += 1
		totalNumDays = int((timestamp - globalLoggingStartTimestamp).total_seconds() / (60 * 60 * 24) * timePrecision) / timePrecision
		print(f'	Sample successfully logged. Total of {globalNumSamples} samples to date, logging interval: {totalNumDays} days. Total of {globalNumForksSeen} forks with a max length of {globalMaxForkLength} blocks.')
		isTimeForNewDirectory = (sampleNumber >= numSamplesPerDirectory)

	except Exception as e:
		errorMessage = str(e)
		errorTraceback = traceback.format_exc()
		errorFilePath = os.path.join(directory, 'errors.csv')
		if not os.path.exists(errorFilePath):
			file = open(errorFilePath, 'w')
			header = 'Timestamp,'
			header += 'Timestamp (UNIX epoch),'
			header += 'Error Message,'
			header += 'Error Traceback,'
			file.write(header + '\n')
		else:
			file = open(errorFilePath, 'a')
		line = '"' + getHumanReadableDateTime(timestamp) + '",'
		line += str(timestampSeconds) + ','
		line += '"' + str(errorMessage.replace('"', "'")) + '",'
		line += '"' + str(errorTraceback.replace('"', "'")) + '",'
		file.write(line + '\n')
		file.close()
		logging.error(f'Error: {errorMessage}\n{errorTraceback}, logged to {errorFilePath}.')

	# Compute the time until the next sample will run, then schedule the run
	targetDateTime += datetime.timedelta(seconds = numSecondsPerSample)
	offset = (targetDateTime - datetime.datetime.now()).total_seconds()
	timerThread = Timer(offset, log, [targetDateTime, directory, isTimeForNewDirectory])
	timerThread.daemon = True
	timerThread.start()

if __name__ == '__main__':
	main()