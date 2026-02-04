from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """
    用户表模型（使用 SQLModel）

    字段说明：
    - id: 主键，自增
    - username: 用户名，带索引（便于按用户名查找）
    - password_hash: 密码哈希，切勿保存明文密码
    - is_active: 帐号是否激活（可用于软删除或禁用）
    - created_at: 记录创建时间

    说明：把与数据库相关的字段放在 models 中，方便后续迁移到 MySQL/Postgres 时复用模型定义或者根据模型导出建表语句。
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False)
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
