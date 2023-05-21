from threading import Timer
import datetime
import json
import os
import platform
import psutil
import re
import subprocess
import sys
import time

numSecondsPerSample = 60
directory = 'IndividualPeerInfoLog'

# Send a command to the linux terminal
def terminal(cmd):
	return os.popen(cmd).read()

# Send a command to the Bitcoin console
def bitcoin(cmd):
	return terminal('./src/bitcoin-cli -rpcuser=cybersec -rpcpassword=kZIdeN4HjZ3fp9Lge4iezt0eJrbjSi8kuSuOHeUkEUbQVdf09JZXAAGwF3R5R2qQkPgoLloW91yTFuufo7CYxM2VPT7A5lYeTrodcLWWzMMwIrOKu7ZNiwkrKOQ95KGW8kIuL1slRVFXoFpGsXXTIA55V3iUYLckn8rj8MZHBpmdGQjLxakotkj83ZlSRx1aOJ4BFxdvDNz0WHk1i2OPgXL4nsd56Ph991eKNbXVJHtzqCXUbtDELVf4shFJXame -rpcport=8332 ' + str(cmd))

# Start Bitcoin Core
def startBitcoin():
	subprocess.Popen(['gnome-terminal -t "Custom Bitcoin Core Instance" -- bash ./run.sh'], shell=True)
	rpcReady = False
	while rpcReady is False:
		time.sleep(1)
		try:
			blockHeight = int(bitcoin('getblockcount'))
			rpcReady = True
		except: pass
	print('Bitcoin is up and ready to go')

# Check if the Bitcoin Core instance is up
def bitcoinUp():
	return winexists('Custom Bitcoin Core Instance')

# Check if a window exists
def winexists(target):
	for line in subprocess.check_output(['wmctrl', '-l']).splitlines():
		window_name = line.split(None, 3)[-1].decode()
		if window_name == target:
			return True
	return False

# Return the header for the CSV file
def makeHeader():
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
	line += 'Aggregate of New Unique Transaction Fees (satoshis),'
	line += 'Aggregate of New Unique Transaction Sizes (bytes),'
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
	line += 'Minimum Accepted Transaction Fee,'
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

# Generate the machine state 
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

# Log the state of the machine to file, returns the sample number
def logMachineState(timestamp):
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


# Given a combined address and port, return the individual address and port 
def splitAddress(address):
	split = address.split(':')
	port = split.pop()
	address = ':'.join(split)
	return address, port

def logNode(address, timestamp, updateInfo):
	filePath = os.path.join(directory, re.sub('[^A-Za-z0-9\.]', '-', address)) + '.csv'
	if not os.path.exists(filePath):
		# Create a new file
		prevLine = ''
		numPrevLines = 1
		print(f'    Logging {address} ({numPrevLines} sample)')
		file = open(filePath, 'w')
		file.write(makeHeader() + '\n')
	else:
		# Read the last line from the file
		with open(filePath, 'r') as f:
			prevLines = f.readlines()
			# Don't let prevLine contain the header; data only
			if len(prevLines) > 1: prevLine = prevLines[-1].split(',')
			else: prevLine = ''
			numPrevLines = len(prevLines)
		print(f'    Logging {address} ({numPrevLines} samples)')

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

def log(targetDateTime):
	global t
	if not bitcoinUp(): startBitcoin()
	timestamp = datetime.datetime.now()
	getpeersmsginfoandclear = json.loads(bitcoin('getpeersmsginfoandclear'))
	listnewbroadcastsandclear = json.loads(bitcoin('listnewbroadcastsandclear'))
	getpeerinfo = json.loads(bitcoin('getpeerinfo'))
	peersToUpdate = {}

	for peerEntry in getpeerinfo:
		address, port = splitAddress(peerEntry['addr'])
		if address not in peersToUpdate:
			peersToUpdate[address] = {
				# Start of listnewbroadcastsandclear
				'newBlocksReceivedCount': '',
				'newTransactionsReceivedCount': '',
				'newTransactionsReceivedFee': '',
				'newTransactionsReceivedSize': '',
				# End of listnewbroadcastsandclear
				# Start of getpeerinfo
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
				'New_ADDRs_Received (count)': '',
				'Size_ADDR (bytes)': '',
				'MaxSize_ADDR (bytes)': '',
				'Time_ADDR (milliseconds)': '',
				'MaxTime_ADDR (milliseconds)': '',
				'New_ADDRV2s_Received (count)': '',
				'Size_ADDRV2 (bytes)': '',
				'MaxSize_ADDRV2 (bytes)': '',
				'Time_ADDRV2 (milliseconds)': '',
				'MaxTime_ADDRV2 (milliseconds)': '',
				'New_BLOCKs_Received (count)': '',
				'Size_BLOCK (bytes)': '',
				'MaxSize_BLOCK (bytes)': '',
				'Time_BLOCK (milliseconds)': '',
				'MaxTime_BLOCK (milliseconds)': '',
				'New_BLOCKTXNs_Received (count)': '',
				'Size_BLOCKTXN (bytes)': '',
				'MaxSize_BLOCKTXN (bytes)': '',
				'Time_BLOCKTXN (milliseconds)': '',
				'MaxTime_BLOCKTXN (milliseconds)': '',
				'New_CFCHECKPTs_Received (count)': '',
				'Size_CFCHECKPT (bytes)': '',
				'MaxSize_CFCHECKPT (bytes)': '',
				'Time_CFCHECKPT (milliseconds)': '',
				'MaxTime_CFCHECKPT (milliseconds)': '',
				'New_CFHEADERSs_Received (count)': '',
				'Size_CFHEADERS (bytes)': '',
				'MaxSize_CFHEADERS (bytes)': '',
				'Time_CFHEADERS (milliseconds)': '',
				'MaxTime_CFHEADERS (milliseconds)': '',
				'New_CFILTERs_Received (count)': '',
				'Size_CFILTER (bytes)': '',
				'MaxSize_CFILTER (bytes)': '',
				'Time_CFILTER (milliseconds)': '',
				'MaxTime_CFILTER (milliseconds)': '',
				'New_CMPCTBLOCKs_Received (count)': '',
				'Size_CMPCTBLOCK (bytes)': '',
				'MaxSize_CMPCTBLOCK (bytes)': '',
				'Time_CMPCTBLOCK (milliseconds)': '',
				'MaxTime_CMPCTBLOCK (milliseconds)': '',
				'New_FEEFILTERs_Received (count)': '',
				'Size_FEEFILTER (bytes)': '',
				'MaxSize_FEEFILTER (bytes)': '',
				'Time_FEEFILTER (milliseconds)': '',
				'MaxTime_FEEFILTER (milliseconds)': '',
				'New_FILTERADDs_Received (count)': '',
				'Size_FILTERADD (bytes)': '',
				'MaxSize_FILTERADD (bytes)': '',
				'Time_FILTERADD (milliseconds)': '',
				'MaxTime_FILTERADD (milliseconds)': '',
				'New_FILTERCLEARs_Received (count)': '',
				'Size_FILTERCLEAR (bytes)': '',
				'MaxSize_FILTERCLEAR (bytes)': '',
				'Time_FILTERCLEAR (milliseconds)': '',
				'MaxTime_FILTERCLEAR (milliseconds)': '',
				'New_FILTERLOADs_Received (count)': '',
				'Size_FILTERLOAD (bytes)': '',
				'MaxSize_FILTERLOAD (bytes)': '',
				'Time_FILTERLOAD (milliseconds)': '',
				'MaxTime_FILTERLOAD (milliseconds)': '',
				'New_GETADDRs_Received (count)': '',
				'Size_GETADDR (bytes)': '',
				'MaxSize_GETADDR (bytes)': '',
				'Time_GETADDR (milliseconds)': '',
				'MaxTime_GETADDR (milliseconds)': '',
				'New_GETBLOCKSs_Received (count)': '',
				'Size_GETBLOCKS (bytes)': '',
				'MaxSize_GETBLOCKS (bytes)': '',
				'Time_GETBLOCKS (milliseconds)': '',
				'MaxTime_GETBLOCKS (milliseconds)': '',
				'New_GETBLOCKTXNs_Received (count)': '',
				'Size_GETBLOCKTXN (bytes)': '',
				'MaxSize_GETBLOCKTXN (bytes)': '',
				'Time_GETBLOCKTXN (milliseconds)': '',
				'MaxTime_GETBLOCKTXN (milliseconds)': '',
				'New_GETCFCHECKPTs_Received (count)': '',
				'Size_GETCFCHECKPT (bytes)': '',
				'MaxSize_GETCFCHECKPT (bytes)': '',
				'Time_GETCFCHECKPT (milliseconds)': '',
				'MaxTime_GETCFCHECKPT (milliseconds)': '',
				'New_GETCFHEADERSs_Received (count)': '',
				'Size_GETCFHEADERS (bytes)': '',
				'MaxSize_GETCFHEADERS (bytes)': '',
				'Time_GETCFHEADERS (milliseconds)': '',
				'MaxTime_GETCFHEADERS (milliseconds)': '',
				'New_GETCFILTERSs_Received (count)': '',
				'Size_GETCFILTERS (bytes)': '',
				'MaxSize_GETCFILTERS (bytes)': '',
				'Time_GETCFILTERS (milliseconds)': '',
				'MaxTime_GETCFILTERS (milliseconds)': '',
				'New_GETDATAs_Received (count)': '',
				'Size_GETDATA (bytes)': '',
				'MaxSize_GETDATA (bytes)': '',
				'Time_GETDATA (milliseconds)': '',
				'MaxTime_GETDATA (milliseconds)': '',
				'New_GETHEADERSs_Received (count)': '',
				'Size_GETHEADERS (bytes)': '',
				'MaxSize_GETHEADERS (bytes)': '',
				'Time_GETHEADERS (milliseconds)': '',
				'MaxTime_GETHEADERS (milliseconds)': '',
				'New_HEADERSs_Received (count)': '',
				'Size_HEADERS (bytes)': '',
				'MaxSize_HEADERS (bytes)': '',
				'Time_HEADERS (milliseconds)': '',
				'MaxTime_HEADERS (milliseconds)': '',
				'New_INVs_Received (count)': '',
				'Size_INV (bytes)': '',
				'MaxSize_INV (bytes)': '',
				'Time_INV (milliseconds)': '',
				'MaxTime_INV (milliseconds)': '',
				'New_MEMPOOLs_Received (count)': '',
				'Size_MEMPOOL (bytes)': '',
				'MaxSize_MEMPOOL (bytes)': '',
				'Time_MEMPOOL (milliseconds)': '',
				'MaxTime_MEMPOOL (milliseconds)': '',
				'New_MERKLEBLOCKs_Received (count)': '',
				'Size_MERKLEBLOCK (bytes)': '',
				'MaxSize_MERKLEBLOCK (bytes)': '',
				'Time_MERKLEBLOCK (milliseconds)': '',
				'MaxTime_MERKLEBLOCK (milliseconds)': '',
				'New_NOTFOUNDs_Received (count)': '',
				'Size_NOTFOUND (bytes)': '',
				'MaxSize_NOTFOUND (bytes)': '',
				'Time_NOTFOUND (milliseconds)': '',
				'MaxTime_NOTFOUND (milliseconds)': '',
				'New_PINGs_Received (count)': '',
				'Size_PING (bytes)': '',
				'MaxSize_PING (bytes)': '',
				'Time_PING (milliseconds)': '',
				'MaxTime_PING (milliseconds)': '',
				'New_PONGs_Received (count)': '',
				'Size_PONG (bytes)': '',
				'MaxSize_PONG (bytes)': '',
				'Time_PONG (milliseconds)': '',
				'MaxTime_PONG (milliseconds)': '',
				'New_REJECTs_Received (count)': '',
				'Size_REJECT (bytes)': '',
				'MaxSize_REJECT (bytes)': '',
				'Time_REJECT (milliseconds)': '',
				'MaxTime_REJECT (milliseconds)': '',
				'New_SENDADDRV2s_Received (count)': '',
				'Size_SENDADDRV2 (bytes)': '',
				'MaxSize_SENDADDRV2 (bytes)': '',
				'Time_SENDADDRV2 (milliseconds)': '',
				'MaxTime_SENDADDRV2 (milliseconds)': '',
				'New_SENDCMPCTs_Received (count)': '',
				'Size_SENDCMPCT (bytes)': '',
				'MaxSize_SENDCMPCT (bytes)': '',
				'Time_SENDCMPCT (milliseconds)': '',
				'MaxTime_SENDCMPCT (milliseconds)': '',
				'New_SENDHEADERSs_Received (count)': '',
				'Size_SENDHEADERS (bytes)': '',
				'MaxSize_SENDHEADERS (bytes)': '',
				'Time_SENDHEADERS (milliseconds)': '',
				'MaxTime_SENDHEADERS (milliseconds)': '',
				'New_SENDTXRCNCLs_Received (count)': '',
				'Size_SENDTXRCNCL (bytes)': '',
				'MaxSize_SENDTXRCNCL (bytes)': '',
				'Time_SENDTXRCNCL (milliseconds)': '',
				'MaxTime_SENDTXRCNCL (milliseconds)': '',
				'New_TXs_Received (count)': '',
				'Size_TX (bytes)': '',
				'MaxSize_TX (bytes)': '',
				'Time_TX (milliseconds)': '',
				'MaxTime_TX (milliseconds)': '',
				'New_VERACKs_Received (count)': '',
				'Size_VERACK (bytes)': '',
				'MaxSize_VERACK (bytes)': '',
				'Time_VERACK (milliseconds)': '',
				'MaxTime_VERACK (milliseconds)': '',
				'New_VERSIONs_Received (count)': '',
				'Size_VERSION (bytes)': '',
				'MaxSize_VERSION (bytes)': '',
				'Time_VERSION (milliseconds)': '',
				'MaxTime_VERSION (milliseconds)': '',
				'New_WTXIDRELAYs_Received (count)': '',
				'Size_WTXIDRELAY (bytes)': '',
				'MaxSize_WTXIDRELAY (bytes)': '',
				'Time_WTXIDRELAY (milliseconds)': '',
				'MaxTime_WTXIDRELAY (milliseconds)': '',
				'New_[UNDOCUMENTED]s_Received (count)': '',
				'Size_[UNDOCUMENTED] (bytes)': '',
				'MaxSize_[UNDOCUMENTED] (bytes)': '',
				'Time_[UNDOCUMENTED] (milliseconds)': '',
				'MaxTime_[UNDOCUMENTED] (milliseconds)': '',
				# End of getpeersmsginfoandclear
			}



		if address in listnewbroadcastsandclear['new_block_broadcasts']: peersToUpdate[address]['newBlocksReceivedCount'] = listnewbroadcastsandclear['new_block_broadcasts'][address]
		if address in listnewbroadcastsandclear['new_transaction_broadcasts']: peersToUpdate[address]['newTransactionsReceivedCount'] = listnewbroadcastsandclear['new_transaction_broadcasts'][address]
		if address in listnewbroadcastsandclear['new_transaction_fee_broadcasts']: peersToUpdate[address]['newTransactionsReceivedFee'] = listnewbroadcastsandclear['new_transaction_fee_broadcasts'][address]
		if address in listnewbroadcastsandclear['new_transaction_size_broadcasts']: peersToUpdate[address]['newTransactionsReceivedSize'] = listnewbroadcastsandclear['new_transaction_size_broadcasts'][address]

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
		peersToUpdate[address]['bytesSentDistribution'] = '"' + json.dumps(peerEntry['bytessent_per_msg'], separators=(',', ':')).replace('"', "'") + '"'
		peersToUpdate[address]['lastReceiveTime'] = peerEntry['lastrecv'] if peerEntry['lastrecv'] != 0 else ''
		peersToUpdate[address]['bytesReceived'] = peerEntry['bytesrecv']
		peersToUpdate[address]['bytesReceivedDistribution'] = '"' + json.dumps(peerEntry['bytesrecv_per_msg'], separators=(',', ':')).replace('"', "'") + '"'
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

	sampleNumber = logMachineState(timestamp)
	print(f'Adding Sample #{sampleNumber}:')

	for address in peersToUpdate:
		logNode(address, timestamp, peersToUpdate[address])
	print(f'    Sample successfully logged.')
	

	targetDateTime += datetime.timedelta(seconds = numSecondsPerSample)
	offset = (targetDateTime - datetime.datetime.now()).total_seconds()
	t = Timer(offset, log, [targetDateTime])
	t.daemon = True
	t.start()


if not bitcoinUp(): startBitcoin()

if not os.path.exists(directory):
	print('Creating directory:', directory)
	os.makedirs(directory)

targetDateTime = datetime.datetime.now()
log(targetDateTime)

while True:
	try:
		time.sleep(3600) # Every hour
	except KeyboardInterrupt as e:
		print(e)
		t.cancel()
		break

print('Logger terminated by user. Have a nice day!')