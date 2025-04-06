from sqlalchemy import String, Boolean, Integer, LargeBinary, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from api.database import BaseModel


class Secret(BaseModel):
    secret = mapped_column(LargeBinary, nullable=False)
    secret_key = mapped_column(String(), nullable=False, unique=True)
    passphrase = mapped_column(String(length=255), nullable=True, unique=False)
    ttl_seconds = mapped_column(Integer(), nullable=True)
    num_of_readings = mapped_column(Integer(), nullable=False, default=0)

    """
    Тут лучше реализовать "мягкое" удаление через флаг delete.
    Таким образом будет решена проблема связей лога и секрета.
    У меня пока будет так :D.
    """

    logs = relationship("ServerLog", back_populates="secret")


class ServerLog(BaseModel):
    ip_address = mapped_column(String, nullable=False)
    message = mapped_column(String, nullable=False)

    secret_id = mapped_column(Integer,
                              ForeignKey("secret.id", ondelete="SET NULL"), nullable=True)
    secret = relationship("Secret", back_populates="logs")

