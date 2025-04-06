import uuid


from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet

from api.models import Secret
from api.settings import SECRET_KEY
from api.schemas import SecretKeyMessage, StatusMessage, CreateSecretSchema, BaseSecretSchema


if SECRET_KEY:
    cipher = Fernet(SECRET_KEY)
else:
    raise HTTPException(status_code=500, detail="Something went wrong!")


async def add_secret_to_db(secret_payload: CreateSecretSchema,
                           session: AsyncSession) -> SecretKeyMessage:
    new_secret_payload = secret_payload.model_dump()
    new_secret_payload["secret"] = cipher.encrypt(new_secret_payload["secret"].encode())
    secret_key = str(uuid.uuid4())

    new_secret = Secret(**new_secret_payload, secret_key=secret_key)
    session.add(new_secret)

    try:
        await session.commit()
        return SecretKeyMessage(secret_key=secret_key)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Something went wrong!")


async def get_secret_from_db(secret_key: str,
                             session: AsyncSession) -> BaseSecretSchema:
    secret = await session.execute(select(Secret).where(Secret.secret_key == secret_key))
    secret = secret.fetchone()

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not Found")

    decrypted_secret = cipher.decrypt(secret[0].secret).decode()

    return BaseSecretSchema(secret=decrypted_secret)


async def delete_secret_from_db(secret_key: str,
                                session: AsyncSession) -> StatusMessage:
    secret = await session.execute(select(Secret).where(Secret.secret_key == secret_key))
    secret = secret.fetchone()

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not Found")

    await session.delete(secret)
    await session.commit()

    return StatusMessage(status="secret_deleted")

