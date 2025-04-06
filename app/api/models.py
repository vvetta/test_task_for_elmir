from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import mapped_column

from api.database import BaseModel


class Secret(BaseModel):
    secret = mapped_column(String(length=255), nullable=False, unique=False)
    secret_key = mapped_column(String(), nullable=False, unique=True)
    passphrase = mapped_column(String(length=255), nullable=True, unique=False)
    ttl_seconds = mapped_column(Integer(), nullable=True)
    num_of_readings = mapped_column(Integer(), nullable=False, default=0)


class ServerLog(BaseModel):
    pass
