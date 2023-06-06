from datetime import datetime, timedelta
from typing import Annotated

import grpc
import users_pb2
import users_pb2_grpc
import uvicorn
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from models import Token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ALGORITHM = config("ALGORITHM")
SECRET_KEY = config("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)


app = FastAPI()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username, password):
    with grpc.insecure_channel("localhost:" + config("MS2_PORT")) as channel:
        stub = users_pb2_grpc.UsersStub(channel=channel)
        response = stub.AuthenticateUser(
            users_pb2.UserAuthenticationRequest(username=username, password=password)
        )
        return response.user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not bool(user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def run():
    host = config("GATEWAY_HOST")
    port = config("GATEWAY_PORT", cast=int)
    log_level = config("LOG_LEVEL")
    uvicorn.run("server:app", host=host, port=port, log_level=log_level, reload=True)


if __name__ == "__main__":
    run()
