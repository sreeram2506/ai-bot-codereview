import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BITBUCKET_USERNAME: Optional[str] = Field(None, env="BITBUCKET_USERNAME")
    BITBUCKET_APP_PASSWORD: Optional[str] = Field(None, env="BITBUCKET_APP_PASSWORD")
    GITHUB_TOKEN: Optional[str] = Field(None, env="GITHUB_TOKEN")
    HF_API_KEY: Optional[str] = Field(None, env="HF_API_KEY")
    HF_MODEL: str = Field("Qwen/Qwen2.5-Coder-7B-Instruct", env="HF_MODEL")
    PORT: int = Field(8000, env="PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
