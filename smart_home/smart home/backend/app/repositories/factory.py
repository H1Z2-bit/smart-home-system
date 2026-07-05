from app.core.config import settings
from app.repositories.mock.account_operation_log_mock import MockAccountOperationLogRepository
from app.repositories.mock.alarm_mock import MockAlarmRepository
from app.repositories.mock.device_event_mock import MockDeviceEventRepository
from app.repositories.mock.device_mock import MockDeviceRepository
from app.repositories.mock.device_simulation_mock import MockDeviceSimulationRepository
from app.repositories.mock.home_mock import MockHomeRepository
from app.repositories.mock.linkage_mock import MockLinkageRepository
from app.repositories.mock.member_mock import MockMemberRepository
from app.repositories.mock.operation_log_mock import MockOperationLogRepository
from app.repositories.mock.room_mock import MockRoomRepository
from app.repositories.mock.scene_mock import MockSceneRepository
from app.repositories.mock.schedule_mock import MockScheduleRepository
from app.repositories.mock.self_check_mock import MockSelfCheckRepository
from app.repositories.mock.sms_code_mock import MockSmsCodeRepository
from app.repositories.mock.system_config_mock import MockSystemConfigRepository
from app.repositories.mock.user_mock import MockUserRepository
from app.repositories.mysql.account_operation_log_mysql import MySQLAccountOperationLogRepository
from app.repositories.mysql.alarm_mysql import MySQLAlarmRepository
from app.repositories.mysql.device_event_mysql import MySQLDeviceEventRepository
from app.repositories.mysql.device_mysql import MySQLDeviceRepository
from app.repositories.mysql.device_simulation_mysql import MySQLDeviceSimulationRepository
from app.repositories.mysql.home_mysql import MySQLHomeRepository
from app.repositories.mysql.linkage_mysql import MySQLLinkageRepository
from app.repositories.mysql.member_mysql import MySQLMemberRepository
from app.repositories.mysql.operation_log_mysql import MySQLOperationLogRepository
from app.repositories.mysql.room_mysql import MySQLRoomRepository
from app.repositories.mysql.scene_mysql import MySQLSceneRepository
from app.repositories.mysql.schedule_mysql import MySQLScheduleRepository
from app.repositories.mysql.self_check_mysql import MySQLSelfCheckRepository
from app.repositories.mysql.sms_code_mysql import MySQLSmsCodeRepository
from app.repositories.mysql.system_config_mysql import MySQLSystemConfigRepository
from app.repositories.mysql.user_mysql import MySQLUserRepository


def _choose(mock_repository, mysql_repository):
    return mock_repository if settings.use_mock_repository else mysql_repository


user_repository = _choose(MockUserRepository(), MySQLUserRepository())
sms_code_repository = _choose(MockSmsCodeRepository(), MySQLSmsCodeRepository())
home_repository = _choose(MockHomeRepository(), MySQLHomeRepository())
member_repository = _choose(MockMemberRepository(), MySQLMemberRepository())
system_config_repository = _choose(MockSystemConfigRepository(), MySQLSystemConfigRepository())
account_operation_log_repository = _choose(
    MockAccountOperationLogRepository(),
    MySQLAccountOperationLogRepository(),
)

room_repository = _choose(MockRoomRepository(), MySQLRoomRepository())
device_repository = _choose(MockDeviceRepository(), MySQLDeviceRepository())
device_event_repository = _choose(MockDeviceEventRepository(), MySQLDeviceEventRepository())
device_simulation_repository = _choose(
    MockDeviceSimulationRepository(),
    MySQLDeviceSimulationRepository(),
)
operation_log_repository = _choose(MockOperationLogRepository(), MySQLOperationLogRepository())
scene_repository = _choose(MockSceneRepository(), MySQLSceneRepository())
schedule_repository = _choose(MockScheduleRepository(), MySQLScheduleRepository())
linkage_repository = _choose(MockLinkageRepository(), MySQLLinkageRepository())
alarm_repository = _choose(MockAlarmRepository(), MySQLAlarmRepository())
self_check_repository = _choose(MockSelfCheckRepository(), MySQLSelfCheckRepository())


def get_user_repository():
    return user_repository


def get_sms_code_repository():
    return sms_code_repository


def get_home_repository():
    return home_repository


def get_member_repository():
    return member_repository


def get_system_config_repository():
    return system_config_repository


def get_account_operation_log_repository():
    return account_operation_log_repository


def get_room_repository():
    return room_repository


def get_device_repository():
    return device_repository


def get_device_event_repository():
    return device_event_repository


def get_device_simulation_repository():
    return device_simulation_repository


def get_operation_log_repository():
    return operation_log_repository


def get_scene_repository():
    return scene_repository


def get_schedule_repository():
    return schedule_repository


def get_linkage_repository():
    return linkage_repository


def get_alarm_repository():
    return alarm_repository


def get_self_check_repository():
    return self_check_repository
