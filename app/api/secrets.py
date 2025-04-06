from fastapi import APIRouter
from api.schemas import BaseSecretSchema, CreateSecretSchema, StatusMessage, SecretKeyMessage


secrets = APIRouter(tags=["Secrets"], prefix="/secret")


@secrets.post('', response_model=SecretKeyMessage)
async def create_secret(secret: CreateSecretSchema) -> SecretKeyMessage:
    pass

@secrets.get('/{secret_key}', response_model=BaseSecretSchema)
async def get_secret() -> BaseSecretSchema:
    pass

@secrets.delete('/{secret_key}', response_model=StatusMessage)
async def delete_secret() -> StatusMessage:
    pass

