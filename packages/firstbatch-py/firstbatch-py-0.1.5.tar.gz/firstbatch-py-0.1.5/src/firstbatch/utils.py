from typing import List


class EventTypes:
    AIRDROP = "Airdrop"
    INTEREST_GATED = "Interest-gated"
    PERSONHOOD = "Personhood"
    ZK_SEGMENTATION = "ZK-Segmentation"


class StateEnum:
    PAUSED = "PAUSED"
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"
    INIT = "INIT"


class Gate:
    def __init__(self, group_id: int):
        self.group_id = int(group_id)


class Rule:
    def __init__(self, address: str, amount: int):
        self.address = address
        self.amount = amount

    def unroll(self):
        return {"address": self.address, "amount": self.amount}


def custom_persona_query(or_groups: List, not_group: List):
    query = ""
    if or_groups is None or len(or_groups) == 0:
        query += "[]"
    for i, g in enumerate(or_groups):
        query += str(g)
        if i < len(or_groups) - 1:
            query += " OR "
    if len(not_group) != 0:
        query += " NOT "
        query += str(not_group)
    return query


class FirstBatchEvent:
    def __init__(self, name, event_id, event_type, state=StateEnum.INIT):
        self.name: str = name
        self.event_id: str = event_id
        self.event_type: EventTypes = event_type
        self.state = state
        self.gate_id: int = 0
        self.rules = []

    def attach_gate(self, gate: Gate):
        self.gate_id = gate.group_id

    def attach_rule(self, rule: Rule):
        self.rules.append(rule.unroll())
