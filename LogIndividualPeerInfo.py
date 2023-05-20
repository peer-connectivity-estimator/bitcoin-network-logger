from threading import Timer
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import time
import traceback

numSecondsPerSample = 60

directory = 'IndividualPeerInfoLog'

# Send a command to the linux terminal
def terminal(cmd):
	return os.popen(cmd).read()

# Send a command to the Bitcoin console
def bitcoin(cmd):
	if cmd == 'getpeerinfo':
		return """[
  {
    "id": 0,
    "addr": "108.221.203.186:8333",
    "addrbind": "10.0.2.5:39772",
    "addrlocal": "128.198.113.128:53467",
    "network": "ipv4",
    "services": "0000000000000409",
    "servicesnames": [
      "NETWORK",
      "WITNESS",
      "NETWORK_LIMITED"
    ],
    "relaytxes": false,
    "lastsend": 1684537703,
    "lastrecv": 1684537703,
    "last_transaction": 0,
    "last_block": 0,
    "bytessent": 1317,
    "bytesrecv": 198,
    "conntime": 1684537693,
    "timeoffset": 0,
    "pingwait": 13.252258,
    "version": 70016,
    "subver": "/Satoshi:22.0.0/",
    "inbound": false,
    "bip152_hb_to": false,
    "bip152_hb_from": false,
    "startingheight": 790525,
    "presynced_headers": -1,
    "synced_headers": -1,
    "synced_blocks": -1,
    "inflight": [
    ],
    "addr_relay_enabled": false,
    "addr_processed": 0,
    "addr_rate_limited": 0,
    "permissions": [
    ],
    "minfeefilter": 0.00000000,
    "bytessent_per_msg": {
      "getheaders": 1053,
      "ping": 32,
      "sendaddrv2": 24,
      "sendcmpct": 33,
      "verack": 24,
      "version": 127,
      "wtxidrelay": 24
    },
    "bytesrecv_per_msg": {
      "sendaddrv2": 24,
      "verack": 24,
      "version": 126,
      "wtxidrelay": 24
    },
    "connection_type": "block-relay-only"
  },
  {
    "id": 1,
    "addr": "119.42.55.203:8333",
    "addrbind": "10.0.2.5:57838",
    "addrlocal": "128.198.113.128:53468",
    "network": "ipv4",
    "services": "0000000000000409",
    "servicesnames": [
      "NETWORK",
      "WITNESS",
      "NETWORK_LIMITED"
    ],
    "relaytxes": false,
    "lastsend": 1684537694,
    "lastrecv": 1684537694,
    "last_transaction": 0,
    "last_block": 0,
    "bytessent": 1479,
    "bytesrecv": 1510,
    "conntime": 1684537694,
    "timeoffset": 0,
    "pingtime": 0.224998,
    "minping": 0.224998,
    "version": 70016,
    "subver": "/Satoshi:24.0.1/",
    "inbound": false,
    "bip152_hb_to": false,
    "bip152_hb_from": false,
    "startingheight": 790525,
    "presynced_headers": -1,
    "synced_headers": 790525,
    "synced_blocks": 790525,
    "inflight": [
    ],
    "addr_relay_enabled": false,
    "addr_processed": 0,
    "addr_rate_limited": 0,
    "permissions": [
    ],
    "minfeefilter": 0.00000000,
    "bytessent_per_msg": {
      "getheaders": 1053,
      "headers": 106,
      "ping": 32,
      "pong": 32,
      "sendaddrv2": 24,
      "sendcmpct": 33,
      "sendheaders": 24,
      "verack": 24,
      "version": 127,
      "wtxidrelay": 24
    },
    "bytesrecv_per_msg": {
      "feefilter": 32,
      "getheaders": 1053,
      "headers": 106,
      "ping": 32,
      "pong": 32,
      "sendaddrv2": 24,
      "sendcmpct": 33,
      "sendheaders": 24,
      "verack": 24,
      "version": 126,
      "wtxidrelay": 24
    },
    "connection_type": "block-relay-only"
  },
  {
    "id": 3,
    "addr": "71.184.224.62:8333",
    "addrbind": "10.0.2.5:55920",
    "addrlocal": "128.198.113.128:53471",
    "network": "ipv4",
    "services": "0000000000000409",
    "servicesnames": [
      "NETWORK",
      "WITNESS",
      "NETWORK_LIMITED"
    ],
    "relaytxes": true,
    "lastsend": 1684537710,
    "lastrecv": 1684537714,
    "last_transaction": 1684537706,
    "last_block": 0,
    "bytessent": 3958,
    "bytesrecv": 21697,
    "conntime": 1684537698,
    "timeoffset": 0,
    "pingtime": 0.09564499999999999,
    "minping": 0.09564499999999999,
    "version": 70016,
    "subver": "/Satoshi:22.0.0/",
    "inbound": false,
    "bip152_hb_to": false,
    "bip152_hb_from": false,
    "startingheight": 790524,
    "presynced_headers": -1,
    "synced_headers": -1,
    "synced_blocks": -1,
    "inflight": [
    ],
    "addr_relay_enabled": true,
    "addr_processed": 1001,
    "addr_rate_limited": 0,
    "permissions": [
    ],
    "minfeefilter": 0.00006554,
    "bytessent_per_msg": {
      "addrv2": 40,
      "feefilter": 32,
      "getaddr": 24,
      "getdata": 205,
      "getheaders": 1053,
      "headers": 106,
      "inv": 2202,
      "ping": 32,
      "pong": 32,
      "sendaddrv2": 24,
      "sendcmpct": 33,
      "verack": 24,
      "version": 127,
      "wtxidrelay": 24
    },
    "bytesrecv_per_msg": {
      "addrv2": 17981,
      "feefilter": 32,
      "getheaders": 1053,
      "headers": 25,
      "inv": 590,
      "ping": 32,
      "pong": 32,
      "sendaddrv2": 24,
      "sendcmpct": 66,
      "sendheaders": 24,
      "tx": 1664,
      "verack": 24,
      "version": 126,
      "wtxidrelay": 24
    },
    "connection_type": "outbound-full-relay"
  },
  {
    "id": 4,
    "addr": "217.180.221.162:8333",
    "addrbind": "10.0.2.5:46092",
    "network": "ipv4",
    "services": "0000000000000409",
    "servicesnames": [
      "NETWORK",
      "WITNESS",
      "NETWORK_LIMITED"
    ],
    "relaytxes": true,
    "lastsend": 1684537711,
    "lastrecv": 1684537711,
    "last_transaction": 1684537711,
    "last_block": 0,
    "bytessent": 4568,
    "bytesrecv": 63680,
    "conntime": 1684537699,
    "timeoffset": -2,
    "pingtime": 0.119029,
    "minping": 0.119029,
    "version": 70016,
    "subver": "/Satoshi:24.0.1/",
    "inbound": false,
    "bip152_hb_to": false,
    "bip152_hb_from": false,
    "startingheight": 790525,
    "presynced_headers": -1,
    "synced_headers": 790525,
    "synced_blocks": 790525,
    "inflight": [
    ],
    "addr_relay_enabled": true,
    "addr_processed": 1000,
    "addr_rate_limited": 0,
    "permissions": [
    ],
    "minfeefilter": 0.00005959,
    "bytessent_per_msg": {
      "feefilter": 32,
      "getaddr": 24,
      "getdata": 2828,
      "getheaders": 1053,
      "headers": 106,
      "inv": 205,
      "ping": 32,
      "pong": 32,
      "sendaddrv2": 24,
      "sendcmpct": 33,
      "sendheaders": 24,
      "verack": 24,
      "version": 127,
      "wtxidrelay": 24
    },
    "bytesrecv_per_msg": {
      "addrv2": 17245,
      "feefilter": 32,
      "getheaders": 1053,
      "headers": 106,
      "inv": 2609,
      "ping": 32,
      "pong": 32,
      "sendaddrv2": 24,
      "sendcmpct": 33,
      "sendheaders": 24,
      "tx": 42316,
      "verack": 24,
      "version": 126,
      "wtxidrelay": 24
    },
    "connection_type": "outbound-full-relay"
  }
]"""
	elif cmd == 'getpeersmsginfoandclear':
		return """{
  "CLOCKS PER SECOND": "1000000",
  "108.221.203.186": {
    "ADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "ADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CMPCTBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FEEFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERADD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERCLEAR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERLOAD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFILTERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETDATA": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "HEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "INV": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "MEMPOOL": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "MERKLEBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "NOTFOUND": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PING": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PONG": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "REJECT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDCMPCT": "1 msgs => ([1, 1.000000, 1] clcs, [0, 0.000000, 0] byts",
    "SENDHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDTXRCNCL": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "TX": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERACK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERSION": "1 msgs => ([12, 12.000000, 12] clcs, [0, 0.000000, 0] byts",
    "WTXIDRELAY": "1 msgs => ([177, 177.000000, 177] clcs, [102, 102.000000, 102] byts",
    "[UNDOCUMENTED]": "1 msgs => ([2, 2.000000, 2] clcs, [0, 0.000000, 0] byts"
  },
  "119.42.55.203": {
    "ADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "ADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CMPCTBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FEEFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERADD": "1 msgs => ([3, 3.000000, 3] clcs, [8, 8.000000, 8] byts",
    "FILTERCLEAR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERLOAD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFILTERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETDATA": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "HEADERS": "1 msgs => ([145, 145.000000, 145] clcs, [1029, 1029.000000, 1029] byts",
    "INV": "1 msgs => ([48, 48.000000, 48] clcs, [82, 82.000000, 82] byts",
    "MEMPOOL": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "MERKLEBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "NOTFOUND": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PING": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PONG": "1 msgs => ([105, 105.000000, 105] clcs, [8, 8.000000, 8] byts",
    "REJECT": "1 msgs => ([1, 1.000000, 1] clcs, [8, 8.000000, 8] byts",
    "SENDADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDCMPCT": "1 msgs => ([1, 1.000000, 1] clcs, [0, 0.000000, 0] byts",
    "SENDHEADERS": "1 msgs => ([16, 16.000000, 16] clcs, [9, 9.000000, 9] byts",
    "SENDTXRCNCL": "1 msgs => ([5, 5.000000, 5] clcs, [0, 0.000000, 0] byts",
    "TX": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERACK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERSION": "1 msgs => ([82, 82.000000, 82] clcs, [0, 0.000000, 0] byts",
    "WTXIDRELAY": "1 msgs => ([320, 320.000000, 320] clcs, [102, 102.000000, 102] byts",
    "[UNDOCUMENTED]": "1 msgs => ([2, 2.000000, 2] clcs, [0, 0.000000, 0] byts"
  },
  "217.180.221.162": {
    "ADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "ADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCK": "1 msgs => ([2276, 2276.000000, 2276] clcs, [17221, 17221.000000, 17221] byts",
    "BLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CMPCTBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FEEFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERADD": "1 msgs => ([3, 3.000000, 3] clcs, [8, 8.000000, 8] byts",
    "FILTERCLEAR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERLOAD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFILTERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETDATA": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "HEADERS": "1 msgs => ([67, 67.000000, 67] clcs, [1029, 1029.000000, 1029] byts",
    "INV": "1 msgs => ([9, 9.000000, 9] clcs, [82, 82.000000, 82] byts",
    "MEMPOOL": "6 msgs => ([729, 121.500000, 254] clcs, [3570, 595.000000, 1081] byts",
    "MERKLEBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "NOTFOUND": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PING": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PONG": "1 msgs => ([151, 151.000000, 151] clcs, [8, 8.000000, 8] byts",
    "REJECT": "1 msgs => ([4, 4.000000, 4] clcs, [8, 8.000000, 8] byts",
    "SENDADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDCMPCT": "1 msgs => ([2, 2.000000, 2] clcs, [0, 0.000000, 0] byts",
    "SENDHEADERS": "1 msgs => ([5, 5.000000, 5] clcs, [9, 9.000000, 9] byts",
    "SENDTXRCNCL": "1 msgs => ([1, 1.000000, 1] clcs, [0, 0.000000, 0] byts",
    "TX": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERACK": "83 msgs => ([92477, 1114.180723, 14650] clcs, [43547, 524.662651, 8485] byts",
    "VERSION": "1 msgs => ([128, 128.000000, 128] clcs, [0, 0.000000, 0] byts",
    "WTXIDRELAY": "1 msgs => ([609, 609.000000, 609] clcs, [102, 102.000000, 102] byts",
    "[UNDOCUMENTED]": "1 msgs => ([3, 3.000000, 3] clcs, [0, 0.000000, 0] byts"
  },
  "3.37.38.115": {
    "ADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "ADDRV2": "1 msgs => ([31, 31.000000, 31] clcs, [31, 31.000000, 31] byts",
    "BLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CMPCTBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FEEFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERADD": "1 msgs => ([2, 2.000000, 2] clcs, [8, 8.000000, 8] byts",
    "FILTERCLEAR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERLOAD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFILTERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETDATA": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "HEADERS": "1 msgs => ([141, 141.000000, 141] clcs, [1029, 1029.000000, 1029] byts",
    "INV": "1 msgs => ([17, 17.000000, 17] clcs, [82, 82.000000, 82] byts",
    "MEMPOOL": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "MERKLEBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "NOTFOUND": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PING": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PONG": "1 msgs => ([101, 101.000000, 101] clcs, [8, 8.000000, 8] byts",
    "REJECT": "1 msgs => ([1, 1.000000, 1] clcs, [8, 8.000000, 8] byts",
    "SENDADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDCMPCT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDHEADERS": "2 msgs => ([14, 7.000000, 10] clcs, [18, 9.000000, 9] byts",
    "SENDTXRCNCL": "1 msgs => ([13, 13.000000, 13] clcs, [0, 0.000000, 0] byts",
    "TX": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERACK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERSION": "1 msgs => ([66, 66.000000, 66] clcs, [0, 0.000000, 0] byts",
    "WTXIDRELAY": "1 msgs => ([260, 260.000000, 260] clcs, [102, 102.000000, 102] byts",
    "[UNDOCUMENTED]": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts"
  },
  "71.184.224.62": {
    "ADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "ADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCK": "2 msgs => ([2184, 1092.000000, 2172] clcs, [17933, 8966.500000, 17917] byts",
    "BLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CMPCTBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FEEFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERADD": "1 msgs => ([3, 3.000000, 3] clcs, [8, 8.000000, 8] byts",
    "FILTERCLEAR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERLOAD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFILTERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETDATA": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "HEADERS": "1 msgs => ([75, 75.000000, 75] clcs, [1029, 1029.000000, 1029] byts",
    "INV": "1 msgs => ([1, 1.000000, 1] clcs, [1, 1.000000, 1] byts",
    "MEMPOOL": "3 msgs => ([168, 56.000000, 75] clcs, [831, 277.000000, 325] byts",
    "MERKLEBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "NOTFOUND": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PING": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PONG": "1 msgs => ([90, 90.000000, 90] clcs, [8, 8.000000, 8] byts",
    "REJECT": "1 msgs => ([1, 1.000000, 1] clcs, [8, 8.000000, 8] byts",
    "SENDADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDCMPCT": "1 msgs => ([3, 3.000000, 3] clcs, [0, 0.000000, 0] byts",
    "SENDHEADERS": "2 msgs => ([6, 3.000000, 4] clcs, [18, 9.000000, 9] byts",
    "SENDTXRCNCL": "1 msgs => ([5, 5.000000, 5] clcs, [0, 0.000000, 0] byts",
    "TX": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERACK": "13 msgs => ([5321, 409.307692, 705] clcs, [3845, 295.769231, 477] byts",
    "VERSION": "1 msgs => ([251, 251.000000, 251] clcs, [0, 0.000000, 0] byts",
    "WTXIDRELAY": "1 msgs => ([986, 986.000000, 986] clcs, [102, 102.000000, 102] byts",
    "[UNDOCUMENTED]": "1 msgs => ([5, 5.000000, 5] clcs, [0, 0.000000, 0] byts"
  },
  "72.74.68.192": {
    "ADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "ADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCK": "1 msgs => ([2832, 2832.000000, 2832] clcs, [17409, 17409.000000, 17409] byts",
    "BLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CMPCTBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FEEFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERADD": "1 msgs => ([2, 2.000000, 2] clcs, [8, 8.000000, 8] byts",
    "FILTERCLEAR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERLOAD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFILTERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETDATA": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "HEADERS": "1 msgs => ([234, 234.000000, 234] clcs, [1029, 1029.000000, 1029] byts",
    "INV": "1 msgs => ([10, 10.000000, 10] clcs, [82, 82.000000, 82] byts",
    "MEMPOOL": "1 msgs => ([11, 11.000000, 11] clcs, [37, 37.000000, 37] byts",
    "MERKLEBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "NOTFOUND": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PING": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PONG": "1 msgs => ([490, 490.000000, 490] clcs, [8, 8.000000, 8] byts",
    "REJECT": "1 msgs => ([7, 7.000000, 7] clcs, [8, 8.000000, 8] byts",
    "SENDADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDCMPCT": "1 msgs => ([1, 1.000000, 1] clcs, [0, 0.000000, 0] byts",
    "SENDHEADERS": "1 msgs => ([16, 16.000000, 16] clcs, [9, 9.000000, 9] byts",
    "SENDTXRCNCL": "1 msgs => ([2, 2.000000, 2] clcs, [0, 0.000000, 0] byts",
    "TX": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERACK": "1 msgs => ([592, 592.000000, 592] clcs, [340, 340.000000, 340] byts",
    "VERSION": "1 msgs => ([147, 147.000000, 147] clcs, [0, 0.000000, 0] byts",
    "WTXIDRELAY": "1 msgs => ([2212, 2212.000000, 2212] clcs, [102, 102.000000, 102] byts",
    "[UNDOCUMENTED]": "1 msgs => ([2, 2.000000, 2] clcs, [0, 0.000000, 0] byts"
  },
  "72.83.171.244": {
    "ADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "ADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCK": "1 msgs => ([2763, 2763.000000, 2763] clcs, [17771, 17771.000000, 17771] byts",
    "BLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CMPCTBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FEEFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERADD": "1 msgs => ([5, 5.000000, 5] clcs, [8, 8.000000, 8] byts",
    "FILTERCLEAR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERLOAD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFILTERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETDATA": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "HEADERS": "1 msgs => ([106, 106.000000, 106] clcs, [1029, 1029.000000, 1029] byts",
    "INV": "1 msgs => ([9, 9.000000, 9] clcs, [82, 82.000000, 82] byts",
    "MEMPOOL": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "MERKLEBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "NOTFOUND": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PING": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PONG": "1 msgs => ([96, 96.000000, 96] clcs, [8, 8.000000, 8] byts",
    "REJECT": "1 msgs => ([4, 4.000000, 4] clcs, [8, 8.000000, 8] byts",
    "SENDADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDCMPCT": "1 msgs => ([6, 6.000000, 6] clcs, [0, 0.000000, 0] byts",
    "SENDHEADERS": "1 msgs => ([5, 5.000000, 5] clcs, [9, 9.000000, 9] byts",
    "SENDTXRCNCL": "1 msgs => ([2, 2.000000, 2] clcs, [0, 0.000000, 0] byts",
    "TX": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERACK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERSION": "1 msgs => ([616, 616.000000, 616] clcs, [0, 0.000000, 0] byts",
    "WTXIDRELAY": "1 msgs => ([1604, 1604.000000, 1604] clcs, [102, 102.000000, 102] byts",
    "[UNDOCUMENTED]": "1 msgs => ([10, 10.000000, 10] clcs, [0, 0.000000, 0] byts"
  },
  "95.111.229.184": {
    "ADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "ADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "BLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "CMPCTBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FEEFILTER": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERADD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERCLEAR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "FILTERLOAD": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETADDR": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETBLOCKTXN": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFCHECKPT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETCFILTERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETDATA": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "GETHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "HEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "INV": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "MEMPOOL": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "MERKLEBLOCK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "NOTFOUND": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PING": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "PONG": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "REJECT": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDADDRV2": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDCMPCT": "1 msgs => ([2, 2.000000, 2] clcs, [0, 0.000000, 0] byts",
    "SENDHEADERS": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "SENDTXRCNCL": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "TX": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERACK": "0 msgs => ([0, 0.000000, 0] clcs, [0, 0.000000, 0] byts",
    "VERSION": "1 msgs => ([319, 319.000000, 319] clcs, [0, 0.000000, 0] byts",
    "WTXIDRELAY": "1 msgs => ([2481, 2481.000000, 2481] clcs, [102, 102.000000, 102] byts",
    "[UNDOCUMENTED]": "1 msgs => ([2, 2.000000, 2] clcs, [0, 0.000000, 0] byts"
  }
}"""
	elif cmd == 'listnewbroadcastsandclear':
		return """{
  "new_block_broadcasts": {
  },
  "new_transaction_broadcasts": {
    "217.180.221.162": 89,
    "71.184.224.62": 13,
    "72.74.68.192": 1
  },
  "new_transaction_fee_broadcasts": {
    "217.180.221.162": 1564570,
    "71.184.224.62": 115383,
    "72.74.68.192": 7215
  },
  "new_transaction_size_broadcasts": {
    "217.180.221.162": 46003,
    "71.184.224.62": 3845,
    "72.74.68.192": 340
  }
}"""
	return terminal('./src/bitcoin-cli -rpcuser=cybersec -rpcpassword=kZIdeN4HjZ3fp9Lge4iezt0eJrbjSi8kuSuOHeUkEUbQVdf09JZXAAGwF3R5R2qQkPgoLloW91yTFuufo7CYxM2VPT7A5lYeTrodcLWWzMMwIrOKu7ZNiwkrKOQ95KGW8kIuL1slRVFXoFpGsXXTIA55V3iUYLckn8rj8MZHBpmdGQjLxakotkj83ZlSRx1aOJ4BFxdvDNz0WHk1i2OPgXL4nsd56Ph991eKNbXVJHtzqCXUbtDELVf4shFJXame -rpcport=8332 ' + str(cmd))

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
	line += 'Node time offset (seconds),'
	line += 'Ping Round Trip Time (milliseconds),'
	line += 'Minimum Ping Round Trip Time (milliseconds),'
	line += 'Ping Wait Time for an Outstanding Ping (milliseconds),'
	line += 'Address/Network Type,'
	line += 'Prototol Version,'
	line += 'Bitcoin Software Version,'
	line += 'Connection Type,'
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



def log(targetDateTime, sampleNumber):
	print(f'Adding Sample #{sampleNumber}:')
	global t
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

	for address in peersToUpdate:
		logNode(address, timestamp, peersToUpdate[address])


	print(f'    Sample successfully logged.')
	


	sampleNumber += 1
	targetDateTime += datetime.timedelta(seconds = numSecondsPerSample)
	offset = (targetDateTime - datetime.datetime.now()).total_seconds()
	t = Timer(offset, log, [targetDateTime, sampleNumber])
	t.daemon = True
	t.start()

if not os.path.exists(directory):
	print('Creating directory:', directory)
	os.makedirs(directory)

targetDateTime = datetime.datetime.now()
log(targetDateTime, 1)

while True:
	try:
		time.sleep(3600) # Every hour
	except KeyboardInterrupt as e:
		print(e)
		t.cancel()
		break

print('Logger terminated by user. Have a nice day!')