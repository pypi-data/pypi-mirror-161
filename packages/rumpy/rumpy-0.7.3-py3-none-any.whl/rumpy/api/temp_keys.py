from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://149.56.22.113:8545'))

w3.isConnected()