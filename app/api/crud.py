import uuid

from typing import Sequence
from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone

from api.log import logger
from api.models import Secret, ServerLog
from api.settings import SECRET_KEY
from api.schemas import SecretKeyMessage, StatusMessage, CreateSecretSchema, BaseSecretSchema


if SECRET_KEY:
    cipher = Fernet(SECRET_KEY)
    logger.info("Ключ шифрования успешно установлен!")
else:
    logger.warning("Ключ шифрования не найден! Установите ключ шифрования через переменную окружения!")
    raise HTTPException(status_code=500, detail="Something went wrong!")


async def add_secret_to_db(secret_payload: CreateSecretSchema,
                           session: AsyncSession, request: Request) -> SecretKeyMessage:
    new_secret_payload = secret_payload.model_dump()
    new_secret_payload["secret"] = cipher.encrypt(new_secret_payload["secret"].encode())

    secret_key = str(uuid.uuid4())

    new_secret = Secret(**new_secret_payload, secret_key=secret_key)
    session.add(new_secret)

    logger.info(new_secret.passphrase)

    try:
        await session.commit()
        logger.info("Секрет успешно создан!")

        await create_server_log(new_secret, "Секрет успешно создан!",
                                request.client.host if request.client else "unknown", session)

        return SecretKeyMessage(secret_key=secret_key)

    except Exception as e:
        await session.rollback()
        logger.warning(f"Произошла ошибка при создании секрета! {e}")
        raise HTTPException(status_code=400, detail="Something went wrong!")


async def get_secret_from_db(secret_key: str, session: AsyncSession,
                             request: Request, passphrase: str | None) -> BaseSecretSchema:
    secret = await session.execute(select(Secret).where(Secret.secret_key == secret_key))
    secret = secret.fetchone()

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not Found")

    logger.info(passphrase)

    if secret[0].passphrase and secret[0].passphrase != passphrase:
        raise HTTPException(status_code=401, detail="Access denied!")

    expire_flag = False

    if secret[0].ttl_seconds and secret[0].ttl_seconds != 0:
        secret_time_created = datetime.fromisoformat(str(secret[0].time_created))
        expire_time = secret_time_created + timedelta(seconds=secret[0].ttl_seconds)
        now = datetime.now(timezone.utc)

        if now > expire_time:
            expire_flag = True

    if secret[0].num_of_readings == 0 and not expire_flag:

        decrypted_secret = cipher.decrypt(secret[0].secret).decode()

        secret[0].num_of_readings += 1
        await session.commit()

        logger.info("Секрет был успешно получен!")

        await create_server_log(secret[0], "Секрет был успешно выдан!",
                                request.client.host if request.client else "unknown", session)

        return BaseSecretSchema(secret=decrypted_secret)
    else:
        raise HTTPException(status_code=404, detail="The secret is not available!")


async def delete_secret_from_db(secret_key: str, session: AsyncSession,
                                request: Request,
                                passphrase: str | None = None) -> StatusMessage:
    secret = await session.execute(select(Secret).where(Secret.secret_key == secret_key))
    secret = secret.fetchone()

    if not secret:
        logger.info("Секрет не был найден!")
        raise HTTPException(status_code=404, detail="Secret not Found")

    if secret[0].passphrase and secret[0].passphrase != passphrase:
        raise HTTPException(status_code=401, detail="Access denied!")

    await create_server_log(secret[0], "Секрет был успешно выдан!",
                            request.client.host if request.client else "unknown", session)

    await session.delete(secret[0])

    try:
        await session.commit()


        logger.info("Секрет был успешно удален!")
    except Exception as e:
        await session.rollback()
        logger.warning("Произошла ошибка при удалении секрета!")
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return StatusMessage(status="secret_deleted")


async def create_server_log(secret: Secret, message: str,
                            ip_address: str, session: AsyncSession) -> ServerLog:
    log = ServerLog(secret=secret, ip_address=ip_address,
                    message=message)

    session.add(log)

    try:
        await session.commit()
        logger.info("Лог успешно создан и сохранен на сервере!")
        return log
    except Exception as e:
        logger.warning("Произошла ошибка при сохранении лога на сервере!")
        raise HTTPException(status_code=500, detail="Something went wrong!")


async def read_server_logs(session: AsyncSession) -> Sequence[ServerLog]:
    logs = await session.execute(select(ServerLog))
    logs = logs.scalars().all()

    return logs

