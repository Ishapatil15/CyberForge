import hashlib
import hmac
import re
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
ALLOWED_UPLOAD_EXT = {
    ".zip",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".pcap",
    ".cap",
    ".gz",
    ".7z",
    ".json",
    ".raw",
    ".bin",
    ".log",
    ".csv",
    ".py",
}
ALLOWED_UPLOAD_MIME = {
    "application/zip",
    "application/x-zip-compressed",
    "application/octet-stream",
    "text/plain",
    "image/png",
    "image/jpeg",
    "image/gif",
    "application/pdf",
    "application/vnd.tcpdump.pcap",
    "application/gzip",
    "application/x-7z-compressed",
    "application/json",
    "text/csv",
    "text/x-python",
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": expire}, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return str(payload.get("sub")) if payload.get("sub") else None
    except JWTError:
        return None


def normalize_flag(flag: str) -> str:
    return flag.strip()


def hash_flag(flag: str) -> str:
    settings = get_settings()
    digest = hmac.new(
        settings.flag_pepper.encode("utf-8"),
        normalize_flag(flag).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest


def flags_match(submitted: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_flag(submitted), stored_hash)
