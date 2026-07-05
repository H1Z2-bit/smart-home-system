from typing import Any

from app.repositories.linkage_repository import LinkageRepository
from app.repositories.mock import store


class MockLinkageRepository(LinkageRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        return [store.copy_record(rule) for rule in store.linkage_rules.values() if rule["home_id"] == home_id]

    def get(self, rule_id: int) -> dict[str, Any] | None:
        return store.copy_record(store.linkage_rules.get(rule_id))

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        rule_id = store.next_linkage_rule_id()
        rule = {
            "rule_id": rule_id,
            "home_id": home_id,
            "rule_name": data["rule_name"],
            "trigger_condition": data["trigger_condition"],
            "action_config": data["action_config"],
            "enabled": data.get("enabled", True),
            "created_by": data.get("created_by", 1),
            "created_at": store.now_text(),
        }
        store.linkage_rules[rule_id] = rule
        return store.copy_record(rule)

    def update(self, rule_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        rule = store.linkage_rules.get(rule_id)
        if rule is None:
            return None
        for key in ["rule_name", "trigger_condition", "action_config", "enabled"]:
            if key in data and data[key] is not None:
                rule[key] = data[key]
        return store.copy_record(rule)

    def delete(self, rule_id: int) -> bool:
        if rule_id not in store.linkage_rules:
            return False
        del store.linkage_rules[rule_id]
        return True
