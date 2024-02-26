import os
import dns.resolver

def main():
	# Define the DNS seeds
	dns_seeds = [
		'seed.bitcoin.sipa.be', # Pieter Wuille, only supports x1, x5, x9, and xd
		'dnsseed.bluematt.me', # Matt Corallo, only supports x9
		'dnsseed.bitcoin.dashjr.org', # Luke Dashjr
		'seed.bitcoinstats.com', # Christian Decker, supports x1 - xf
		'seed.bitcoin.jonasschnelli.ch', # Jonas Schnelli, only supports x1, x5, x9, and xd
		'seed.btc.petertodd.net', # Peter Todd, only supports x1, x5, x9, and xd
		'seed.bitcoin.sprovoost.nl', # Sjors Provoost
		'dnsseed.emzy.de', # Stephan Oeste
		'seed.bitcoin.wiz.biz' # Jason Maurice
	]

	# Create directory for DNS Seed Results if it doesn't exist
	dir_path = 'Bitcoin_DNS_Seed_Results'
	os.makedirs(dir_path, exist_ok=True)

	# Process each DNS seed
	for seed in dns_seeds:
		print('Querying seed:', seed)
		results = query_dns_seed_detailed(seed)
		file_path = os.path.join(dir_path, f'{seed}.txt')
		with open(file_path, 'w') as f:
			for line in results:
				f.write(line + '\n')

# Query each DNS seed
def query_dns_seed_detailed(seed_hostname):
	result = []
	resolver = dns.resolver.Resolver()
	#resolver.nameservers = ['8.8.8.8']  # Using Google's DNS
	resolver.nameservers = ['1.1.1.1']  # Using Cloudflare's DNS

	resolver.timeout = 10  # Increase timeout to 10 seconds
	resolver.lifetime = 10  # Set the total query lifetime to 10 seconds

	# Query for A records (IPv4)
	try:
		answers_ipv4 = resolver.resolve(seed_hostname, 'A')
		for rdata in answers_ipv4:
			result.append(str(rdata))
	except dns.resolver.NoAnswer:
		result.append('No IPv4 addresses found.')

	# Query for AAAA records (IPv6)
	try:
		answers_ipv6 = resolver.resolve(seed_hostname, 'AAAA')
		for rdata in answers_ipv6:
			result.append(str(rdata))
	except dns.resolver.NoAnswer:
		result.append('No IPv6 addresses found.')
	
	return result

if __name__ == '__main__':
	main()