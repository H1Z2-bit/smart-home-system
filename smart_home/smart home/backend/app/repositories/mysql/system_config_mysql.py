from app.models.system_config import SystemConfig
from app.repositories.entities import SystemConfigEntity
from app.repositories.mysql.base import flush_refresh, session_scope


class MySQLSystemConfigRepository:
    def get_by_home(self, home_id: int) -> SystemConfigEntity:
        with session_scope() as session:
            config = session.query(SystemConfig).filter_by(home_id=home_id).one_or_none()
            if config is None:
                config = SystemConfig(home_id=home_id)
                flush_refresh(session, config)
            return self._to_entity(config)

    def update(self, home_id: int, **kwargs) -> SystemConfigEntity:
        with session_scope() as session:
            config = session.query(SystemConfig).filter_by(home_id=home_id).one_or_none()
            if config is None:
                config = SystemConfig(home_id=home_id)
                session.add(config)
                session.flush()
            for key, value in kwargs.items():
                if value is not None and hasattr(config, key):
                    setattr(config, key, value)
            session.flush()
            session.refresh(config)
            return self._to_entity(config)

    @staticmethod
    def _to_entity(config: SystemConfig) -> SystemConfigEntity:
        return SystemConfigEntity(
            home_id=config.home_id,
            alarm_smoke_threshold=float(config.alarm_smoke_threshold),
            alarm_gas_threshold=float(config.alarm_gas_threshold),
            temperature_high_threshold=float(config.temperature_high_threshold),
            auto_alarm_enabled=bool(config.auto_alarm_enabled),
            simulation_enabled=bool(config.simulation_enabled),
        )
