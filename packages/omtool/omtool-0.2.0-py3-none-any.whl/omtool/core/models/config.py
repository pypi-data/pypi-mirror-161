import glob
import importlib
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Optional, Type

from amuse.lab import VectorQuantity, units
from zlog import logger

from omtool.core.datamodel import AbstractModel, Snapshot


@dataclass
class ModelConfig:
    name: str
    args: dict[str, Any]
    position: VectorQuantity
    velocity: VectorQuantity
    downsample_to: Optional[int]



@dataclass
class Model:
    name: str
    model: Type


def get_model(models: list[Model], model_name: str, args: dict) -> AbstractModel | None:
    selected_models = [m.model for m in models if m.name == model_name]

    if not selected_models:
        return None

    return selected_models[0](**args)


def load_model(filename: str) -> Model:
    path = pathlib.Path(filename)

    sys.path.append(str(path.parent))
    model_module = importlib.import_module(path.stem)

    res = {
        "model": model_module.model,
        "name": model_module.model_name
        if hasattr(model_module, "model_name")
        else model_module.model.__name__,
    }

    return Model(**res)


def load_models(imports: list[str]) -> list[Model]:
    filenames = []

    for imp in imports:
        filenames.extend(glob.glob(imp))

    models = []
    for filename in filenames:
        model = load_model(filename)
        models.append(model)
        logger.debug().string("name", model.name).string("from", filename).msg("imported model")

    return models


def initialize_models(imports: list[str], configs: list[ModelConfig]) -> list[Snapshot]:
    imported_models = load_models(imports)
    models: list[Snapshot] = []

    for config in configs:
        model = get_model(imported_models, config.name, config.args)

        if model is None:
            (
                logger.warn()
                .string("error", "model not found")
                .string("name", config.name)
                .msg("skipping")
            )
            continue

        snapshot = model.run()
        snapshot.particles.position += config.position
        snapshot.particles.velocity += config.velocity

        if config.downsample_to is not None:
            c = len(snapshot.particles) / config.downsample_to
            snapshot.particles = snapshot.particles[:: int(c)]
            snapshot.particles.mass *= c

        models.append(snapshot)
        (
            logger.info()
            .int("n", len(snapshot.particles))
            .measured_float(
                "total_mass", snapshot.particles.total_mass().value_in(units.MSun), "MSun"
            )
            .msg("added snapshot")
        )

    return models
