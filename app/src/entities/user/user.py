import uuid
from sqlmodel import SQLModel, Field

from entities.user.user_role import UserRole


class User(SQLModel, table=True):

    id: uuid.UUID = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    surname: str
    hashed_password: str 
    balance: float = Field(default=0.0)
    role: UserRole = Field(default='user')

