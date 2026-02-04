import os
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select

from app.db import init_db, get_session
from app.models import User
from app.schemas import RegisterIn, TokenOut, UserOut
from app.auth import hash_password, verify_password, create_access_token, get_current_user

# 可通过环境变量关闭自动文档（生产环境可关闭以避免信息泄露）
DISABLE_DOCS = os.getenv("DISABLE_DOCS", "0") in ("1", "true", "True")

# 创建 FastAPI 应用，docs_url/redoc_url 控制是否开启自动文档界面
app = FastAPI(
    title="MyBackend",
    docs_url=None if DISABLE_DOCS else "/docs",
    redoc_url=None if DISABLE_DOCS else "/redoc",
)


@app.on_event("startup")
def on_startup():
    """
    应用启动事件：确保数据库表已创建。
    在第一次运行时会自动创建 SQLite 的 data.db 文件以及所需表。
    """
    init_db()


@app.get("/ping")
def ping():
    """
    健康检查接口，返回固定 pong，用于验证服务是否可用。
    """
    return {"msg": "pong"}


@app.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, session = Depends(get_session)):
    """
    用户注册接口。

    流程：
    1. 检查用户名是否已存在
    2. 哈希密码并写入数据库
    3. 返回 JWT token
    """
    statement = select(User).where(User.username == payload.username)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="username exists")
    user = User(username=payload.username, password_hash=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token({"sub": user.username})
    return {"access_token": token}


@app.post("/login", response_model=TokenOut)
def login(payload: RegisterIn, session = Depends(get_session)):
    """
    用户登录接口。

    验证用户名和密码，正确时返回 JWT。
    """
    statement = select(User).where(User.username == payload.username)
    user = session.exec(statement).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token}


@app.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息。

    依赖 `get_current_user`，会解析 Authorization header 中的 Bearer token 并返回对应用户。
    """
    return {"id": current_user.id, "username": current_user.username}
