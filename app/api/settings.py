import os
from dotenv import load_dotenv


load_dotenv()


DATA_BASE_URL: str = (f"postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}"
                      f"@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_NAME")}")

