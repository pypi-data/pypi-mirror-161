import requests
from dcentrapi.Base import Base


class EventPolling(Base):

    def get_collection(self, collection_name):
        url = self.url + "event_polling/collection"
        data = {
            "collection_name": collection_name,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def set_schema(self, contract_name, contract_version, abi):
        url = self.url + "event_polling/schema"
        data = {
            "contract_name": contract_name,
            "contract_version": contract_version,
            "abi": abi,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def add_collection_contract(self, contract_address, schema_id, network_name, collection_name):
        url = self.url + "event_polling/collection_contract"
        data = {
            "contract_address": contract_address,
            "schema_id": schema_id,
            "network_name": network_name,
            "collection_name": collection_name,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_schema(self, contract_name, contract_version):
        url = self.url + "event_polling/schema"
        data = {
            "contract_name": contract_name,
            "contract_version": contract_version,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_events_sum_of_values_in_range(self, collection_name, contract_address, event_name, field_name, start_time, end_time):
        url = self.url + "event_polling/events_sum_of_values_in_range"
        data = {
            "collection_name": collection_name,
            "contract_address": contract_address,
            "event_name": event_name,
            "field_name": field_name,
            "start_time": start_time,
            "end_time": end_time,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_sum_of_values_in_range(self, collection_name, event_name, field_name, start_time, end_time):
        url = self.url + "event_polling/collection_sum_of_values_in_range"
        data = {
            "collection_name": collection_name,
            "event_name": event_name,
            "field_name": field_name,
            "start_time": start_time,
            "end_time": end_time,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_contracts_sum_of_values(self, collection_name, event_name, field_name, start_time, end_time):
        url = self.url + "event_polling/collection_contracts_sum_of_values"
        data = {
            "collection_name": collection_name,
            "event_name": event_name,
            "field_name": field_name,
            "start_time": start_time,
            "end_time": end_time,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_daily_nof_transactions(self, collection_name, start_time, end_time):
        url = self.url + "event_polling/collection_daily_nof_transactions"
        data = {
            "collection_name": collection_name,
            "start_time": start_time,
            "end_time": end_time,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_nof_transactions(self, collection_name):
        url = self.url + "event_polling/collection_nof_transactions"
        data = {
            "collection_name": collection_name,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_nof_transactions_by_time(self, collection_name, start_time, end_time):
        url = self.url + "event_polling/collection_nof_transactions_by_time"
        data = {
            "collection_name": collection_name,
            "start_time": start_time,
            "end_time": end_time,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_nof_users_in_time_range(self, collection_name, start_time, end_time):
        url = self.url + "event_polling/collection_nof_users_in_time_range"
        data = {
            "collection_name": collection_name,
            "start_time": start_time,
            "end_time": end_time,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_contract_nof_transactions(self, collection_name, contract_address):
        url = self.url + "event_polling/contract_nof_transactions"
        data = {
            "collection_name": collection_name,
            "contract_address": contract_address,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_collection_users_in_time_range(self, collection_name, start_time, end_time):
        url = self.url + "event_polling/collection_users_in_time_range"
        data = {
            "collection_name": collection_name,
            "start_time": start_time,
            "end_time": end_time,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

    def get_contract_users_in_time_range(self, collection_name, contract_address, start_time, end_time):
        url = self.url + "event_polling/contract_users_in_time_range"
        data = {
            "collection_name": collection_name,
            "contract_address": contract_address,
            "start_time": start_time,
            "end_time": end_time,
            "api_key": self.key,
            "user_name": self.username
        }
        response = requests.get(url, params=data, headers=self.headers)
        return response.json()

