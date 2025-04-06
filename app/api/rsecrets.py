from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from cachetools import TTLCache

from api.log import logger
from api.database import get_session
from api.crud import add_secret_to_db, get_secret_from_db, delete_secret_from_db
from api.schemas import BaseSecretSchema, CreateSecretSchema, StatusMessage, SecretKeyMessage


secrets = APIRouter(tags=["Secrets"], prefix="/secret")

"""
Не стал заморачиваться с Redis.
"""

cache = TTLCache(maxsize=2000, ttl=600)

@secrets.post('', response_model=SecretKeyMessage)
async def create_secret(secret_payload: CreateSecretSchema, request: Request,
                        session: AsyncSession = Depends(get_session)) -> SecretKeyMessage:
    secret_key = await add_secret_to_db(secret_payload, session, request)

    cache[secret_key.secret_key] = secret_payload.model_dump()
    cache[secret_key.secret_key]["num_of_readings"] = 0
    cache[secret_key.secret_key]["time_created"] = str(datetime.now(timezone.utc))

    logger.info(cache[secret_key.secret_key])

    return secret_key


@secrets.get('/{secret_key}', response_model=BaseSecretSchema)
async def get_secret(secret_key: str, request: Request,
                     session: AsyncSession = Depends(get_session),
                     passphrase: Optional[str] = None) -> BaseSecretSchema:

    if secret_key in cache and cache[secret_key]["num_of_readings"] == 0:
        if cache[secret_key]["passphrase"] and cache[secret_key]["passphrase"] != passphrase:
            raise HTTPException(status_code=401, detail="Access Denied!")

        if cache[secret_key]["ttl_seconds"]:
            secret_time_created = datetime.fromisoformat(cache[secret_key]["time_created"])
            expire_time = secret_time_created + timedelta(seconds=cache[secret_key]["ttl_seconds"])
            now = datetime.now(timezone.utc)
            if now > expire_time:
                raise HTTPException(status_code=404, detail="The secret is not available!")

        logger.info("Секрет был взят из кеша!")
        cache[secret_key]["num_of_readings"] += 1
        return BaseSecretSchema(secret=cache[secret_key]["secret"])

    elif secret_key in cache and cache[secret_key]["num_of_readings"] == 1:
        secret = await get_secret_from_db(secret_key, session, request, passphrase)
        raise HTTPException(status_code=404, detail="The secret is not available!")

    secret = await get_secret_from_db(secret_key, session, request, passphrase)
    cache[secret_key] = dict(secret)

    return secret


@secrets.delete('/{secret_key}', response_model=StatusMessage)
async def delete_secret(secret_key: str, request: Request,
                        session: AsyncSession = Depends(get_session),
                        passphrase: Optional[str] = None) -> StatusMessage:
    status = await delete_secret_from_db(secret_key, session, request, passphrase)

    try:
        del cache[secret_key]
    except KeyError:
        pass

    return status

