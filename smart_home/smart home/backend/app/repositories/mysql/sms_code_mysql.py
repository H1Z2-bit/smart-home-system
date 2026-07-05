from datetime import datetime

from sqlalchemy import desc, select

from app.models.user import SmsCode
from app.repositories.entities import SmsCodeEntity
from app.repositories.mysql.base import flush_refresh, session_scope


class MySQLSmsCodeRepository:
    def save(self, phone: str, scene: str, code: str, expires_at: float) -> SmsCodeEntity:
        expires_datetime = datetime.fromtimestamp(expires_at)
        with session_scope() as session:
            sms_code = SmsCode(
                phone=phone,
                scene=scene,
                code=code,
                expires_at=expires_datetime,
                used=False,
                attempts=0,
            )
            flush_refresh(session, sms_code)
            return self._to_entity(sms_code)

    def find_latest(self, phone: str, scene: str) -> SmsCodeEntity | None:
        with session_scope() as session:
            sms_code = session.scalar(
                select(SmsCode)
                .where(SmsCode.phone == phone, SmsCode.scene == scene)
                .order_by(desc(SmsCode.created_at), desc(SmsCode.sms_id))
                .limit(1)
            )
            return self._to_entity(sms_code) if sms_code else None

    def mark_used(self, phone: str, scene: str) -> None:
        with session_scope() as session:
            sms_code = session.scalar(
                select(SmsCode)
                .where(SmsCode.phone == phone, SmsCode.scene == scene)
                .order_by(desc(SmsCode.created_at), desc(SmsCode.sms_id))
                .limit(1)
            )
            if sms_code:
                sms_code.used = True

    def increment_attempts(self, phone: str, scene: str) -> None:
        with session_scope() as session:
            sms_code = session.scalar(
                select(SmsCode)
                .where(SmsCode.phone == phone, SmsCode.scene == scene)
                .order_by(desc(SmsCode.created_at), desc(SmsCode.sms_id))
                .limit(1)
            )
            if sms_code:
                sms_code.attempts += 1

    def is_expired(self, sms_code: SmsCodeEntity) -> bool:
        return sms_code.expires_at < datetime.now().timestamp()

    @staticmethod
    def _to_entity(sms_code: SmsCode) -> SmsCodeEntity:
        return SmsCodeEntity(
            phone=sms_code.phone,
            scene=sms_code.scene,
            code=sms_code.code,
            expires_at=sms_code.expires_at.timestamp(),
            used=bool(sms_code.used),
            attempts=int(sms_code.attempts),
        )
