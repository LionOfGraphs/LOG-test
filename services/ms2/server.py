from concurrent import futures

import grpc
import users_pb2
import users_pb2_grpc
from decouple import config
from models import UserInDB
from passlib.context import CryptContext

fake_users_db = {
    "admin": {
        "user_id": 0,
        "username": "admin",
        "usertype": "admin",
        "full_name": "Administrator",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$5WLUvQ5ws7DTuyqbl/0kIOxOtx9My0AqiR61TZH6EAO5CY0nFpEwW",
        "disabled": False,
    }
}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


class Users(users_pb2_grpc.UsersServicer):
    def AuthenticateUser(self, request, context):
        user = authenticate_user(
            fake_db=fake_users_db, username=request.username, password=request.password
        )
        if user:
            return users_pb2.UserAuthenticationReply(
                user=user.copy(exclude={"hashed_password"}).dict()
            )
        else:
            return users_pb2.UserAuthenticationReply(user=None)


def run():
    port = config("MS2_PORT")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UsersServicer_to_server(Users(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    run()
