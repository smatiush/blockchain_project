from pyserum.market import Market
from pyserum.connection import conn
from pyserum.enums import OrderType, Side
from solana import account
from solana.publickey import PublicKey
from solana.rpc.types import TxOpts
import requests
from pprint import pprint

class solana:
    def __init__(self):
        self.raydium_base_url ='https://api.raydium.io/'
        self.ray_pools_url = self.raydium_base_url + 'pools'
        self.ray_pairs_url = self.raydium_base_url + 'pairs'
        self.serum_base_url  = 'https://serum-api.bonfida.com/'
        self.serum_pools_url = self.serum_base_url + 'pools-recent'
        self.serum_OB_url = self.serum_base_url + 'orderbook/' # + pair
        self.test_market = 'A8YFbxQYFVqKZaoYJLLUVcQiWP7G2MeEgW5wsAQgMvFw'

    def get_ray_pools(self):
        return requests.get(self.ray_pools_url).json()

    def get_serum_pools(self):
        return requests.get(self.serum_pools_url).json()

    def get_account(self):
        secret_key = []
        ac = account.Account(secret_key=secret_key[:32])
        if ac:
            return ac
        else:
            return False

    def get_market_serum(self, market:str):
        market_address = PublicKey(market)  # Address for BTC/USDC A8YFbxQYFVqKZaoYJLLUVcQiWP7G2MeEgW5wsAQgMvFw
        return Market.load(conn('https://api.mainnet-beta.solana.com'), market_address)

    def get_ob_serum(self):
        return [self.get_market_serum(self.test_market).load_asks(),self.get_market_serum(self.test_market).load_bids()]

    def limit_order(self):
        owner = self.get_account()
        payer = PublicKey("GVmKAFGVgkF6Xffj2AGEWDzqkxNeJUvJQnxbrF6awdEy")
        market = self.get_market_serum('A8YFbxQYFVqKZaoYJLLUVcQiWP7G2MeEgW5wsAQgMvFw')
        print(market.place_order(payer=payer,
                                 owner=owner,
                                 order_type=OrderType.LIMIT,
                                 side=Side.BUY,
                                 limit_price=1,
                                 max_quantity=1,
                                 opts = TxOpts()))

    def market_order(self, side:bool):
        market = self.get_market_serum(self.test_market)
        if side == True:#buy
            #obL1 = get_ob()['data']['asks'][0]
            side = Side.BUY
        else:
            #obL1 = get_ob()['data']['bids'][0]
            side = Side.SELL
        owner = self.get_account()
        payer = PublicKey("GVmKAFGVgkF6Xffj2AGEWDzqkxNeJUvJQnxbrF6awdEy")#my wallet usdtc (con deposito)
        print(market.place_order(payer=payer,
                                 owner=owner,
                                 order_type=OrderType.IOC,
                                 side=side,
                                 limit_price=75000,
                                 max_quantity=0.0001,
                                 opts=TxOpts()))

if __name__ == '__main__':
    ray = solana()
    #pprint(ray.get_ray_pools())
    #pprint(ray.get_serum_pools())
    #print(ray.get_account())
    #print(ray.get_market_serum('A8YFbxQYFVqKZaoYJLLUVcQiWP7G2MeEgW5wsAQgMvFw'))
    #print(ray.get_ob_serum())
    #print(ray.limit_order())
    #print(ray.market_order(True))

