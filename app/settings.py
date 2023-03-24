import os

from dotenv.main import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    pass


class RDBSettings(Settings):
    host: str = os.environ["RDB_HOST"]
    port: int = os.environ["RDB_PORT"]
    password: str = os.environ["RDB_PASSWORD"]
    db: int = os.environ["RDB_DB"]
