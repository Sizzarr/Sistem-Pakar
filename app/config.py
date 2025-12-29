from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "mysql+pymysql://root:@127.0.0.1:3306/sistem_pakar_tidur"
    JWT_SECRET: str = "change-me"
    JWT_EXPIRE_MINUTES: int = 120

    FIRST_ADMIN_EMAIL: str | None = None
    FIRST_ADMIN_PASSWORD: str | None = None

settings = Settings()
