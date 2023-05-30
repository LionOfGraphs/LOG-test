import uvicorn
from decouple import Csv, config
from fastapi import FastAPI

app = FastAPI()


# @app.post("/token")
# def login_for_access_token():


def run():
    host, port, log_level = config("GATEWAY_ENDPOINT", cast=Csv())
    uvicorn.run(
        "server:app", host=host, port=int(port), log_level=log_level, reload=True
    )


if __name__ == "__main__":
    run()
