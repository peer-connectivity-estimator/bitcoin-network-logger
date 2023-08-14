from bitcoin.core import CBlock
from bitcoin.core import x
from bitcoin.messages import msg_block
from bitcoin.messages import msg_version, msg_verack
from bitcoin.net import CAddress
from getpass import getpass
import argparse
import json
import os
import random
import requests
import socket
import time
import re


datadir = '' # Virtual machine shared folder

# Main logger node path
if os.path.exists(f'/home/{os.getlogin()}/BitcoinFullLedger/blocks'):
    datadir = f' -datadir=/home/{os.getlogin()}/BitcoinFullLedger'

elif os.path.exists('/media/sf_Bitcoin/blocks'):
    datadir = ' -datadir=/media/sf_Bitcoin' # Virtual machine shared folder
elif os.path.exists('/media/sf_BitcoinVictim/blocks'):
    datadir = ' -datadir=/media/sf_BitcoinVictim'
elif os.path.exists('/media/sf_BitcoinAttacker/blocks'):
    datadir = ' -datadir=/media/sf_BitcoinAttacker'
elif os.path.exists(f'/media/{os.getlogin()}/BITCOIN/blocks'):
    datadir = f' -datadir=/media/{os.getlogin()}/BITCOIN'
elif os.path.exists(f'/media/{os.getlogin()}/Blockchains/Bitcoin/blocks'):
    datadir = f' -datadir=/media/{os.getlogin()}/Blockchains/Bitcoin'
elif os.path.exists(f'/media/{os.getlogin()}/Long Term Storage/Bitcoin/blocks'):
    datadir = f' -datadir=/media/{os.getlogin()}/Long Term Storage/Bitcoin'


rpc_username = 'cybersec'
rpc_password = 'kZIdeN4HjZ3fp9Lge4iezt0eJrbjSi8kuSuOHeUkEUbQVdf09JZXAAGwF3R5R2qQkPgoLloW91yTFuufo7CYxM2VPT7A5lYeTrodcLWWzMMwIrOKu7ZNiwkrKOQ95KGW8kIuL1slRVFXoFpGsXXTIA55V3iUYLckn8rj8MZHBpmdGQjLxakotkj83ZlSRx1aOJ4BFxdvDNz0WHk1i2OPgXL4nsd56Ph991eKNbXVJHtzqCXUbtDELVf4shFJXame'

bitcoin_protocolversion = 70015
bitcoin_subversion = "/Satoshi:0.21.1/"


def bitcoin(cmd):
    return os.popen(f'src/bitcoin-cli {datadir} {cmd}').read()


def get_block(block_height):
    block_hash = bitcoin(f'getblockhash {block_height}').strip()

    if not block_hash:
        print("Error: Block hash not found.")
        return None

    block_data = ''
    block_chunk = bitcoin(f'getblock {block_hash} 0')
    while block_chunk:
        print('Got block chunk of size', len(block_chunk))
        block_data += block_chunk
        block_header = re.search(r'"nextblockhash"\s*:\s*"(?P<next_block_hash>[^"]+)"', block_chunk)
        if block_header:
            next_block_hash = block_header.group('next_block_hash')
            block_chunk = bitcoin(f'getblock {next_block_hash} 0')
        else:
            break

    block_data = re.sub('[^a-fA-F0-9]', '', block_data)

    if len(block_data) % 2 != 0:
        block_data = '0' + block_data

    return block_data




# def get_block(my_node_url, block_height):
#     headers = {'content-type': 'application/json'}
#     payload = {
#         'method': 'getblockhash',
#         'params': [block_height],
#         'jsonrpc': '2.0',
#         'id': 0,
#     }
    
#     response = requests.post(
#         my_node_url, 
#         auth=(rpc_username, rpc_password),
#         headers=headers,
#         data=json.dumps(payload),
#     )

#     block_hash = response.json()['result']
#     payload['method'] = 'getblock'
#     payload['params'] = [block_hash]

#     response = requests.post(
#         my_node_url, 
#         auth=(rpc_username, rpc_password),
#         headers=headers,
#         data=json.dumps(payload),
#     )

#     return response.json()['result']

def version_packet(src_ip, dst_ip, src_port, dst_port):
    msg = msg_version()
    msg.nVersion = bitcoin_protocolversion
    msg.addrFrom = CAddress()
    msg.addrFrom.ip = src_ip
    msg.addrFrom.port = src_port
    msg.addrTo = CAddress()
    msg.addrTo.ip = dst_ip
    msg.addrTo.port = dst_port
    msg.strSubVer = bitcoin_subversion.encode()
    return msg

def establish_connection(my_node_ip, target_node_ip, block_height):
    src_port = random.randint(1024, 65535)
    dst_port = 8333  # Default Bitcoin port

    print("Creating socket and binding to source IP and port...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((my_node_ip, src_port))

    print(f"Attempting to connect to {target_node_ip}:{dst_port}...")
    try:
        s.connect((target_node_ip, dst_port))
    except:
        print(f"Unable to connect to {target_node_ip}:{dst_port}")
        s.close()
        return

    print("Connected successfully. Preparing and sending version packet...")
    version = version_packet(my_node_ip, target_node_ip, src_port, dst_port)
    s.send(version.to_bytes())
    print("Version packet sent. Awaiting response...")

    # print("Ignoring received version and verack packets...")
    # s.recv(1024)
    # s.recv(1024)
    s.settimeout(5.0)  # Set a timeout of 5 seconds
    time.sleep(5)

    print("Preparing and sending verack packet...")
    verack = msg_verack()
    s.send(verack.to_bytes())
    print("Verack packet sent.")

    print(f"Fetching block at height {block_height}...")
    block_data = get_block(block_height)

    if block_data is None:
        print("Error fetching block data. Aborting.")
        s.close()
        return

    print("Block fetched successfully. Preparing and sending block message...")

    # Deserialize the block data to a CBlock object
    block_obj = CBlock.deserialize(x(block_data))
    block_msg = msg_block(block_obj)

    s.send(block_msg.to_bytes())
    print("Block message sent.")

    print("Closing connection...")
    s.close()
    print("Connection closed successfully.")


def main():
    parser = argparse.ArgumentParser(description="Fetch a block by its height and send to a Bitcoin peer.")
    parser.add_argument('height', nargs='?', help='The height of the block.')
    parser.add_argument('target_ip', help='The IP of the target Bitcoin peer.')
    args = parser.parse_args()

    my_node_ip = '127.0.0.1'  # <- Here

    if args.height:
        block_height = int(args.height)
    else:
        block_height = int(input('Enter the block height: '))

    target_node_ip = args.target_ip

    establish_connection(my_node_ip, target_node_ip, block_height)


if __name__ == '__main__':
    main()
