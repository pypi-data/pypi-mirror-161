from dataclasses import dataclass

from omtool.core.configs.base_config import BaseConfig
from omtool.core.models import ModelConfig


@dataclass
class CreationConfig(BaseConfig):
    output_file: str
    overwrite: bool
    objects: list[ModelConfig]
