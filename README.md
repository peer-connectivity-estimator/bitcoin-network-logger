Bitcoin Network Logger
=====================================
Log thousands of parameters specific to Bitcoin Core at a recurring interval, and generate data insights that have never been seen before.

---

This is a fork from the official Bitcoin Core main branch, which includes many additional features for testing the protocol and functionality of Bitcoin, as well as real-time logging of each individual peer connection, supporting Bitcoin over IPv4, IPv6, Tor, I2P, and CJDNS.

Instructions
----------------
For first-time users, inside a Debian version of Linux, run `./first_compile.sh` from the terminal to install all the necessary prerequisites, compile, and run Bitcoin.

If modifications are made to the code, run `./compile.sh` to only compile the code and run it, without the additional prerequisites/configurations from first_compile.sh.

If no modifications are made, run `./run.sh [PARAMETERS]` to start up Bitcoin, with no additional overhead from compile.sh or first_compile.sh. Parameters are separated by spaces, and can be in any order. They include:
* `./run.sh gui` -- Run Bitcoin Core in GUI mode.
* `./run.sh noconsole` -- Run Bitcoin Core, but do not auto-start the console.
* `./run.sh gdb` -- Run Bitcoin through the GNU Debugger (GDB).

Any other arguments supplied will be passed to bitcoind, for example:
* `./run.sh --debug=all --maxconnections=128`

---
By default, Bitcoin will store its blockchain in ~/.bitcoin. If this is the case, then run.sh will by default start Bitcoin in pruned mode, where it will only keep the last 550 blocks (a few gigabytes), to avoid the cost of a full blockchain (several hundred gigabytes).

If run.sh is successful, a window will show up labeled "Bitcoin Console", which is a python script (bitcoin_console.py) that communicates with Bitcoin. Within this window, type `help` to list all the available RPC commands, which can be used to interact with Bitcoin Core.

The Main Logger
----------------
The main network logging application can be ran with:
```python
python3 LogIndividualPeerInfo.py
```
First, check the configuration variables in the beginning of the file, which define the behaviors of the logger. Upon running the file, logs will be generated in a Research_Logs/Bitcoin_Log_X or Research_Logs/Bitcoin_**IBD**_Log_X (depending on whether the node is in Initial Block Download (IBD) mode or not), where X increments, starting at 1. At the end of each log, it will be compressed into a .tar.xz file for maximum compression, and copied over to the directory path: `outputFilesToTransferPath`. This is recommended to be an external storage device, like a USB flash drive. If the flash drive is not plugged in at the end of a sample, then it will resume logging but next time it finalizes a compressed Tar file and the directory at outputFilesToTransferPath does exist, then it will also move the past files that it was unable to move, so no data will be lost.

The compressed log directories are bulk, and contain `numSamplesPerDirectory` samples/rows. They include the following files:
* machine_info.txt -- Appends the machine specifications once upon directory creation
* machine_state.csv -- The primary log file containing information about the machine, one row is generated every `numSecondsPerSample` seconds
* blockchain_state_info.csv -- Keeps track of each newly received block (including forks)
* address_manager_bucket_info.csv -- Logs the contents of the address manager buckets every `numSamplesPerAddressManagerBucketLog` samples
* traceroutes.csv -- A simple ICMP traceroute to each IPv4 and IPv6 connection.
* debug.log -- Bitcoin's debug log with all categories enabled. Due to size limitations, this file is disabled by default, and is not generated.
* tor.log -- Tor's debug log. This is disabled by default and is not generated.
* i2pd.log -- I2P's debug log. This is disabled by default and is not generated.
The last type of file contains one file for each peer connection, and the corresponding file name is the peer's address.

Modifications
----------------

A new category of RPC commands exist under the label "Researcher". A few of them are as follows:
* count -- Displays the number of peer connections
* ls -- Displays the list of peer connections and each connection's ID
* getmsginfo -- Display the aggregate information about each message type, consisting of:
	* Count for how many times the message was received
	* Average number of bytes for the message
	* Maximum number of bytes for the message
	* Average number of clocks to process the message
	* Maximum number of clocks to process the message
	* At the end, a list of all undocumented messages received in Bitcoin
* getpeersmsginfo -- Display the getmsginfo for each individual peer connection
* getpeersmsginfoandclear -- Same as getpeersmsginfo, but then it clears all the data each RPC call
* listnewbroadcasts -- Displays information about the blocks and transactions for each peer, consisting of:
	* Number of unique block broadcasts for each peer
	* Latest block propagation time (system time)
	* Latest block propagation time (network adjusted time)
	* Number of unique transaction broadcasts for each peer
	* Fee in satoshi for the unique transactions for each peer
	* Size in bytes for the unique transactions for each peer
* listnewbroadcastsandclear -- Same as listnewbroadcasts, but then it clears all the data each RPC call
* getbucketinfo -- Print the entire contents of the every new and tried bucket, including statistics:
	* Addrman nKey
	* Number of tried entries
	* Number of (unique) new entries
	* Number of total addresses
	* Number of unrouteable new addresses
	* Number of unrouteable tried addresses
	* Number of IPv4 new addresses
	* Number of IPv4 tried addresses
	* Number of IPv6 new addresses
	* Number of IPv6 tried addresses
	* Number of TOR (v2 or v3) new addresses
	* Number of TOR (v2 or v3) tried addresses
	* Number of I2P new addresses
	* Number of I2P tried addresses
	* Number of CJDNS new addresses
	* Number of CJDNS tried addresses
	* Number of internal new addresses
	* Number of internal tried addresses
	* Last time Good was called
* getbucketentry "address" -- Get a specific entry from the buckets.
* sendaddr ( "peer_ip" "addrs_to_send" "seconds_offset" ) -- Send an ADDR message to a peer IP address, including a list of addresses to send, and the seconds offset for the nTime value in each address

A new optional parameter has also been added to the configuration, named `minconnections`. This can be used by adding `minconnections=X` to ~/.bitcoin/bitcoin.conf, where X is the number of outbound peer connections you would like to make. This overrides the previous "maxconnections=X" parameter with a more powerful function that forces the peer to connect to more connections than the default of 10 peers (even when incoming connections are disabled). 

---

For additional information about how to use each command, as well as a brief description of what each one does, enter `help` followed by the command in question.
