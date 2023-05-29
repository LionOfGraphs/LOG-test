import uvicorn
from decouple import Csv, config
from fastapi import FastAPI

# from fastapi import Depends, FastAPI, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()


@app.get("/user/ms2")
async def test():
    # grpc client -> grpc server ms2
    return {"hello": "hello"}


def run():
    host, port, log_level = config("GATEWAY_ENDPOINT", cast=Csv())
    uvicorn.run(
        "server:app", host=host, port=int(port), log_level=log_level, reload=True
    )


if __name__ == "__main__":
    run()
