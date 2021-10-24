from web3.auto import Web3
from web3.middleware import geth_poa_middleware
from json import load
from discord_sender import send_discord_msg as snd_DiscordMsg


#factory pancacke: 0xBCfCcbde45cE874adCB698cC183deBcF17952812
class uniswapV2_pair:
    #TODO: implementare events from smart contract ed implementare State-Changing Functions: https://uniswap.org/docs/v2/smart-contracts/pair/
    def __init__(self, contract_addr):
        self.tick_data = dict()
        self.contr_adr = contract_addr
        self.w3 = Web3(Web3.WebsocketProvider('ws://192.168.1.7:8546', websocket_timeout=5))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.contract = self.w3.eth.contract(address=contract_addr, abi=self.get_abi())
        #self.w3.eth.filter('latest')
        self.filter_swap = self.contract.events.Swap.createFilter(fromBlock="pending")

    def get_decimals_token0(self):
        return self.w3.eth.contract(address=self.get_token0_adr(), abi=load(open("../UniswapV2ERC20.json"))['abi']).functions.decimals().call()

    def get_decimals_token1(self):
        return self.w3.eth.contract(address=self.get_token1_adr(), abi=load(open("../UniswapV2ERC20.json"))['abi']).functions.decimals().call()

    def get_abi(self):
        with open("../pancake_pair_abi.json", "r") as fp:
            abi = load(fp)
            return abi#["abi"]

    def easy_print_pair(self):
            print("#############################################################")
            print(self.get_token0_adr())
            print(self.get_token1_adr())
            print(self.get_reserves())
            print(self.get_price0CumulativeLast())

    def get_token0_adr(self):
        return self.contract.functions.token0().call()

    def get_token1_adr(self):
        return self.contract.functions.token1().call()

    def get_reserves(self):
        return self.contract.functions.getReserves().call()

    def get_price0CumulativeLast(self):
        return self.contract.functions.price0CumulativeLast().call()

    def get_price1CumulativeLast(self):
        return self.contract.functions.price1CumulativeLast().call()

    def get_kLast(self):
        return self.contract.functions.kLast().call()

    async def get_swap(self):
        #self.filter_swap.get_all_entries()
        while True:
            trades = self.filter_swap.get_new_entries()
            if len(trades) > 0:
                for swap in trades:
                    # eth/dai price(BUY)
                    if swap['args']["amount0Out"] > 0:
                        self.tick_data["timestamp"] = self.w3.eth.get_block(self.w3.eth.getTransaction(swap["transactionHash"])['blockNumber'])['timestamp']
                        self.tick_data["price"] = float(swap['args']["amount0Out"]/10**self.get_decimals_token0()) / float(swap['args']["amount1In"]/10**self.get_decimals_token1())
                        self.tick_data["side"] = 0
                        self.tick_data["size"] = swap['args']["amount0Out"]/10**self.get_decimals_token0()
                        self.tick_data["blockNumber"] = self.w3.eth.getTransaction(swap["transactionHash"])['blockNumber']
                    # eth/dai price(BUY)
                    elif swap['args']["amount0In"] > 0:
                        self.tick_data["timestamp"] = self.w3.eth.get_block(self.w3.eth.getTransaction(swap["transactionHash"])['blockNumber'])['timestamp']
                        self.tick_data["price"] = float(swap['args']["amount0In"]/10**self.get_decimals_token0()) / float(swap['args']["amount1Out"]/10**self.get_decimals_token1())
                        self.tick_data["side"] = 1
                        self.tick_data["size"] = swap['args']["amount0In"]/10**self.get_decimals_token0()
                        self.tick_data["blockNumber"] = self.w3.eth.getTransaction(swap["transactionHash"])['blockNumber']
                #print("new_entr: "+ str(self.filter_swap.get_new_entries()))
                print(self.tick_data)


class pancacke_factory:
    def __init__(self):
        self.contr_adr = "0xBCfCcbde45cE874adCB698cC183deBcF17952812"
        self.w3 = Web3(Web3.WebsocketProvider('ws://192.168.1.7:8546', websocket_timeout=5))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.contract_factory = self.w3.eth.contract(address=self.contr_adr, abi=self.get_abi(
            "../UniswapV2Factory.json"))
        # self.w3.eth.filter('latest')
        self.filter_swap = self.contract_factory.events.PairCreated.createFilter(fromBlock="latest")

    def get_abi(self, file_name):
        with open(str(file_name), "r") as fp:
            abi = load(fp)
            return abi["abi"]

    def get_num_CreatedPair(self):
        return self.contract.functions.allPairsLength().call()

    def get_created_pair(self):
        num_pair = self.contract_factory.functions.allPairsLength().call()
        print(num_pair)
        while True:#5534
            new_num_pair = self.contract_factory.functions.allPairsLength().call()
            if new_num_pair > num_pair:
                data_PairCreated = self.contract_factory.functions.allPairs(new_num_pair-1).call()
                yield data_PairCreated
            else:
                print('created_pair: '+str(num_pair))
            num_pair = new_num_pair

    def get_reserve(self, address):
        liq_pools = {}
        contract_pair =  self.w3.eth.contract(address=address, abi = self.get_abi("../UniswapV2Pair.json"))
        token0 = contract_pair.functions.token0().call()
        token1 = contract_pair.functions.token1().call()
        contract_ERC20_token0  = self.w3.eth.contract(address=token0, abi = self.get_abi("../UniswapV2ERC20.json"))
        contract_ERC20_token1  = self.w3.eth.contract(address=token1, abi = self.get_abi("../UniswapV2ERC20.json"))
        reserve = contract_pair.functions.getReserves().call()
        liq_pools[contract_ERC20_token0.functions.symbol().call()] = reserve[0]/10**contract_ERC20_token0.functions.decimals().call()
        liq_pools[contract_ERC20_token1.functions.symbol().call()] = reserve[1]/10**contract_ERC20_token1.functions.decimals().call()
        liq_pools["timestamp"]  = reserve[2]
        return liq_pools

    def main(self):
        for address in self.get_created_pair():
            reserve  = self.get_reserve(address)
            snd_DiscordMsg("address:"+str(address)+"\n reserve: "+str(reserve))
            with open("listing.txt", "w+") as fp:
                fp.write(str("address:"+str(address)+"\n reserve: "+str(reserve)))



if __name__ == "__main__":
    pck = pancacke_factory()
    pck.main()