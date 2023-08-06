import numpy as np
from zlog import logger


def logger_action(
    data: dict[str, np.ndarray], id: str = "msg", print_last: bool = False
) -> dict[str, np.ndarray]:
    """
    Handler that logs ndarrays to the INFO level.
    """
    event = logger.info().string("id", id)

    for key, val in data.items():
        if print_last:
            event = event.float(key, val[-1])
        else:
            event = event.list(key, val.tolist())

    event.send()

    return data
