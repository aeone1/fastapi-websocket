'''Config'''
from pydantic import BaseSettings as PydanticBaseSettings
from pydantic import Field


class BaseSettings(PydanticBaseSettings):

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class UvicornSettings(BaseSettings):
    app: str = "api.server:app"
    port: int = Field(default=8080, env="MODULE_PORT")
    debug: bool = True
    reload: bool = True
    host: str = "0.0.0.0"
    log_level: str = "debug"
    use_colors: bool = True
    proxy_headers: bool = True

class GlobalSettings(BaseSettings):
    uvicorn: UvicornSettings = UvicornSettings()


Settings = GlobalSettings()
