"""
app/main.py

FastAPI 应用与路由定义。

包含：
- /ping 健康检查
- /register 用户注册
- /login 用户登录
- /me 获取当前用户（需要 Authorization header）
- /users/count 方便查看用户数量（快速检查用）

关键点注释已写在文件中以便你学习后端请求流和依赖注入。
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select

from app.db import init_db, get_session
from app.models import User
from app.schemas import RegisterIn, TokenOut, UserOut
from app.auth import hash_password, verify_password, create_access_token, get_current_user

# 通过环境变量可关闭自动生成的 docs（生产中建议关闭或在代理层限制访问）
DISABLE_DOCS = os.getenv("DISABLE_DOCS", "0") in ("1", "true", "True")

app = FastAPI(
    title="pushk3n",
    docs_url=None if DISABLE_DOCS else "/docs",
    redoc_url=None if DISABLE_DOCS else "/redoc",
)


@app.on_event("startup")
def on_startup():
    """
    应用启动时自动调用：确保数据库表已经创建（如果不存在则创建）。
    这会在第一次运行时生成 data.db 文件（如果使用 SQLite）。
    """
    init_db()


@app.get("/ping")
def ping() -> dict:
    """健康检查接口，返回固定 pong"""
    return {"msg": "pong"}


@app.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, session = Depends(get_session)):
    """
    用户注册流程：
    - 通过 Depends(get_session) 获取 DB 会话（每请求一个 session)
    - 检查用户名和邮箱是否已存在
    - 哈希密码并写入用户表
    - 返回 JWT(access_token)
    """
    # 检查用户名和邮箱唯一性
    statement_usrname = select(User).where(User.username == payload.username)
    statement_email = select(User).where(User.e_mail == payload.e_mail)
    existing_usrname = session.exec(statement_usrname).first()
    existing_email = session.exec(statement_email).first()
    if existing_usrname:
        raise HTTPException(status_code=400, detail="username exists")
    if existing_email:
        raise HTTPException(status_code=400, detail="email exists")
    
    user = User(username=payload.username, password_hash=hash_password(payload.password), e_mail=payload.e_mail)
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token({"sub": user.username})
    return {"access_token": token}


@app.post("/login", response_model=TokenOut)
def login(payload: RegisterIn, session = Depends(get_session)):
    """
    登录流程：
    - 查找用户并验证密码（使用 passlib 的 verify）
    - 验证通过后签发 JWT 并返回
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
    返回当前登录用户信息。
    - current_user 由 get_current_user 解析 token 并从 DB 加载
    """
    return {"id": current_user.id, "username": current_user.username}


@app.get("/users/count")
def users_count(session = Depends(get_session)):
    """
    快速检查路由：返回用户数量（方便在没有 sqlite GUI 下做快速验证）。
    仅供开发/学习使用。
    """
    statement = select(User)
    users = session.exec(statement).all()
    return {"count": len(users)}