import requests

from dcentrapi.Base import Base


class RpcAggregation(Base):

    def test(self):
        url = self.url + "test"
        response = requests.get(url, headers=self.headers2)
        return response.json()

    def get_token_balance(self, user, token, network, rpc_url=None):
        url = self.url + "tokenBalance"
        data = {
            "network": network,
            "user": user,
            "token": token,
            "rpc_url": rpc_url,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_token_balances_for_user(self, user, tokens : list, network, rpc_url=None):
        url = self.url + "tokenBalancesForUser"
        data = {
            "network": network,
            "user": user,
            "tokens": tokens,
            "rpc_url": rpc_url,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def get_token_balance_for_users(self, users : list, token, network, rpc_url=None):
        url = self.url + "tokenBalanceForUsers"
        data = {
            "network": network,
            "users": users,
            "token": token,
            "rpc_url": rpc_url,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def calculate_token_price_from_pair(self, pool, network, rpc_url=None):
        url = self.url + "calculateTokenPriceFromPair"
        data = {
            "network": network,
            "lp_token": pool,
            "rpc_url": rpc_url,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()
    
    def calculate_reserves_amount_from_pair(self, pool, amount, network, rpc_url=None):
        url = self.url + "calculateReservesAmountsFromPair"
        data = {
            "network": network,
            "lp_token": pool,
            "amount": amount,
            "rpc_url": rpc_url,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()
    
    def get_reserves_from_pair(self, pool, network, rpc_url=None):
        url = self.url + "getReservesFromPair"
        data = {
            "network": network,
            "lp_token": pool,
            "rpc_url": rpc_url,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()





