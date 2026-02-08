from typing import Generator
import os
from sqlmodel import SQLModel, create_engine, Session

# 数据库连接字符串，优先从环境变量读取，默认使用项目根目录下的 SQLite 文件
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

# sqlite 需要特殊连接参数以允许多线程共享同一个连接对象
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# 创建 SQLModel 使用的 engine（统一入口）。生产环境可改为 PostgreSQL/MySQL，只需修改 DATABASE_URL。
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    """
    初始化数据库表结构。
    在应用启动时调用一次( app.on_event("startup") 中已经调用) ，会根据 SQLModel 的 model 自动创建表。
    对于简单项目使用 SQLite 时，这一步会在项目目录生成 data.db 文件.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator:
    """
    提供一个数据库会话（Session）的生成器，用于 FastAPI 的依赖注入（Depends）。

    使用方法（在路由函数中）：
        def endpoint(session = Depends(get_session)):
            session.add(...)
            session.commit()

    这样可以确保每次请求都会创建新的 Session，并在请求结束时自动关闭。
    """
    with Session(engine) as session:
        yield session
