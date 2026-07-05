from typing import Any

from app.repositories.mock import store
from app.repositories.scene_repository import SceneRepository


class MockSceneRepository(SceneRepository):
    def list_by_home(self, home_id: int) -> list[dict[str, Any]]:
        return [store.copy_record(scene) for scene in store.scenes.values() if scene["home_id"] == home_id]

    def get(self, scene_id: int) -> dict[str, Any] | None:
        return store.copy_record(store.scenes.get(scene_id))

    def exists_name(self, home_id: int, scene_name: str, exclude_scene_id: int | None = None) -> bool:
        normalized = scene_name.strip()
        return any(
            scene["home_id"] == home_id
            and scene["scene_name"] == normalized
            and scene["scene_id"] != exclude_scene_id
            for scene in store.scenes.values()
        )

    def create(self, home_id: int, data: dict[str, Any]) -> dict[str, Any]:
        scene_id = store.next_scene_id()
        scene = {
            "scene_id": scene_id,
            "home_id": home_id,
            "scene_name": data["scene_name"],
            "enabled": data.get("enabled", True),
            "actions": data.get("actions", []),
            "created_at": store.now_text(),
        }
        store.scenes[scene_id] = scene
        return store.copy_record(scene)

    def update(self, scene_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        scene = store.scenes.get(scene_id)
        if scene is None:
            return None
        for key in ["scene_name", "enabled", "actions"]:
            if key in data and data[key] is not None:
                scene[key] = data[key]
        return store.copy_record(scene)

    def delete(self, scene_id: int) -> bool:
        if scene_id not in store.scenes:
            return False
        del store.scenes[scene_id]
        return True
