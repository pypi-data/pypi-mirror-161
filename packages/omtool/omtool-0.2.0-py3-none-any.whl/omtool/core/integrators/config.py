import glob
import importlib
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Type

from zlog import logger

from omtool.core.datamodel import AbstractIntegrator


@dataclass
class IntegratorConfig:
    name: str
    args: dict[str, Any]


@dataclass
class Integrator:
    name: str
    integrator: Type


def get_integrator(
    integrators: list[Integrator], integrator_name: str, args: dict
) -> AbstractIntegrator | None:
    selected_integrators = [i.integrator for i in integrators if i.name == integrator_name]

    if not selected_integrators:
        return None

    return selected_integrators[0](**args)


def load_integrator(filename: str) -> Integrator:
    path = pathlib.Path(filename)

    sys.path.append(str(path.parent))
    integrator_module = importlib.import_module(path.stem)

    res = {
        "integrator": integrator_module.integrator,
        "name": integrator_module.integrator_name
        if hasattr(integrator_module, "integrator_name")
        else integrator_module.integrator.__name__,
    }

    return Integrator(**res)


def load_integrators(imports: list[str]) -> list[Integrator]:
    filenames = []

    for imp in imports:
        filenames.extend(glob.glob(imp))

    integrators = []
    for filename in filenames:
        integrator = load_integrator(filename)
        integrators.append(integrator)
        (
            logger.debug()
            .string("name", integrator.name)
            .string("from", filename)
            .msg("imported integrator")
        )

    return integrators


def initialize_integrator(imports: list[str], config: IntegratorConfig) -> AbstractIntegrator:
    imported_integrators = load_integrators(imports)

    integrator = get_integrator(imported_integrators, config.name, config.args)
    if integrator is None:
        logger.error().string("name", config.name).msg("integrator not found")
        raise ImportError(f"integrator {config.name} not found")

    logger.debug().string("name", config.name).msg("loaded integrator")
    return integrator
