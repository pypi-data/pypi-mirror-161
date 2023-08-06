from typing import Callable

from omtool.actions_before.barion_filter_action import barion_filter_action
from omtool.actions_before.slice_action import slice_action


def initialize_actions_before() -> dict[str, Callable]:
    return {"slice": slice_action, "barion_filter": barion_filter_action}
