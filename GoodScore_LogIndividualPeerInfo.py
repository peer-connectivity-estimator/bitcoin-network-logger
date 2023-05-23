import os
import re
import sys
import csv

numSecondsPerSample = 1
directory = 'IndividualPeerInfoLog'

decayRate = 0.999

# Compute the score
def computeScore(b, t, wb = 1, wt = 1/9333/2):
	return (new_blocks * wb + new_tx_fees * wt)

# List the files with a regular expression
def listFiles(regex, directory = ''):
	path = os.path.join(os.curdir, directory)
	return [os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and bool(re.match(regex, file))]

filePaths = listFiles(r'^[^_]+\.csv', directory)
data = {}
addresses = {}

for filePath in filePaths:
	file = open(filePath, 'r')
	reader = csv.reader(file)
	header = next(reader)
	for row in reader:
		timestamp_str = row[0]
		timestamp_id = row[1]
		timestamp_diff = row[1]
		address = row[3]
		new_blocks = int(row[8])
		new_tx = int(row[9])
		new_tx_fees = int(row[10])
		new_tx_bytes = int(row[11])

		score = computeScore(new_blocks, new_tx_fees)

		if timestamp_id not in data:
			data[timestamp_id] = {}

		data[timestamp_id][address] = score
		if address not in addresses:
			addresses[address] = score
		else:
			addresses[address] = max(addresses[address], score)

	file.close()

data = dict(sorted(data.items()))
addresses = dict(sorted(addresses.items(), key=lambda item: item[1], reverse=True))

outputFileName = 'GoodScoreIndividualPeerInfo.csv'
outputFile = open(outputFileName, 'w')
line = 'Timestamp (UNIX epoch),'
for address in addresses:
	line += f'{address} Score,'
outputFile.write(line + '\n')

score = {}
for address in addresses:
	score[address] = 0

for timestamp in data:
	print(f'Processing timestamp {timestamp}...')
	line = timestamp + ','
	for address in addresses:
		if address in data[timestamp]:
			score[address] *= decayRate
			score[address] += data[timestamp][address]
		line += str(score[address]) + ','
	outputFile.write(line + '\n')

print('Done! That was fast. Have a nice day!')