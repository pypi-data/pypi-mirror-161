import hmac
import requests
import hashlib
from firstbatch.utils import EventTypes


class FirstBatchRequests:
    def __init__(self):
        self.base_url = 'https://api.firstbatch.xyz/'
        self.mask = "token_auth"
        self.headers = {}

    def set_header(self, pk: str, bearer: str):
        self.headers = {"pk": pk, "bearer": bearer}

    def __call_get(self, url):
        try:
            r = requests.get(self.base_url + url, headers=self.headers)
            return r.json()
        except:
            raise Exception

    def __call_post(self, url, payload):
        try:
            r = requests.post(self.base_url + url, json=payload, headers=self.headers)
            return r.json()
        except:
            raise Exception

    def auth_sign(self, secret):
        return str(hmac.new(str.encode(self.mask), str.encode(secret), hashlib.sha256).hexdigest())

    def call_auth(self, signed_hash: str, public_key: str):
        url = "auth"
        payload = {'signed_message': signed_hash, 'pk': public_key}
        return self.__call_post(url, payload)

    def call_create_event(self, name: str, event_type: EventTypes):
        url = "create_event"
        payload = {'name': name, 'event_type': event_type}
        return self.__call_post(url, payload)

    def call_create_event_onchain(self, event_id):
        url = "create_event_onchain"
        payload = {"event_id":event_id}
        return self.__call_post(url, payload)

    def call_get_events(self):
        url = "get_events"
        return self.__call_get(url)

    def call_get_event_detail(self, event_id):
        url = "get_event_details_id"
        return self.__call_post(url, payload={"event_id": event_id})

    def call_get_event_linkt(self, event_id):
        url = "get_event_link"
        payload = {"event_id": event_id}
        return self.__call_post(url, payload)

    def call_update_event_state(self, event_id, state):
        url = "update_event_state"
        payload = {"event_id":event_id, "state": state}
        return self.__call_post(url=url, payload=payload)

    def call_add_gate(self, event_id, group_id):
        url = "add_gate"
        payload = {"event_id":event_id, "group_id":group_id}
        return self.__call_post(url, payload)

    def call_add_rule(self, event_id, rules):
        url = "add_rule"
        payload = {"event_id":event_id, "rules":rules}
        return self.__call_post(url, payload)

    def call_create_custom_persona(self, name, logic):
        url = "create_custom_group"
        payload = {"name": name, "logic":logic}
        return self.__call_post(url=url, payload=payload)

    def call_get_custom_personas(self):
        url = "get_custom_personas"
        return self.__call_get(url)

    def call_event_statistics(self, event_id):
        url = "event_statistics"
        payload = {"event_id": event_id}
        return self.__call_post(url=url, payload=payload)
