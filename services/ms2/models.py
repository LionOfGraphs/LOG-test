from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    username: str
    usertype: str
    full_name: str | None = None
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
