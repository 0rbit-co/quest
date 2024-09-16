#!/bin/bash
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}*              Langsung Crot aja ya          *${NC}"
echo -e "${CYAN}${BOLD}*               Saandy codeblocks                   *${NC}"
echo ""
echo -e "${YELLOW}${BOLD}This entire code is created by Brian (x.com/brianeedsleep)${NC}"
echo -e "${YELLOW}${BOLD}Make sure you have joined t.me/airdropsultanindonesia${NC}"
echo ""

# Option to choose RPC credentials
echo "Choose how to run the indexer:"
echo "1. Use custom RPC endpoint and credentials"
echo "2. Use default credentials (when using docker-compose)"
read -p "Enter your choice (1 or 2): " CHOICE

case $CHOICE in
  1)
    read -p "Enter Bitcoin Core RPC Username: " RPC_USER
    read -sp "Enter Bitcoin Core RPC Password: " RPC_PASSWORD
    echo
    read -p "Enter Bitcoin Core RPC URL (e.g., http://127.0.0.1:5000): " RPC_URL
    ;;
  2)
    RPC_URL="http://127.0.0.1:5000"
    RPC_USER="demo"
    RPC_PASSWORD="demo"
    ;;
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac

read -p "Enter Start Height (e.g., 42000): " START_HEIGHT
read -p "Enter Wallet Name: " WALLET_NAME

BITCOIN_CORE_REPO="https://github.com/mocacinno/btc_testnet4"
INDEXER_URL="https://github.com/rainbowprotocol-xyz/rbo_indexer_testnet/releases/download/v0.0.1-alpha/rbo_worker"
BITCOIN_CORE_DATA_DIR="/root/project/run_btc_testnet4/data"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

apt-get update
apt-get install -y docker.io docker-compose wget

mkdir -p $BITCOIN_CORE_DATA_DIR

git clone $BITCOIN_CORE_REPO
cd btc_testnet4

git switch bci_node

rm -f $DOCKER_COMPOSE_FILE

cat <<EOF > $DOCKER_COMPOSE_FILE
version: '3'
services:
  bitcoind:
    image: mocacinno/btc_testnet4:bci_node
    privileged: true
    container_name: bitcoind
    volumes:
      - /root/project/run_btc_testnet4/data:/root/.bitcoin/
    command: ["bitcoind", "-testnet4", "-server", "-txindex", "-rpcuser=demo", "-rpcpassword=demo", "-rpcallowip=0.0.0.0/0", "-rpcbind=0.0.0.0:5000"]
    ports:
      - "8333:8333"
      - "48332:48332"
      - "5000:5000"
EOF

cat $DOCKER_COMPOSE_FILE

docker compose up -d

sleep 30

docker exec -it bitcoind /bin/bash -c "bitcoin-cli -testnet4 -rpcuser=demo -rpcpassword=demo -rpcport=5000 createwallet $WALLET_NAME"
docker exec -it bitcoind /bin/bash -c "exit"

wget $INDEXER_URL
chmod +x rbo_worker

echo "INDEXER_LOGGER_FILE=./logs/indexer" > $ENV_FILE

./rbo_worker worker --rpc http://127.0.0.1:5000 --password demo --username demo --start_height $START_HEIGHT

echo "Setup completed. Make sure to check the JSON file and save your private key."

echo "For support, you don’t need to donate. Just follow me on x.com/brianeedsleep and join t.me/airdropsultanindonesia"
