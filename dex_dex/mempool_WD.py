from web3 import Web3
from web3.middleware import geth_poa_middleware
import time
import zmq
import asyncio
from json import load


class Mempool_WD:
    def __init__(self):
        self.web3 = Web3(Web3.WebsocketProvider("wss://fantom-mainnet-api.bwarelabs.com/ws/8ddb4b79-581f-4c26-89a2-2553555a8632"))#wss://fantom-mainnet-api.bwarelabs.com/ws/8ddb4b79-581f-4c26-89a2-2553555a8632 - wss://wsapi.fantom.network/ - wss://apis.ankr.com/wss/5103d987e26d4581a35ecc4d4ca924f8/9dff8dc6d9534002f0b6e851fbd88a53/fantom/full/main
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.router_adr = load(open("./router_addresses.json"))
        self.pair_adr = load(open("./pair_addresses.json"))
        self.zmq_pub = self.init_zmq()

    def init_zmq(self):
        socket = zmq.Context().socket(zmq.PUB)
        socket.bind("tcp://127.0.0.1:5555")
        return socket

    async def parse_tx(self, tx):
        print(tx)


#todo:benchmark
    async def get_mempool(self):
        pending = self.web3.geth.txpool.content()['pending']
        for adr in pending:
            for tx in list(pending[adr].keys()):
                pending_tx = dict(pending[adr][tx])
                if pending_tx['to'] == None:
                    continue
                if self.web3.toChecksumAddress(pending_tx['to']) in self.web3.toChecksumAddress(self.router_adr['SpiritSwapRouter']):
                    print('hash:' + str(pending_tx['hash']))
                    return {
                        'to' : 'SpiritSwapRouter',
                        'tot_gas_sent': self.web3.fromWei(self.web3.toInt(hexstr=pending_tx['gas']) * self.web3.toInt(hexstr=pending_tx['gasPrice']), 'ether')
                    }
                elif self.web3.toChecksumAddress(pending_tx['to']) in self.web3.toChecksumAddress(self.router_adr['SushiSwapRouter']):
                    print('hash:' + str(pending_tx['hash']))
                    return {
                        'to':'SushiSwapRouter',
                            'tot_gas_sent': self.web3.fromWei(self.web3.toInt(hexstr=pending_tx['gas']) * self.web3.toInt(hexstr=pending_tx['gasPrice']), 'ether')
                    }
                elif self.web3.toChecksumAddress(pending_tx['to']) in self.web3.toChecksumAddress(self.router_adr['SpookySwapRouter']):
                    print('hash:' + str(pending_tx['hash']))
                    return {
                        'to' : 'SpookySwapRouter',
                        'tot_gas_sent' : self.web3.fromWei(self.web3.toInt(hexstr=pending_tx['gas']) * self.web3.toInt(hexstr=pending_tx['gasPrice']), 'ether')
                    }

    #todo:benchmark
    async def log_loop(self,event_filter):
        while True:
                for event in event_filter.get_new_entries():
                    await self.handle_event(event)

    '''TODO: benchmark: 
        duration s: parse_tx '''

    async def handle_event(self, event):
        data = await self.parse_tx(await self.get_mempool())
        #self.zmq_pub.send_string(str(data))
        print('handle_event: '+str(data))

    def main(self):
        loop = asyncio.get_event_loop()
        block_filter = self.web3.eth.filter('pending')
        loop.run_until_complete(asyncio.ensure_future(self.log_loop(block_filter)))


dex = Mempool_WD()
dex.main()