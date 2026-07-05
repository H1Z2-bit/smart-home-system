from typing import Any

from app.core.exceptions import BusinessException
from app.repositories.linkage_repository import LinkageRepository
from app.services.operation_log_service import OperationLogService


class LinkageService:
    def __init__(
        self,
        linkage_repository: LinkageRepository,
        operation_log_service: OperationLogService,
    ):
        self.linkage_repository = linkage_repository
        self.operation_log_service = operation_log_service

    def list_rules(self, home_id: int) -> list[dict[str, Any]]:
        return self.linkage_repository.list_by_home(home_id)

    def create_rule(self, home_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        payload = {
            "rule_name": self._clean_required(data.get("rule_name"), "rule_name 不能为空"),
            "trigger_condition": self._clean_required_dict(
                data.get("trigger_condition"), "trigger_condition 不能为空"
            ),
            "action_config": self._clean_required_dict(data.get("action_config"), "action_config 不能为空"),
            "enabled": bool(data.get("enabled", True)),
            "created_by": operator_id,
        }
        created = self.linkage_repository.create(home_id, payload)
        self._write_log(
            home_id=home_id,
            operator_id=operator_id,
            operation_type="linkage_create",
            operation_object=f"linkage:{created['rule_id']}",
            operation_desc=f"新增联动规则：{created['rule_name']}",
        )
        return created

    def update_rule(self, rule_id: int, data: dict[str, Any], operator_id: int) -> dict[str, Any]:
        current = self.linkage_repository.get(rule_id)
        if current is None:
            raise BusinessException("联动规则不存在", 404)

        payload: dict[str, Any] = {}
        if "rule_name" in data:
            payload["rule_name"] = self._clean_required(data.get("rule_name"), "rule_name 不能为空")
        if "trigger_condition" in data:
            payload["trigger_condition"] = self._clean_required_dict(
                data.get("trigger_condition"), "trigger_condition 不能为空"
            )
        if "action_config" in data:
            payload["action_config"] = self._clean_required_dict(
                data.get("action_config"), "action_config 不能为空"
            )
        if "enabled" in data:
            payload["enabled"] = bool(data.get("enabled"))

        updated = self.linkage_repository.update(rule_id, payload)
        if updated is None:
            raise BusinessException("联动规则不存在", 404)
        self._write_log(
            home_id=updated["home_id"],
            operator_id=operator_id,
            operation_type="linkage_update",
            operation_object=f"linkage:{rule_id}",
            operation_desc=f"修改联动规则：{updated['rule_name']}",
        )
        return updated

    def delete_rule(self, rule_id: int, operator_id: int) -> dict[str, int]:
        rule = self.linkage_repository.get(rule_id)
        if rule is None:
            raise BusinessException("联动规则不存在", 404)
        self.linkage_repository.delete(rule_id)
        self._write_log(
            home_id=rule["home_id"],
            operator_id=operator_id,
            operation_type="linkage_delete",
            operation_object=f"linkage:{rule_id}",
            operation_desc=f"删除联动规则：{rule['rule_name']}",
        )
        return {"rule_id": rule_id}

    def _write_log(
        self,
        home_id: int,
        operator_id: int,
        operation_type: str,
        operation_object: str,
        operation_desc: str,
    ) -> None:
        self.operation_log_service.write_log(
            home_id=home_id,
            operator_id=operator_id,
            operation_type=operation_type,
            operation_object=operation_object,
            operation_result="success",
            operation_desc=operation_desc,
        )

    @staticmethod
    def _clean_required(value: Any, message: str) -> str:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise BusinessException(message, 400)
        return cleaned

    @staticmethod
    def _clean_required_dict(value: Any, message: str) -> dict[str, Any]:
        if not isinstance(value, dict) or not value:
            raise BusinessException(message, 400)
        return value
