from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    disabled: bool