from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.crud import add_secret_to_db, get_secret_from_db, delete_secret_from_db
from api.schemas import BaseSecretSchema, CreateSecretSchema, StatusMessage, SecretKeyMessage


secrets = APIRouter(tags=["Secrets"], prefix="/secret")


@secrets.post('', response_model=SecretKeyMessage)
async def create_secret(secret_payload: CreateSecretSchema,
                        session: AsyncSession = Depends(get_session)) -> SecretKeyMessage:
    secret_key = await add_secret_to_db(secret_payload, session)
    return secret_key


@secrets.get('/{secret_key}', response_model=BaseSecretSchema)
async def get_secret(secret_key: str,
                     session: AsyncSession = Depends(get_session)) -> BaseSecretSchema:
    secret = await get_secret_from_db(secret_key, session)
    return secret


@secrets.delete('/{secret_key}', response_model=StatusMessage)
async def delete_secret(secret_key: str,
                        session: AsyncSession = Depends(get_session)) -> StatusMessage:
    status = await delete_secret_from_db(secret_key, session)
    return status

