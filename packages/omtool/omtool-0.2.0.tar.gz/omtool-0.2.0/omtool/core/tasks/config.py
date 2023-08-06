import glob
import importlib
import pathlib
import sys
from dataclasses import dataclass
from typing import Callable, Type

from zlog import logger

from omtool.core.datamodel import AbstractTask, HandlerTask


@dataclass
class TasksConfig:
    name: str
    args: dict
    actions_before: list[dict]
    actions_after: list[dict]


@dataclass
class Task:
    name: str
    task: Type


def get_task(tasks: list[Task], task_name: str, args: dict) -> AbstractTask | None:
    selected_tasks = [t.task for t in tasks if t.name == task_name]

    if not selected_tasks:
        return None

    return selected_tasks[0](**args)


def load_task(filename: str) -> Task:
    path = pathlib.Path(filename)

    sys.path.append(str(path.parent))
    task_module = importlib.import_module(path.stem)

    res = {
        "task": task_module.task,
        "name": task_module.task_name
        if hasattr(task_module, "task_name")
        else task_module.task.__name__,
    }

    return Task(**res)


def load_tasks(imports: list[str]) -> list[Task]:
    filenames = []

    for imp in imports:
        filenames.extend(glob.glob(imp))

    tasks = []
    for filename in filenames:
        task = load_task(filename)
        tasks.append(task)
        logger.debug().string("name", task.name).string("from", filename).msg("imported task")

    return tasks


def initialize_tasks(
    imports: list[str],
    configs: list[TasksConfig],
    actions_before: dict[str, Callable],
    actions_after: dict[str, Callable],
) -> list[HandlerTask]:
    imported_tasks = load_tasks(imports)
    tasks: list[HandlerTask] = []

    for config in configs:
        task = get_task(imported_tasks, config.name, config.args)

        if task is None:
            (
                logger.warn()
                .string("error", "task not found")
                .string("name", config.name)
                .msg("skipping")
            )
            continue

        curr_task = HandlerTask(task)

        for action_params in config.actions_before:
            action_name = action_params.pop("type", None)

            if action_name is None:
                logger.error().msg(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is not specified, skipping."
                )
                continue

            if action_name not in actions_before:
                logger.error().msg(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is unknown, skipping."
                )
                continue

            def action(snapshot, name=action_name, params=action_params):
                return actions_before[name](snapshot, **params)

            curr_task.actions_before.append(action)

        for handler_params in config.actions_after:
            handler_name = handler_params.pop("type", None)

            if handler_name is None:
                (
                    logger.error().msg(
                        f"Handler type {handler_name} of the task "
                        f"{type(curr_task.task)} is not specified, skipping."
                    )
                )
                continue

            if handler_name not in actions_after:
                (
                    logger.error().msg(
                        f"Handler type {handler_name} of the task "
                        f"{type(curr_task.task)} is unknown, skipping."
                    )
                )
                continue

            def handler(data, name=handler_name, params=handler_params):
                return actions_after[name](data, **params)

            curr_task.actions_after.append(handler)

        tasks.append(curr_task)
        logger.debug().string("name", config.name).msg("initialized task")

    return tasks
