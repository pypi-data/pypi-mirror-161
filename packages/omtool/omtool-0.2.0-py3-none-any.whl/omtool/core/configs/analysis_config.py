from dataclasses import dataclass
from typing import Optional

from omtool import io_service, visualizer
from omtool.core import tasks
from omtool.core.configs.base_config import BaseConfig


@dataclass
class AnalysisConfig(BaseConfig):
    input_file: io_service.IOServiceConfig
    visualizer: Optional[visualizer.VisualizerConfig]
    tasks: list[tasks.TasksConfig]
