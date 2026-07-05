from fastapi import APIRouter

from app.core.config import get_settings
from app.core.security import hash_password
from app.repositories.entities import HomeEntity, MemberEntity, OperationLogEntity, SystemConfigEntity, UserEntity
from app.repositories.mock import store as device_store
from app.repositories.mock.account_store import store as account_store
from app.utils.response import AppException, success_response
from app.utils.time import now_str

router = APIRouter(prefix="/debug", tags=["开发调试"])


def reset_account_mock_data() -> None:
    account_store.users = {
        1: UserEntity(1, "han", "13800000000", hash_password("123456"), "OWNER", phone_verified=True),
        2: UserEntity(2, "member", "13900000000", hash_password("123456"), "MEMBER", phone_verified=True),
        3: UserEntity(3, "guest", "13700000000", hash_password("123456"), "GUEST", phone_verified=True),
        4: UserEntity(4, "maintainer", "13600000000", hash_password("123456"), "MAINTAINER", phone_verified=True),
    }
    account_store.sms_codes = {}
    account_store.homes = {
        1: HomeEntity(1, "演示家庭", "北京市朝阳区", 1, now_str()),
    }
    account_store.members = {
        1: MemberEntity(1, 1, 1, "han", "13800000000", "OWNER", "ACTIVE"),
        2: MemberEntity(2, 1, 2, "member", "13900000000", "MEMBER", "ACTIVE"),
        3: MemberEntity(3, 1, 3, "guest", "13700000000", "GUEST", "ACTIVE"),
    }
    account_store.configs = {1: SystemConfigEntity(home_id=1)}
    account_store.logs = []
    account_store.user_seq = 5
    account_store.home_seq = 2
    account_store.member_seq = 4
    account_store.log_seq = 1


def reset_device_mock_data() -> None:
    device_store.rooms.clear()
    device_store.rooms.update(
        {
            1: {
                "room_id": 1,
                "home_id": 1,
                "room_name": "客厅",
                "room_type": "living_room",
                "remark": "用于智能灯、插座、门磁演示",
            },
            2: {
                "room_id": 2,
                "home_id": 1,
                "room_name": "主卧",
                "room_type": "bedroom",
                "remark": "用于温度传感器演示",
            },
            3: {
                "room_id": 3,
                "home_id": 1,
                "room_name": "厨房",
                "room_type": "kitchen",
                "remark": "用于烟雾和燃气报警演示",
            },
        }
    )

    device_store.devices.clear()
    device_store.devices.update(
        {
            1: {
                "device_id": 1,
                "home_id": 1,
                "room_id": 1,
                "device_name": "客厅灯",
                "device_type": "light",
                "device_status": "off",
                "is_key_device": False,
                "created_at": "2026-07-02 00:00:00",
            },
            2: {
                "device_id": 2,
                "home_id": 1,
                "room_id": 1,
                "device_name": "客厅插座",
                "device_type": "socket",
                "device_status": "off",
                "is_key_device": False,
                "created_at": "2026-07-02 00:00:00",
            },
            3: {
                "device_id": 3,
                "home_id": 1,
                "room_id": 2,
                "device_name": "主卧温度传感器",
                "device_type": "temperature_sensor",
                "device_status": "online",
                "is_key_device": False,
                "created_at": "2026-07-02 00:00:00",
            },
            4: {
                "device_id": 4,
                "home_id": 1,
                "room_id": 3,
                "device_name": "厨房烟雾传感器",
                "device_type": "smoke_sensor",
                "device_status": "online",
                "is_key_device": True,
                "created_at": "2026-07-02 00:00:00",
            },
            5: {
                "device_id": 5,
                "home_id": 1,
                "room_id": 3,
                "device_name": "厨房燃气传感器",
                "device_type": "gas_sensor",
                "device_status": "online",
                "is_key_device": True,
                "created_at": "2026-07-02 00:00:00",
            },
            6: {
                "device_id": 6,
                "home_id": 1,
                "room_id": 1,
                "device_name": "入户门磁",
                "device_type": "door_sensor",
                "device_status": "online",
                "is_key_device": True,
                "created_at": "2026-07-02 00:00:00",
            },
        }
    )

    device_store.operation_logs.clear()
    device_store.device_events.clear()
    device_store.scenes.clear()
    device_store.scenes.update(
        {
            1: {
                "scene_id": 1,
                "home_id": 1,
                "scene_name": "离家模式",
                "enabled": True,
                "actions": [
                    {"device_id": 1, "target_state": "off", "param_value": None, "sort_no": 1},
                    {"device_id": 2, "target_state": "off", "param_value": None, "sort_no": 2},
                ],
                "created_at": "2026-07-02 00:00:00",
            }
        }
    )
    device_store.schedules.clear()
    device_store.linkage_rules.clear()
    device_store.alarms.clear()
    device_store.alarms.update(
        {
            1: {
                "alarm_id": 1,
                "home_id": 1,
                "device_id": 4,
                "alarm_type": "smoke",
                "alarm_level": "warning",
                "trigger_value": "80",
                "alarm_status": "new",
                "trigger_time": "2026-07-02 00:00:00",
                "closed_time": None,
            }
        }
    )
    device_store.alarm_process_logs.clear()
    device_store.alarm_process_logs.append(
        {
            "log_id": 1,
            "alarm_id": 1,
            "handler_id": None,
            "action_type": "notify",
            "process_desc": "系统生成烟雾报警",
            "process_result": "success",
            "created_at": "2026-07-02 00:00:00",
        }
    )
    device_store.self_check_records.clear()
    device_store.device_simulations.clear()


def reset_all_mock_data() -> None:
    reset_account_mock_data()
    reset_device_mock_data()


@router.post("/reset", summary="重置 Mock 演示数据")
def reset_mock_data() -> dict:
    settings = get_settings()
    if settings.app_env.lower() not in {"dev", "test", "local"}:
        raise AppException(403, "debug reset is only available in dev/test/local env")
    reset_all_mock_data()
    return success_response(
        {
            "status": "reset_ok",
            "users": len(account_store.users),
            "homes": len(account_store.homes),
            "members": len(account_store.members),
            "rooms": len(device_store.rooms),
            "devices": len(device_store.devices),
        }
    )
