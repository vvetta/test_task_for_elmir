from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import Secret
from api.schemas import SecretKeyMessage, StatusMessage, CreateSecretSchema, BaseSecretSchema


async def add_secret_to_db(secret_payload: CreateSecretSchema,
                           session: AsyncSession) -> SecretKeyMessage:
    new_secret = Secret(**secret_payload.model_dump())
    session.add(new_secret)

    try:
        await session.commit()
        return SecretKeyMessage.from_orm(new_secret)

    except Exception as e:
        await session.rollback()
        raise


async def get_secret_from_db(secret_key: str,
                             session: AsyncSession) -> BaseSecretSchema:
    secret = await session.execute(select(Secret).where(Secret.secret_key == secret_key))
    secret = secret.fetchone()

    if not secret:
        raise

    return BaseSecretSchema.from_orm(secret[0])


async def delete_secret_from_db(secret_key: str,
                                session: AsyncSession) -> StatusMessage:
    secret = await session.execute(select(Secret).where(Secret.secret_key == secret_key))
    secret = secret.fetchone()

    if not secret:
        raise

    await session.delete(secret)
    await session.commit()

    return StatusMessage(status="secret_deleted")

