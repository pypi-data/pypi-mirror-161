from firstbatch.request_handler import FirstBatchRequests
from firstbatch.utils import FirstBatchEvent, EventTypes, StateEnum
from firstbatch.maps import RevMap


class FirstBatchClient:
    def __init__(self, public_key, secret):
        self.__requests = FirstBatchRequests()
        self.__public_key = public_key
        self.__secret = secret
        self.__refresh_bearer()
        self.__requests.set_header(pk=self.__public_key, bearer=self.__bearer_token)

    def __refresh_bearer(self):
        response = self.__requests.call_auth(signed_hash=self.__requests.auth_sign(self.__secret),
                                                        public_key=self.__public_key)
        if "error_code" in response:
            raise Exception(response["error_code"], response["message"])
        self.__bearer_token = response["data"]["bearer"]
        self.__requests.set_header(pk=self.__public_key, bearer=self.__bearer_token)

    def __safe_call(self, func, args):
        response = func(**args)
        if "code" in response and response["code"] in ["TOKEN__EXPIRE_TOKEN", "TOKEN__DECODE_ERROR"]:
            self.__refresh_bearer()
            return func(**args)
        elif response["success"] is False:
            raise Exception(response["code"], response["message"])
        else:
            return response

    def get_all_events(self):
        response = self.__safe_call(self.__requests.call_get_events, {})
        return [FirstBatchEvent(name=ev["name"], event_id=ev["event_id"], event_type=ev["event_type"],
                                state=ev["state"]) for ev in response["data"]]

    def get_event(self, event_id: str):
        response = self.__safe_call(self.__requests.call_get_event_detail, {"event_id": event_id})
        event_data = response["data"]
        event = FirstBatchEvent(name=event_data["event_name"], event_id=event_id, event_type=event_data["event_type"],
                               state=event_data["state"])
        event.gate_id = event_data["gate_id"]
        event.rules = event_data["rules"]
        return event

    def create_event(self, name: str, event_type: EventTypes):
        response = self.__safe_call(self.__requests.call_create_event, {"name": name, "event_type": event_type})
        return FirstBatchEvent(name=name, event_id=response["data"]["event_id"], event_type=event_type)

    def boot_event(self, event: FirstBatchEvent):
        return self.__safe_call(self.__requests.call_create_event_onchain, {"event_id":event.event_id})

    def add_gate(self, event: FirstBatchEvent):
        return self.__safe_call(self.__requests.call_add_gate, {"event_id": event.event_id,
                                                                "group_id": event.gate_id, "type": event.event_type})

    def update_rules(self, event: FirstBatchEvent):
        return self.__safe_call(self.__requests.call_add_rule, {"event_id":event.event_id, "rules":event.rules})

    def update_state(self, event: FirstBatchEvent, state: StateEnum):
        response = self.__safe_call(self.__requests.call_update_event_state, {"event_id": event.event_id,
                                                                              "state": state})
        if response["success"]:
            event.state = state
        return response

    def get_statistics(self, event: FirstBatchEvent):
        response = self.__safe_call(self.__requests.call_event_statistics, {"event_id": event.event_id})
        try:
            response["data"] = {RevMap[k]: v for k, v in response["data"]["stats"].items()}
        except Exception as e:
            print("Unknown group id", e)
        else:
            return response

    def get_event_link(self, event: FirstBatchEvent):
        return self.__safe_call(self.__requests.call_get_event_linkt,{"event_id":event.event_id})

    def get_custom_persona(self):
        return self.__safe_call(self.__requests.call_get_custom_personas, {})

    def create_custom_persona(self, name: str, logic: str):
        return self.__safe_call(self.__requests.call_create_custom_persona, {"name":name, "logic":logic})


