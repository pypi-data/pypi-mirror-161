from typing import Callable

import numpy as np
from amuse.lab import Particles, VectorQuantity, units
from zlog import logger

from omtool.core.utils import pyfalcon_analizer


def center_of_mass(particles: Particles) -> VectorQuantity:
    return particles.center_of_mass()


def center_of_mass_velocity(particles: Particles) -> VectorQuantity:
    return particles.center_of_mass_velocity()


def at_origin(particles: Particles) -> VectorQuantity:
    return [0, 0, 0] | units.kpc


def at_origin_velocity(particles: Particles) -> VectorQuantity:
    return [0, 0, 0] | units.kms


def potential_center(particles: Particles) -> VectorQuantity:
    eps = 0.2 | units.kpc
    top_percent = 0.01

    potentials = pyfalcon_analizer.get_potentials(particles, eps)
    perm = potentials.argsort()
    positions = particles.position[perm]
    positions = positions[: int(len(positions) * top_percent)]
    masses = particles.mass[perm]
    masses = masses[: int(len(masses) * top_percent)]

    return np.sum(positions * masses[:, np.newaxis], axis=0) / np.sum(masses)


def potential_center_velocity(particles: Particles) -> VectorQuantity:
    eps = 0.2 | units.kpc
    top_percent = 0.01

    potentials = pyfalcon_analizer.get_potentials(particles, eps)
    perm = potentials.argsort()
    velocities = particles.velocity[perm]
    velocities = velocities[: int(len(velocities) * top_percent)]
    masses = particles.mass[perm]
    masses = masses[: int(len(masses) * top_percent)]

    return np.sum(velocities * masses[:, np.newaxis], axis=0) / np.sum(masses)


def get(func_name: str) -> Callable[[Particles], VectorQuantity]:
    names = {"mass": center_of_mass, "origin": at_origin, "potential": potential_center}

    if func_name not in names:
        logger.warn(f'Unknown center name "{func_name}", falling back to center of mass.')
        func_name = "mass"

    return names[func_name]


def get_velocity(func_name: str) -> Callable[[Particles], VectorQuantity]:
    names = {
        "mass": center_of_mass_velocity,
        "origin": at_origin_velocity,
        "potential": potential_center_velocity,
    }

    if func_name not in names:
        logger.warn(
            f'Unknown center velocity name "{func_name}", falling back to center of mass velocity.'
        )
        func_name = "mass"

    return names[func_name]
