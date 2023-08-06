"""
Struct that holds abstract_task, its part and actions.
"""
from typing import Callable, List

import numpy as np

from omtool.core.datamodel.abstract_task import AbstractTask
from omtool.core.datamodel.snapshot import Snapshot

DataType = dict[str, np.ndarray]


class HandlerTask:
    """
    Struct that holds abstract_task, its part and actions.
    """

    def __init__(
        self,
        task: AbstractTask,
        actions_before: List[Callable[[Snapshot], Snapshot]] = None,
        actions_after: List[Callable[[DataType], DataType]] = None,
    ):
        actions_before = actions_before or []
        actions_after = actions_after or []

        self.task = task
        self.actions_before = actions_before
        self.actions_after = actions_after

    def run(self, snapshot: Snapshot):
        """
        Run actions before, launch task, run actions after.
        """
        for action in self.actions_before:
            snapshot = action(snapshot)

        data = self.task.run(snapshot)

        for handler in self.actions_after:
            data = handler(data)
