from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    mongodb_host: str
    mongodb_port: int
    mongodb_name: str
    redis_url: str
    redis_host: str
    api_tickets: str
    api_2gis: str
    api_weather: str


@dataclass
class Settings:
    bots: Bots


def get_settings(path: str) -> Settings:
    env = Env()
    env.read_env()

    return Settings(
        bots=Bots(
            bot_token=env.str("BOT_TOKEN"),
            admin_id=env.int("ADMIN_ID"),
            mongodb_host=env.str("MONGODB_HOST"),
            mongodb_port=env.int("MONGODB_PORT"),
            mongodb_name=env.str("MONGODB_NAME"),
            redis_url=env.str("REDIS_URL"),
            redis_host=env.str("REDIS_HOST"),
            api_tickets=env.str("API_TICKETS"),
            api_2gis=env.str("API_2GIS"),
            api_weather=env.str("API_WEATHER"),
        )
    )


settings = get_settings(".env")
