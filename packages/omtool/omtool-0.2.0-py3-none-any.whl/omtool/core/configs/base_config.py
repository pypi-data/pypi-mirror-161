from dataclasses import dataclass
from typing import Any


@dataclass
class ImportsConfig:
    tasks: list[str]
    models: list[str]
    integrators: list[str]


@dataclass
class BaseConfig:
    logging: dict[str, Any]
    imports: ImportsConfig
