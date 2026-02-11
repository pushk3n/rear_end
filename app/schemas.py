from typing import Optional
from pydantic import BaseModel


class RegisterIn(BaseModel):
    """
    注册/登录请求数据结构。
    使用 Pydantic(BaseModel)进行输入校验, FastAPI 会自动校验请求体并给出友好错误信息.
    """
    username: str
    password: str
    e_mail: Optional[str] = None

class LoginIn(BaseModel):
    """
    登录请求数据结构。
    使用 Pydantic(BaseModel)进行输入校验, FastAPI 会自动校验请求体并给出友好错误信息.
    """
    username: str
    password: str

class TokenOut(BaseModel):
    """
    登录/注册成功后返回的 token 结构.
    - access_token: JWT 字符串
    - token_type: token 类型, 默认为 bearer
    """
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """
    对外返回的用户信息结构（用于 /me 接口），避免直接暴露 password_hash 等敏感字段。
    """
    id: int
    username: str
    e_mail: str
