"""
Abstract tasks' classes. Import this if you want to create your own task.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np
from amuse.lab import Particles, ScalarQuantity, units

from omtool.core.datamodel.snapshot import Snapshot

DataType = dict[str, np.ndarray]


def get_parameters(particles: Particles) -> dict:
    """
    Returns parameters of the particle set that can be used in expression evaluation.
    """
    return {
        "x": particles.x,
        "y": particles.y,
        "z": particles.z,
        "vx": particles.vx,
        "vy": particles.vy,
        "vz": particles.vz,
        "m": particles.mass,
    }


class AbstractTask(ABC):
    """
    Base class for the tasks that operate on snapshots.
    """

    @abstractmethod
    def run(self, snapshot: Snapshot) -> DataType:
        """
        Runs the task on given snapshot.
        """
        raise NotImplementedError


class AbstractTimeTask(AbstractTask):
    """
    Base class for all tasks that show evolution of some value over time.
    """

    def __init__(self, value_unit: ScalarQuantity, time_unit: ScalarQuantity = 1 | units.Myr):
        self.time_unit = time_unit
        self.value_unit = value_unit
        self.times: List[ScalarQuantity] = []
        self.values: List[ScalarQuantity] = []

    def _append_value(self, snapshot, value):
        self.times.append(snapshot.timestamp / self.time_unit)
        self.values.append(value / self.value_unit)

    def _as_tuple(self) -> Tuple[np.ndarray, np.ndarray]:
        return (np.array(self.times), np.array(self.values))
