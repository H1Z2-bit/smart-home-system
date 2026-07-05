from typing import Any

from sqlalchemy import select

from app.models.automation import SceneDeviceAction, SceneMode
from app.repositories.mysql.base import flush_refresh, model_to_dict, session_scope
from app.repositories.scene_repository import SceneRepository


class MySQLSceneRepository(SceneRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        with session_scope() as session:
            scenes = session.scalars(select(SceneMode).where(SceneMode.home_id == home_id).order_by(SceneMode.sort_no, SceneMode.scene_id)).all()
            return [self._scene_dict(session, scene) for scene in scenes]

    def get(self, scene_id: int) -> dict[str, Any] | None:
        with session_scope() as session:
            scene = session.get(SceneMode, scene_id)
            return self._scene_dict(session, scene) if scene else None

    def exists_name(self, home_id: int, scene_name: str, exclude_scene_id: int | None = None) -> bool:
        with session_scope() as session:
            query = select(SceneMode).where(SceneMode.home_id == home_id, SceneMode.scene_name == scene_name.strip())
            if exclude_scene_id is not None:
                query = query.where(SceneMode.scene_id != exclude_scene_id)
            return session.scalar(query.limit(1)) is not None

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        with session_scope() as session:
            scene = SceneMode(
                home_id=home_id,
                scene_name=data["scene_name"],
                enabled=bool(data.get("enabled", True)),
                created_by=data.get("created_by", 1),
            )
            flush_refresh(session, scene)
            self._replace_actions(session, scene.scene_id, data.get("actions") or [])
            session.refresh(scene)
            return self._scene_dict(session, scene)

    def update(self, scene_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        with session_scope() as session:
            scene = session.get(SceneMode, scene_id)
            if scene is None:
                return None
            if "scene_name" in data and data["scene_name"] is not None:
                scene.scene_name = data["scene_name"]
            if "enabled" in data and data["enabled"] is not None:
                scene.enabled = bool(data["enabled"])
            if "actions" in data and data["actions"] is not None:
                self._replace_actions(session, scene_id, data["actions"])
            session.flush()
            session.refresh(scene)
            return self._scene_dict(session, scene)

    def delete(self, scene_id: int) -> bool:
        with session_scope() as session:
            scene = session.get(SceneMode, scene_id)
            if scene is None:
                return False
            session.delete(scene)
            return True

    @staticmethod
    def _replace_actions(session, scene_id: int, actions: list[dict[str, Any]]) -> None:
        for action in session.scalars(select(SceneDeviceAction).where(SceneDeviceAction.scene_id == scene_id)).all():
            session.delete(action)
        session.flush()
        for item in actions:
            session.add(
                SceneDeviceAction(
                    scene_id=scene_id,
                    device_id=item["device_id"],
                    action=item.get("action", "switch"),
                    target_state=item["target_state"],
                    param_value=item.get("param_value"),
                    sort_no=item.get("sort_no", 1),
                )
            )

    @staticmethod
    def _scene_dict(session, scene: SceneMode) -> dict[str, Any]:
        actions = session.scalars(
            select(SceneDeviceAction)
            .where(SceneDeviceAction.scene_id == scene.scene_id)
            .order_by(SceneDeviceAction.sort_no, SceneDeviceAction.action_id)
        ).all()
        return model_to_dict(scene, {"actions": [model_to_dict(action) for action in actions]})

