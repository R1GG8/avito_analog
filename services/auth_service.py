from datetime import datetime
import hashlib
import os
import secrets
from typing import Optional
import uuid
from fastapi import Request
from sqlalchemy.orm import Session
from models import User


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations=100000
        )
        return f"{salt.hex()}:{key.hex()}"

    @staticmethod
    def verify_password(stored_password_hash: str, provided_password: str) -> bool:
        try:
            salt_hex, key_hex = stored_password_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            key = bytes.fromhex(key_hex)
            new_key = hashlib.pbkdf2_hmac(
                "sha256", provided_password.encode("utf-8"), salt, iterations=100000
            )
            return secrets.compare_digest(key, new_key)
        except Exception:
            return False

    @staticmethod
    def get_current_user(request: Request, db: Session) -> Optional[User]:
        user_id = request.cookies.get("user_id")
        if not user_id:
            return None
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def register_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        password_confirm: Optional[str] = None,
    ) -> User:
        username = username.strip()
        email = email.strip().lower()

        if len(username) < 3:
            raise ValueError("Имя пользователя должно содержать не менее 3 символов")
        if len(password) < 6:
            raise ValueError("Пароль должен содержать минимум 6 символов")
        if password_confirm is not None and password != password_confirm:
            raise ValueError("Пароли не совпадают")

        if db.query(User).filter(User.username == username).first():
            raise ValueError("Пользователь с таким логином уже зарегистрирован")
        if db.query(User).filter(User.email == email).first():
            raise ValueError("Этот Email уже используется")

        user_id = f"user_{uuid.uuid4().hex[:6]}"
        new_user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=AuthService.hash_password(password),
            created_at=datetime.now().isoformat(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username.strip()).first()
        if not user or not AuthService.verify_password(user.password_hash, password):
            raise ValueError("Неверное имя пользователя или пароль")
        return user
