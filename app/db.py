from typing import Generator
import os
from sqlmodel import SQLModel, create_engine, Session

# 从环境变量读取数据库连接字符串（默认 sqlite 文件）
# MySQL 示例: mysql+pymysql://pushk3n:pushk3n@127.0.0.1:3306/mysql_lr?charset=utf8mb4
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
DATABASE_URL="mysql+pymysql://pushk3n:pushk3n@127.0.0.1:3306/mysql_lr?charset=utf8mb4"

# sqlite 需要特殊连接参数以允许多线程共享同一个连接对象
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# 为了提高 MySQL 等数据库的连接稳定性，开启 pool_pre_ping
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)


def init_db() -> None:
    """
    初始化数据库表结构。
    在应用启动时调用一次( app.on_event("startup") 中已经调用) ，会根据 SQLModel 的 model 自动创建表。
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator:
    """
    提供一个数据库会话（Session）的生成器，用于 FastAPI 的依赖注入（Depends）。
    每次请求会创建一个新的 Session 并在结束时关闭。
    """
    with Session(engine) as session:
        yield session