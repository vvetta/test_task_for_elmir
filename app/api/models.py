from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import mapped_column

from api.database import BaseModel


class Secret(BaseModel):
    secret = mapped_column(String(length=255), nullable=False, unique=False)
    passphrase = mapped_column(String(length=255), nullable=True, unique=False)
    ttl_seconds = mapped_column(Integer(), nullable=True)


class ServerLog(BaseModel):
    pass
