import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PG_HOST: str = os.getenv("PG_HOST", "localhost")
    PG_PORT: int = int(os.getenv("PG_PORT", 5432))
    PG_DB: str = os.getenv("PG_DB")
    PG_USER: str = os.getenv("PG_USER")
    PG_PASS: str = os.getenv("PG_PASS")
    S3_SALES_PREFIX: str = os.getenv("S3_SALES_PREFIX", "s3://test-bucket/sales/")
    DEFAULT_TARGET: str = os.getenv("DEFAULT_TARGET", "pyspark")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("1","true","yes")

settings = Settings()
