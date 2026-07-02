from app.repositories.entities import SystemConfigEntity
from app.repositories.mock.store import store


class MockSystemConfigRepository:
    def get_by_home(self, home_id: int) -> SystemConfigEntity:
        if home_id not in store.configs:
            store.configs[home_id] = SystemConfigEntity(home_id=home_id)
        return store.configs[home_id]

    def update(self, home_id: int, **kwargs) -> SystemConfigEntity:
        config = self.get_by_home(home_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)
        return config