from pydantic import BaseModel


class BaseSecretSchema(BaseModel):
    secret: str


class CreateSecretSchema(BaseSecretSchema):
    passphrase: str | None
    ttl_seconds: int | None


class SecretKeyMessage(BaseModel):
    secret_key: str


class StatusMessage(BaseModel):
    status: str

