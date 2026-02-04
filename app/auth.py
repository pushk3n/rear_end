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

# 从环境变量或默认值读取密钥与配置
SECRET_KEY = os.getenv("SECRET_KEY", "change_me_now_change")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# 使用 passlib 的 Context 管理密码哈希算法（这里选择 bcrypt）
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 的 token 获取地址（用于自动生成 docs 中的认证表单），实际登录接口是 /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hash_password(password: str) -> str:
    """
    将明文密码哈希化后返回。永远不要在数据库中保存明文密码。
    """
    return pwd_ctx.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验明文密码与哈希值是否匹配。
    """
    return pwd_ctx.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    基于 `python-jose` 生成 JWT token。

    参数：
    - data: 要放入 token 的 payload（例如 {"sub": username}）
    - expires_delta: 可选的过期时间（默认使用 ACCESS_TOKEN_EXPIRE_MINUTES）

    返回：JWT 字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), session = Depends(get_session)) -> User:
    """
    FastAPI 依赖，用于在需要鉴权的接口中获取当前登录用户。

    工作流程：
    1. 从 Authorization: Bearer <token> 中获取 token（由 oauth2_scheme 完成）
    2. 解码并验证 token（异常会返回 401）
    3. 从 token 的 sub 字段中取出用户名并从数据库查询对应用户记录
    4. 如果用户不存在或 token 无效，抛出 401

    这样在路由中使用 `current_user: User = Depends(get_current_user)` 就可以获得合法用户对象。
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
    # 从数据库查找用户
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise credentials_exception
    return user
