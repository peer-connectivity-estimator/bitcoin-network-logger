sudo add-apt-repository ppa:bitcoin/bitcoin
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

./autogen.sh
./configure --with-miniupnpc --enable-upnp-default --with-incompatible-bdb # --disablewallet # --prefix=`pwd`/depends/x86_64-linux-gnu
#./configure --without-miniupnpc --enable-upnp-default --with-incompatible-bdb # --disablewallet # --prefix=`pwd`/depends/x86_64-linux-gnu

make -j$(nproc)

params=""
for var in "$@"; do
    params="$params $var"
done
./run.sh $params
