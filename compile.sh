rm -rf src/bitcoind
make -j$(nproc)

params=""
for var in "$@"; do
    params="$params $var"
done
./run.sh $params
