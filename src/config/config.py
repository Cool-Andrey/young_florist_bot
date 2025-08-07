from pydantic import Field
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    bot_token: str = Field()
    ai_token: str = Field()
