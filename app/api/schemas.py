from typing import Optional
from pydantic import BaseModel, Field


class BaseSecretSchema(BaseModel):
    secret: str


class CreateSecretSchema(BaseSecretSchema):
    passphrase: Optional[str] = Field(
        default=None,
        examples=[None, "my_passphrase"],  # Примеры для документации
        description="Опциональная кодовая фраза"
    )
    ttl_seconds: Optional[int] = Field(
        default=None,
        examples=[None, 3600],
        description="Время жизни секрета в секундах"
    )


class SecretKeyMessage(BaseModel):
    secret_key: str


class StatusMessage(BaseModel):
    status: str

