from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ROOT = Path(__file__).resolve().parents[1]
KEY_DIR = ROOT / "keys"
PRIVATE_KEY = KEY_DIR / "private_key.pem"
PUBLIC_KEY = KEY_DIR / "public_key.pem"


def main() -> None:
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    if PRIVATE_KEY.exists() or PUBLIC_KEY.exists():
        raise SystemExit("keys already exist, remove old key files first if you want to regenerate them")

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    PRIVATE_KEY.write_bytes(private_bytes)
    PUBLIC_KEY.write_bytes(public_bytes)
    print(f"created {PRIVATE_KEY}")
    print(f"created {PUBLIC_KEY}")


if __name__ == "__main__":
    main()