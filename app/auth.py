"""
app/auth.py
认证相关工具：密码哈希/验证、JWT 生成与解析、以及获取当前用户的 FastAPI 依赖。

说明（重要）:
- 开发环境临时使用 pbkdf2_sha256（纯 Python）作为密码哈希算法，避免在某些系统上编译 bcrypt 的问题。
  这样在 WSL 或一些系统上不会因为 bcrypt 编译/安装失败而导致无法运行。
- 如果你要切回 bcrypt（生产环境常用），在 LEARNING_GUIDE.md 中有完整的恢复步骤。
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import select

from app.db import get_session
from app.models import User

# 从环境变量读取密钥等配置，如果没有设置会使用默认（仅用于开发）
SECRET_KEY = os.getenv("SECRET_KEY", "change_me_now_change")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# 密码哈希策略：开发时使用 pbkdf2_sha256（纯 Python）
# 如需改回 bcrypt，替换为 schemes=["bcrypt"]，并确保系统已正确安装 bcrypt 包（参见 LEARNING_GUIDE.md）
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2PasswordBearer 用于生成 /docs 中的认证表单（tokenUrl 指向实际的登录接口）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hash_password(password: str) -> str:
    """
    将明文密码哈希并返回哈希值（字符串）。
    使用 passlib 的 CryptContext, 调用示例:
      hashed = hash_password("my_password")
    """
    return pwd_ctx.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希匹配，返回 True/False。
    """
    return pwd_ctx.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT token。
    - data: 字典，会被拷贝到 payload 中(例如 {"sub": username})
    - expires_delta: 可选的过期时长(timedelta),默认使用 ACCESS_TOKEN_EXPIRE_MINUTES
    返回: JWT 字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), session = Depends(get_session)) -> User:
    """
    FastAPI 依赖，用于受保护路由中获取当前用户。
    - 从 Authorization header 中读取 Bearer token（oauth2_scheme 完成）
    - 解码 JWT，获取 sub（我们把用户名放在 sub）
    - 从 DB 中加载 User 对象并返回
    抛出 HTTPException(401) 表示认证失败。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise credentials_exception
    return user