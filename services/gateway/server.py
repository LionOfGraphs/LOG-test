import grpc
import users_pb2
import users_pb2_grpc
import uvicorn
from decouple import Csv, config
from fastapi import FastAPI

app = FastAPI()


@app.get("/user/authenticate")
def authenticate(username, password):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = users_pb2_grpc.UsersStub(channel=channel)
        response = stub.AuthenticateUser(
            users_pb2.UserAuthenticationRequest(username=username, password=password)
        )
        print(response)


def run():
    host, port, log_level = config("GATEWAY_ENDPOINT", cast=Csv())
    uvicorn.run(
        "server:app", host=host, port=int(port), log_level=log_level, reload=True
    )


if __name__ == "__main__":
    run()
