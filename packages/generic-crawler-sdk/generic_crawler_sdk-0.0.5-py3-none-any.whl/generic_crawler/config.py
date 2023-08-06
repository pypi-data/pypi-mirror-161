import socket

from pydantic import BaseSettings


class Settings(BaseSettings):
    service_root_endpoint: str = "https://generic-crawler-service-ai-sensai.apps.tocpgt01.tcs.turkcell.tgc"


settings = Settings()