from typing import Annotated

import yaml
from pydantic import AfterValidator, BaseModel
from pydantic.networks import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def is_correct_time(time_str: str) -> bool:
    if time_str.endswith("s") or time_str.endswith("m") or time_str.endswith("h"):
        return time_str
    return ValueError("Time must end with 's', 'm', or 'h'")

class Endpoint(BaseModel):
    name: str
    url: AnyUrl
    interval: Annotated[str, AfterValidator(is_correct_time)]
    timeout: int = 3

class Endpoints(BaseModel):
    endpoints: list[Endpoint]
    
    def get_by_interval(self, interval: str) -> list[Endpoint]:
        return [x for x in self.endpoints if x.interval == interval]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    yaml_file: str
    # Set the maximum number of instances to run concurrently for the scheduler
    max_instances: int = 3

def read_yaml(file_path: str) -> dict:
    with open(file_path) as stream:
        config = yaml.safe_load(stream)
    
    return Endpoints(**config)