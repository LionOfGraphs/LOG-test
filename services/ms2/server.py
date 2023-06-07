from concurrent import futures
from datetime import datetime, timedelta

import grpc
import users_pb2
import users_pb2_grpc
from database import DB_Session
from decouple import config
from jose import jwt
from models import UserInDB
from passlib.context import CryptContext

ALGORITHM = config("ALGORITHM")
SECRET_KEY = config("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_session = DB_Session()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(username: str, password: str):
    hashed_password = db_session.get_user_hash(username=username)
    if not hashed_password:
        return False
    if not verify_password(password, hashed_password):
        return False

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return access_token


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class Users(users_pb2_grpc.UsersServicer):
    def AuthenticateUser(self, request, context):
        access_token = authenticate_user(
            username=request.username, password=request.password
        )
        if access_token:
            return users_pb2.AuthenticateUserResponse(token=access_token)
        else:
            return users_pb2.AuthenticateUserResponse(token=None)


def run():
    port = config("MS2_PORT")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UsersServicer_to_server(Users(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    run()
