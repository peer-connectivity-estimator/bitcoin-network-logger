import os
import re
import sys
import csv

numSecondsPerSample = 1
directory = 'IndividualPeerInfoLog'

# List the files with a regular expression
def listFiles(regex, directory = ''):
	path = os.path.join(os.curdir, directory)
	return [os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and bool(re.match(regex, file))]

filePaths = listFiles(r'^[^_]+\.csv', directory)
address_data = {}

for filePath in filePaths:
	file = open(filePath, 'r')
	reader = csv.reader(file)
	for row in reader:
		timestamp_str = row[0]
		timestamp_id = row[1]
		timestamp_diff = row[1]
		address = row[3]
		new_blocks = row[8]
		new_tx = row[9]
		new_tx_fees = row[10]
		new_tx_bytes = row[11]

		score = new_blocks + new_tx_fees

		if address not in address_data:
			address_data[address] = []

		address_data[address].append([timestamp_id, score])
	file.close()

addresses = address_data.keys()
address_index = [0] * len(addresses)

for address in addresses:


print('Done. Have a nice day!')