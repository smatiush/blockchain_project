from web3 import Web3
from web3.middleware import geth_poa_middleware
from json import load
from pprint import pprint
import time
import zmq
from zmq.asyncio import Context
import asyncio
import discord
import requests
from discord import Webhook, RequestsWebhookAdapter
import logging
#logging.basicConfig(filename="DexArb_trade_exec_V0.log",
#                    format='%(asctime)s %(message)s',
#                    filemode='w')

class ws_dex():
    def __init__(self):
        self.web3 = Web3(Web3.WebsocketProvider("wss://fantom-mainnet-api.bwarelabs.com/ws/8ddb4b79-581f-4c26-89a2-2553555a8632"))#wss://fantom-mainnet-api.bwarelabs.com/ws/8ddb4b79-581f-4c26-89a2-2553555a8632 - wss://wsapi.fantom.network/
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.router_adr = load(open("./router_addresses.json"))
        self.pair_adr = load(open("./pair_addresses.json"))
        self.pairs_contracts = self.load_Pair_contract()
        self.tokens_info = self.load_token_info()
        self.arb_cntrct = self.web3.eth.contract(address='0x8Adc94aED8DF0a7F5d3Fa1b4E6134dc19D4b6E2C', abi=load(open("./abi/arb_contract.json")))
        self.webhook = Webhook.from_url("https://discord.com/api/webhooks/868492745168277545/8ZIVOqY-qP_O308PeoeN1tCwpnJod8lffWMG1QRoiJJvrVE8tzc9wFM8OURNhsUjc6Rc", adapter=RequestsWebhookAdapter())
        self.zmq_sub = self.init_zmq()

    def init_zmq(self):
        socket = zmq.Context().socket(zmq.SUB)
        socket.set(zmq.SUBSCRIBE, b"")
        socket.connect("tcp://127.0.0.1:5555")
        return socket

    def load_Pair_contract(self):
        pairs_contracts = {}
        for dex in list(self.pair_adr.keys()):
            for ticker in list(self.pair_adr[dex].keys()):
                pairs_contracts[dex + '/' + ticker] = self.web3.eth.contract(address=self.web3.toChecksumAddress(self.pair_adr[dex][ticker]), abi=load(open("./abi/IUniswapV2Pair.json"))['abi'])
        return pairs_contracts

    def get_PairData(self):
        for pair in list(self.pairs_contracts.keys()):
            token0 = self.pairs_contracts[pair].functions.token0().call()
            token1 = self.pairs_contracts[pair].functions.token1().call()
        return {
            'pair_name': pair,
            'token0' : token0,
            'token1' : token1
        }

    def load_token_info(self):
        token_adr_list = [self.get_PairData()['token0'], self.get_PairData()['token1']]
        token_info = {}
        for token_index in range(len(token_adr_list)):
            token_contract = self.web3.eth.contract(address=token_adr_list[token_index], abi=load(open("./abi/ERC20.json"))['abi'])
            decimals = token_contract.functions.decimals().call()
            symbol = token_contract.functions.symbol().call()
            token_info[token_adr_list[token_index]] = {'decimals': decimals, 'symbol': symbol}
        return token_info

    def get_PriceData(self):
        #start_time = time.time()
        price_data = {}
        for pair in list(self.pairs_contracts.keys()):
            reserves = self.pairs_contracts[pair].functions.getReserves().call()
            price_data[pair] = {'last_price': reserves[0]/10 ** self.tokens_info[list(self.tokens_info.keys())[0]]['decimals'] / reserves[1]/10 ** self.tokens_info[list(self.tokens_info.keys())[1]]['decimals']}
        #end_time = time.time()
        #print('duration PriceData: ' + str(end_time - start_time))
        return price_data

    async def get_TradeInfo(self):
        start_time = time.time()
        price_dex0 =  self.get_PriceData()[list(self.get_PriceData().keys())[0]]['last_price']
        price_dex1 =  self.get_PriceData()[list(self.get_PriceData().keys())[1]]['last_price']
        difference = price_dex0 - price_dex1
        profit_dex0_dex1 = ((price_dex0/price_dex1)-1)*100
        profit_dex1_dex0 = ((price_dex1/price_dex0)-1)*100
        end_time = time.time()
        #self.logger.debug('get_TradeInfo Duration: '+ str(end_time - start_time))
        print('get_TradeInfo Duration: '+ str(end_time - start_time))
        return {'price_dex0':price_dex0,
                'price_dex1':price_dex1,
                list(self.get_PriceData().keys())[0][:list(self.get_PriceData().keys())[0].find('/')] + '->' + list(self.get_PriceData().keys())[1][:list(self.get_PriceData().keys())[1].find('/')] : profit_dex0_dex1,
                list(self.get_PriceData().keys())[1][:list(self.get_PriceData().keys())[1].find('/')] + '->' + list(self.get_PriceData().keys())[0][:list(self.get_PriceData().keys())[0].find('/')]: profit_dex1_dex0}

    async def handle_event(self, event):
        #sushi to spooky
        start_time = time.time()
        #dex_PriceData = [self.get_PairData(self.web3.toChecksumAddress(self.pair_adr['SushiSwap']['USDC-WFTM'])), self.get_PairData(self.web3.toChecksumAddress(self.pair_adr['SpiritSwap']['USDC-WFTM']))]
        trade_info = await self.get_TradeInfo()
        print(trade_info)
        #print(event)
        #self.get_mempool()
        if trade_info['SushiSwap->SpiritSwap'] > 0.75:
            self.webhook.send('block_number pre-tx: ' + str(self.web3.eth.get_block_number()))
            receipit = await self.do_trade([self.router_adr['SushiSwapRouter'], self.router_adr['SpookySwapRouter']])
            self.webhook.send('info trade - sushi -> spooky : ' + str(trade_info))
            self.webhook.send('block_number post-tx: ' + str(self.web3.eth.get_block_number()))
            self.webhook.send('tx_hash:' + str(receipit))
            end_time = time.time()
            self.webhook.send('get_handle_event Duration: ' + str(end_time - start_time))
        elif trade_info['SpiritSwap->SushiSwap'] > 0.75:
            self.webhook.send('block_number pre-tx: ' + str(self.web3.eth.get_block_number()))
            receipit = await self.do_trade([self.router_adr['SpookySwapRouter'], self.router_adr['SushiSwapRouter']])
            self.webhook.send('info trade - spooky -> sushi : ' + str(trade_info))
            self.webhook.send('block_number post-tx: ' + str(self.web3.eth.get_block_number()))
            self.webhook.send('tx_hash:' + str(receipit))
            end_time = time.time()
            self.webhook.send('get_handle_event Duration: ' + str(end_time - start_time))
        end_time = time.time()
        print('get_handle_event Duration: '+ str(end_time - start_time))

#todo: provare transact
    async def do_trade(self, dex_path):
        start_time = time.time()
        adr_token0 = '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75' # usdc
        adr_token1 = '0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83' # wftm
        pvt_key = '377d28625eea5903c4f524efda9080861f3c751214d7e1df1ce74908657f4799'
        tx = await self.arb_cntrct.functions.simple_arb_swap(adr_token0, adr_token1, [dex_path[0], dex_path[1]]).buildTransaction({
            'from': self.web3.toChecksumAddress('0xc4EB816fDd19e6943bf39217733869e4C3FD59a9'),
            'nonce': self.web3.eth.get_transaction_count('0xc4EB816fDd19e6943bf39217733869e4C3FD59a9'),
            'gas': 700000,
            'gasPrice': int((self.web3.eth.gas_price + (self.web3.eth.gas_price*20/100)))})
        signed_txn = self.web3.eth.account.sign_transaction(tx, private_key=pvt_key)
        print('signed')
        receipit = self.web3.toHex(self.web3.eth.sendRawTransaction(signed_txn.rawTransaction))
        end_time = time.time()
        self.webhook.send('do_trade Duration: '+ str(end_time - start_time))
        print('do_trade Duration: '+ str(end_time - start_time))
        self.logger.debug('do_trade Duration: '+ str(end_time - start_time))
        return receipit

    async def log_loop(self,event_filter):
        while True:
                for event in event_filter.get_new_entries():
                    print(self.zmq_sub.recv())
                    await self.handle_event(event)

    def main(self):
        '''loop = asyncio.get_event_loop()
        block_filter = self.web3.eth.filter('pending')
        loop.run_until_complete(asyncio.ensure_future(self.log_loop(block_filter)))'''
        while True:
            print(self.zmq_sub.recv())
            time.sleep(0.5)
        #print(self.do_trade([self.router_adr['SushiSwapRouter'], self.router_adr['SpookySwapRouter']]))
        #while True:
        #    print(self.get_mempool())
        #    time.sleep(0.5)
        #print(self.load_Pair_contract())
        #self.load_token_info()
        #self.get_PriceData()
        #self.get_TradeInfo()

dex = ws_dex()
dex.main()