from dataclasses import dataclass
from typing import Optional

from amuse.lab import ScalarQuantity

from omtool import io_service, visualizer
from omtool.core import tasks
from omtool.core.configs.base_config import BaseConfig
from omtool.core.integrators import IntegratorConfig


@dataclass
class LogParams:
    point_id: int
    logger_id: str


@dataclass
class IntegrationConfig(BaseConfig):
    input_file: io_service.IOServiceConfig
    output_file: str
    overwrite: bool
    model_time: ScalarQuantity
    integrator: IntegratorConfig
    snapshot_interval: int
    visualizer: Optional[visualizer.VisualizerConfig]
    tasks: list[tasks.TasksConfig]
    logs: list[LogParams]

