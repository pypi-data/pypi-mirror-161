"""
Creation module for OMTool. Used to create and load models from
files and export them into single file.
"""
import os
from pathlib import Path

from omtool.core.configs import CreationConfig
from omtool.core.creation import SnapshotBuilder
from omtool.core.models import initialize_models
from omtool.core.utils import initialize_logger


def create(config: CreationConfig):
    """
    Creation mode for the OMTool. Used to create and load models from
    files and export them into single file.
    """
    initialize_logger(**config.logging)
    models = initialize_models(config.imports.models, config.objects)
    builder = SnapshotBuilder()

    if Path(config.output_file).is_file():
        os.remove(config.output_file)

    for snapshot in models:
        builder.add_snapshot(snapshot)

    builder.to_fits(config.output_file)
