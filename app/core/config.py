from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    GOOGLE_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
