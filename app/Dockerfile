FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=app_db

CMD sh -c "alembic revision --autogenerate -m 'init' || true && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"

