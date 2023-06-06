from typing import Annotated

import grpc
import users_pb2
import users_pb2_grpc
import uvicorn
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import Token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()


def authenticate_user(username, password):
    with grpc.insecure_channel("localhost:" + config("MS2_PORT")) as channel:
        stub = users_pb2_grpc.UsersStub(channel=channel)
        response = stub.AuthenticateUser(
            users_pb2.AuthenticateUserRequest(username=username, password=password)
        )
        return response.token


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    access_token = authenticate_user(form_data.username, form_data.password)
    if not bool(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": access_token, "token_type": "bearer"}


def run():
    host = config("GATEWAY_HOST")
    port = config("GATEWAY_PORT", cast=int)
    log_level = config("LOG_LEVEL")
    uvicorn.run("server:app", host=host, port=port, log_level=log_level, reload=True)


if __name__ == "__main__":
    run()
