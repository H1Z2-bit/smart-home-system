import time

from app.repositories.entities import SmsCodeEntity
from app.repositories.mock.account_store import store


class MockSmsCodeRepository:
    def _key(self, phone: str, scene: str) -> str:
        return f"{scene}:{phone}"

    def save(self, phone: str, scene: str, code: str, expires_at: float) -> SmsCodeEntity:
        sms_code = SmsCodeEntity(phone=phone, scene=scene, code=code, expires_at=expires_at)
        store.sms_codes[self._key(phone, scene)] = sms_code
        return sms_code

    def find_latest(self, phone: str, scene: str) -> SmsCodeEntity | None:
        return store.sms_codes.get(self._key(phone, scene))

    def mark_used(self, phone: str, scene: str) -> None:
        sms_code = self.find_latest(phone, scene)
        if sms_code:
            sms_code.used = True

    def increment_attempts(self, phone: str, scene: str) -> None:
        sms_code = self.find_latest(phone, scene)
        if sms_code:
            sms_code.attempts += 1

    def is_expired(self, sms_code: SmsCodeEntity) -> bool:
        return sms_code.expires_at < time.time()
