from copy import deepcopy
from datetime import datetime

rooms: dict[int, dict] = {
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

devices: dict[int, dict] = {
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

operation_logs: list[dict] = []

device_events: list[dict] = []

scenes: dict[int, dict] = {
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

schedules: dict[int, dict] = {}

linkage_rules: dict[int, dict] = {}

alarms: dict[int, dict] = {
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

alarm_process_logs: list[dict] = [
    {
        "log_id": 1,
        "alarm_id": 1,
        "handler_id": None,
        "action_type": "notify",
        "process_desc": "系统生成烟雾报警",
        "process_result": "success",
        "created_at": "2026-07-02 00:00:00",
    }
]

self_check_records: list[dict] = []

device_simulations: list[dict] = []


def copy_record(record: dict | None) -> dict | None:
    return deepcopy(record) if record is not None else None


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def next_room_id() -> int:
    return max(rooms.keys(), default=0) + 1


def next_device_id() -> int:
    return max(devices.keys(), default=0) + 1


def next_log_id() -> int:
    return max((log["log_id"] for log in operation_logs), default=0) + 1


def next_device_event_id() -> int:
    return max((event["event_id"] for event in device_events), default=0) + 1


def next_scene_id() -> int:
    return max(scenes.keys(), default=0) + 1


def next_schedule_id() -> int:
    return max(schedules.keys(), default=0) + 1


def next_linkage_rule_id() -> int:
    return max(linkage_rules.keys(), default=0) + 1


def next_alarm_id() -> int:
    return max(alarms.keys(), default=0) + 1


def next_alarm_process_log_id() -> int:
    return max((log["log_id"] for log in alarm_process_logs), default=0) + 1


def next_self_check_id() -> int:
    return max((record["check_id"] for record in self_check_records), default=0) + 1


def next_device_simulation_id() -> int:
    return max((record["simulation_id"] for record in device_simulations), default=0) + 1
