from pydantic import Field
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    bot_token: str = Field()
    plant_token: str = Field()
    deepseek_token : str = Field()
    db_path: str = Field()