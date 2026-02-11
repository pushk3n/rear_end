from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False)
    password_hash: str
    e_mail: Optional[str] = Field(default=None, index=True)  # 新增字段，允许空
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
