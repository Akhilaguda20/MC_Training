import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
  
    @property
    def TABLE_NAME(self) -> str:
        return os.environ["TABLE_NAME"]

    @property
    def EVENT_BUS_NAME(self) -> str:
        return os.environ.get("EVENT_BUS_NAME", "user-events-bus")

    @property
    def LOCALSTACK_URL(self) -> str | None:
        return os.environ.get("LOCALSTACK_URL") or None

    @property
    def AWS_REGION(self) -> str:
        return os.environ.get("AWS_REGION", "us-east-1")


settings = Settings()
