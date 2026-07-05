from typing import Any

from sqlalchemy import select

from app.models.automation import LinkageRule
from app.repositories.linkage_repository import LinkageRepository
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope


class MySQLLinkageRepository(LinkageRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            rules = session.scalars(select(LinkageRule).where(LinkageRule.home_id == home_id).order_by(LinkageRule.rule_id)).all()
            return [model_to_dict(rule) for rule in rules]

    def get(self, rule_id: int) -> dict[str, Any] | None:
        with session_scope() as session:
            rule = session.get(LinkageRule, rule_id)
            return model_to_dict(rule) if rule else None

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            rule = LinkageRule(
                home_id=home_id,
                rule_name=data["rule_name"],
                trigger_condition=data["trigger_condition"],
                action_config=data["action_config"],
                enabled=bool(data.get("enabled", True)),
                created_by=data.get("created_by", 1),
            )
            flush_refresh(session, rule)
            return model_to_dict(rule)

    def update(self, rule_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        with session_scope() as session:
            rule = session.get(LinkageRule, rule_id)
            if rule is None:
                return None
            for key in ["rule_name", "trigger_condition", "action_config", "enabled", "rule_desc"]:
                if key in data and data[key] is not None:
                    setattr(rule, key, data[key])
            session.flush()
            session.refresh(rule)
            return model_to_dict(rule)

    def delete(self, rule_id: int) -> bool:
        with session_scope() as session:
            rule = session.get(LinkageRule, rule_id)
            if rule is None:
                return False
            session.delete(rule)
            return True

