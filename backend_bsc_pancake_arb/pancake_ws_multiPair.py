from web3.auto import Web3
from web3.middleware import geth_poa_middleware
from web3._utils import filters
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from json import load
import asyncio
from aiostream import stream
from pprint import pprint
import zmq

class pancakeV2_pair:
    #TODO: implementare events from smart contract ed implementare State-Changing Functions: https://uniswap.org/docs/v2/smart-contracts/pair/
    def __init__(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:5556")
        self.w3 = Web3(Web3.WebsocketProvider('ws://93.148.7.113:8546', websocket_timeout=5))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.swap_data = dict()
        self.swaps = list()
        self.adr_list = load(open("settings.json"))["address_pair"]
        self.registry_StableCoin = ["0x55d398326f99059fF775485246999027B3197955",#usdt
                                    "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",#busd
                                    "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"]#usdc



    def get_symbol(self,adr):
        return self.w3.eth.contract(address=adr, abi=load(open("UniswapV2ERC20.json"))['abi']).functions.symbol().call()

    def get_decimals_token0(self, adr):
        return self.w3.eth.contract(address=self.get_token0_adr(adr), abi=load(open("UniswapV2ERC20.json"))['abi']).functions.decimals().call()

    def get_decimals_token1(self,adr):
        return self.w3.eth.contract(address=self.get_token1_adr(adr), abi=load(open("UniswapV2ERC20.json"))['abi']).functions.decimals().call()

    def get_abi(self):
        with open("pancake_pair_abi.json", "r") as fp:
            abi = load(fp)
            return abi#["abi"]

    def easy_print_pair(self):
            print("#############################################################")
            print(self.get_token0_adr())
            print(self.get_token1_adr())
            print(self.get_reserves())
            print(self.get_price0CumulativeLast())

    def get_token0_adr(self,address):
        contract = self.w3.eth.contract(address=address, abi=self.get_abi())
        return contract.functions.token0().call()

    def get_token1_adr(self, address):
        contract = self.w3.eth.contract(address=address, abi=self.get_abi())
        return contract.functions.token1().call()

    def get_reserves(self):
        return self.contract.functions.getReserves().call()

    def get_price0CumulativeLast(self):
        return self.contract.functions.price0CumulativeLast().call()

    def get_price1CumulativeLast(self):
        return self.contract.functions.price1CumulativeLast().call()

    def get_kLast(self):
        return self.contract.functions.kLast().call()


    async def swap_events(self, address):
        tick_data = dict()
        self.swaps = list()
        contract = self.w3.eth.contract(address=address, abi=self.get_abi())
        filter_swap = contract.events.Swap.createFilter(fromBlock='latest')
        trades = filter_swap.get_new_entries()
        print("new "+str(address)+":"+str(len(trades)))
        while True:
            trades = filter_swap.get_new_entries()
            if len(trades) > 0:
                for swap in trades:
                    print(self.get_token0_adr(swap["address"]),self.registry_StableCoin)
                    if self.get_token0_adr(swap["address"]) in self.registry_StableCoin:
                        print(swap)
                        if swap["args"]["amount0Out"] > 0:
                            price =  float(swap['args']["amount0Out"]/10**self.get_decimals_token0(address)) / float(swap['args']["amount1In"]/10**self.get_decimals_token1(address))
                            side = 0 #sell out_token0 usd
                            size = swap['args']["amount0Out"]/10**self.get_decimals_token0(address)
                        else:
                            print(swap)
                            price =float(swap['args']["amount0In"]/10**self.get_decimals_token0(address)) / float(swap['args']["amount1Out"]/10**self.get_decimals_token1(address))
                            side = 1 #buy in usd
                            size = swap['args']["amount0In"]/10**self.get_decimals_token0(address)
                    else:
                        if swap["args"]["amount0Out"] > 0:
                            price = float(swap['args']["amount1In"]/10**self.get_decimals_token1(address)) / float(swap['args']["amount0Out"]/10**self.get_decimals_token0(address))
                            side = 1 #buy usdt in
                            size = swap['args']["amount1In"]/10**self.get_decimals_token0(address)
                        else:
                            price = float(swap['args']["amount1Out"] / 10 ** self.get_decimals_token1(address)) / float(swap['args']["amount0In"] / 10 ** self.get_decimals_token0(address))
                            side = 0 #sell usdt out
                            size = swap['args']["amount1Out"] / 10 ** self.get_decimals_token0(address)
                    tick_data["timestamp"] = self.w3.eth.get_block(self.w3.eth.getTransaction(swap["transactionHash"])['blockNumber'])['timestamp']
                    tick_data["symbol"] = self.get_symbol(self.get_token0_adr(swap["address"]))+"-"+self.get_symbol(self.get_token1_adr(swap["address"]))
                    tick_data["price"] = price
                    tick_data["side"] = side
                    tick_data["size"] = size
                    tick_data["blockNumber"] = self.w3.eth.getTransaction(swap["transactionHash"])['blockNumber']
                    tick_data["adr_pair"] = swap["address"]
                    self.swaps.append(tick_data)
                    self.socket.send_string(str(tick_data))
                    print('send_tick:',address)
                    yield tick_data
                    '''elif swap['args']["amount0In"] > 0:
                        tick_data["timestamp"] = self.w3.eth.get_block(self.w3.eth.getTransaction(swap["transactionHash"])['blockNumber'])['timestamp']
                        tick_data["symbol"] = str(self.get_symbol(self.get_token0_adr(address)))+"-"+str(self.get_symbol(self.get_token0_adr(address)))
                        tick_data["price"] = float(swap['args']["amount1Out"]/10**self.get_decimals_token1(address)) / float(swap['args']["amount0In"]/10**self.get_decimals_token0(address))
                        tick_data["side"] = 1
                        tick_data["size"] = swap['args']["amount0In"]/10**self.get_decimals_token0(address)
                        tick_data["blockNumber"] = self.w3.eth.getTransaction(swap["transactionHash"])['blockNumber']
                        tick_data["adr_pair"] = swap["address"]
                        self.swaps.append(tick_data)
                        self.socket.send_string(str(tick_data))
                        print('mandato_1_ ',str(address))
                        yield tick_data'''
            await asyncio.sleep(0)
                    #print("BNB-BUSD:" + str(len(self.swap_data["0x1B96B92314C44b159149f7E0303511fB2Fc4774f"])))
                #return tick_data#await asyncio.sleep(0.00000000000001)

    async def mix_stream(self):
        pending = list()
        temp = list()
        for key, adr in self.adr_list.items():
            # self.swap_data[adr] = list()
            pending.append(self.swap_events(adr))
        mix = stream.combine.merge(*pending)
        print(await stream.list(mix))
        return await stream.list(mix)

    def main(self):
        loop = asyncio.get_event_loop()
        while True:
            a = loop.create_task(self.mix_stream())
            b = loop.run_until_complete(a)
            print(b)
        #a = loop.run_forever()
                #print(pending)
            #for task in pending:
                #print(task)
            #a = loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            #print("BNB-BUSD:"+str(len(self.swap_data["0x1B96B92314C44b159149f7E0303511fB2Fc4774f"])))
            #pending.clear()
        #loop.run_forever()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    pck = pancakeV2_pair()
    pck.main()
    #print("b: "+str(b))
    #loop.run_forever()

    #asyncio.run(pck.get_swap())