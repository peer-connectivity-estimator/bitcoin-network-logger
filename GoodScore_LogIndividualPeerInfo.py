import os
import re
import sys
import csv

numSecondsPerSample = 1
directory = 'IndividualPeerInfoLog'

# Compute the score
def computeScore(b, t, wb = 0.5, wt = 0.5):
	return (new_blocks * wb + new_tx_fees * wt)

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

		score = computeScore(new_blocks, new_tx_fees)

		if timestamp_id not in data:
			data[timestamp_id] = {}

		data[timestamp_id][address] = score
	file.close()

data = dict(sorted(data.items()))

outputFileName = 'IndividualPeerGoodScore.csv'
outputFile = open(outputFileName, 'w')
line += 'Timestamp (UNIX epoch),'
for address in addresses:
	line += f'{address} Score,'
outputFile.write(line + '\n')

for timestamp in data:
	print(f'Processing timestamp {timestamp}...')
	line = timestamp
	for address in addresses:
		if address in data[timestamp]:
			line += str(data[timestamp][address]) + ','
		else:
			line += ','
	outputFile.write(line + '\n')

print('Done! That was fast. Have a nice day!')