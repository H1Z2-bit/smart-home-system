from app.core.security import hash_password
from app.repositories.entities import HomeEntity, MemberEntity, OperationLogEntity, SmsCodeEntity, SystemConfigEntity, UserEntity
from app.utils.time import now_str


def mock_password() -> str:
    return hash_password("123456")


class MockStore:
    users: dict[int, UserEntity] = {
        1: UserEntity(1, "han", "13800000000", mock_password(), "OWNER", phone_verified=True),
        2: UserEntity(2, "member", "13900000000", mock_password(), "MEMBER", phone_verified=True),
        3: UserEntity(3, "guest", "13700000000", mock_password(), "GUEST", phone_verified=True),
        4: UserEntity(4, "maintainer", "13600000000", mock_password(), "MAINTAINER", phone_verified=True),
    }
    sms_codes: dict[str, SmsCodeEntity] = {}
    homes: dict[int, HomeEntity] = {
        1: HomeEntity(1, "演示家庭", "北京市朝阳区", 1, now_str()),
    }
    members: dict[int, MemberEntity] = {
        1: MemberEntity(1, 1, 1, "han", "13800000000", "OWNER", "ACTIVE"),
        2: MemberEntity(2, 1, 2, "member", "13900000000", "MEMBER", "ACTIVE"),
        3: MemberEntity(3, 1, 3, "guest", "13700000000", "GUEST", "ACTIVE"),
    }
    configs: dict[int, SystemConfigEntity] = {
        1: SystemConfigEntity(home_id=1),
    }
    logs: list[OperationLogEntity] = []
    user_seq: int = 5
    home_seq: int = 2
    member_seq: int = 4
    log_seq: int = 1


store = MockStore()
