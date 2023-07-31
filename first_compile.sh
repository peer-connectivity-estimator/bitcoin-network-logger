sudo add-apt-repository -y ppa:bitcoin/bitcoin
sudo apt-get -y update

# Bitcoin dependencies
sudo apt-get -y install build-essential libtool autotools-dev automake pkg-config bsdmainutils python3
# Build with self-compiled depends to re-enable wallet compatibility
sudo apt-get -y install libssl-dev libevent-dev libboost-all-dev

# GUI dependencies
sudo apt-get -y install libqt5gui5 libqt5core5a libqt5dbus5 qttools5-dev qttools5-dev-tools libprotobuf-dev protobuf-compiler
sudo apt-get -y install libqrencode-dev

# Bitcoin wallet functionality
sudo apt-get -y install libdb-dev libdb++-dev

# Incoming connections
sudo apt-get -y install libminiupnpc-dev

# Used to check what windows are open
sudo apt-get -y install wmctrl

# Traceroute access
sudo apt-get -y install inetutils-traceroute

make clean

./autogen.sh
./configure --with-miniupnpc --enable-upnp-default --with-incompatible-bdb # --disablewallet # --prefix=`pwd`/depends/x86_64-linux-gnu
#./configure --without-miniupnpc --enable-upnp-default --with-incompatible-bdb # --disablewallet # --prefix=`pwd`/depends/x86_64-linux-gnu

make -j$(nproc)


# Compile Tor
rm -rf tor-researcher
git clone https://github.com/peer-connectivity-estimator/tor-researcher.git
cd tor-researcher
./first_compile.sh
cd ..

# Compile I2P
rm -rf i2pd-researcher
git clone https://github.com/peer-connectivity-estimator/i2pd-researcher.git
cd i2pd-researcher
./first_compile.sh
cd ..

# Compile CJDNS
rm -rf cjdns-researcher
git clone https://github.com/peer-connectivity-estimator/cjdns-researcher.git
cd cjdns-researcher
./first_compile.sh
cd ..


params=""
for var in "$@"; do
    params="$params $var"
done
./run.sh $params
