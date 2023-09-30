
import os
import re
import sys
import subprocess

# Main program
def main():
	deleteOriginal = input('Would you like to remove the original directory after completion? (y/n): ').lower() in ['y', 'yes']
	directory = selectDir(r'Research_Logs/Bitcoin_Log_[0-9]+', False, 'Research_Logs')
	finalizeLogDirectory(directory, deleteOriginal)

# Send a command to the Linux terminal
def terminal(cmd):
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	stdout, _ = process.communicate()
	return stdout.decode('utf-8')

# Given a regular expression, list the directories that match it, and ask for user input
def selectDir(regex, subdirs = False, startDirectory = '.'):
	dirs = []
	if subdirs:
		for (dirpath, dirnames, filenames) in os.walk(startDirectory):
			if dirpath[:2] in ['./', '.\\']: dirpath = dirpath[2:]
			if bool(re.match(regex, dirpath)):
				dirs.append(dirpath)
	else:
		for obj in os.listdir(startDirectory):
			obj = os.path.join(startDirectory, obj)
			print(obj, os.path.isdir(obj), bool(re.match(regex, obj)))
			if os.path.isdir(obj) and bool(re.match(regex, obj)):
				dirs.append(obj)

	print()
	if len(dirs) == 0:
		print(f'No directories were found that match "{regex}"')
		print()
		return ''

	print('List of directories:')
	for i, directory in enumerate(dirs):
		print(f'  Directory {i + 1}  -  {directory}')
	print()

	selection = None
	while selection is None:
		try:
			i = int(input(f'Please select a directory (1 to {len(dirs)}): '))
		except KeyboardInterrupt:
			sys.exit()
		except:
			pass
		if i > 0 and i <= len(dirs):
			selection = dirs[i - 1]
	print()
	return selection

# When a directory is finalized, we can zip it up with maximum compression, and remove the original
def finalizeLogDirectory(directory, deleteOriginal):
	global outputFilesToTransferPath, outputFilesToTransfer
	print(f'Finalizing {directory}...')
	outputFilePath = directory + '.tar.xz'
	try:
		contents = ' '.join(os.listdir(directory))
		terminal(f'tar -C "{directory}" -cf - {contents} | xz -9e - > "{outputFilePath}"')
	except:
		terminal(f'tar cf - "{directory}" | xz -9e - > "{outputFilePath}"') # Also compresses the directory
	if deleteOriginal and os.path.exists(outputFilePath):
		if os.path.getsize(outputFilePath) > 0:
			terminal(f'rm -rf "{directory}"')
		else:
			print(f'\tFailed to compress {directory}, keeping original directory')
			terminal(f'rm -rf "{outputFilePath}"')
			outputFilePath = directory
	else:
		outputFilePath = directory

if __name__ == '__main__':
	main()