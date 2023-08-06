import numpy as np

from omtool import visualizer


class VisualizerAction:
    def __init__(self, service: visualizer.VisualizerService):
        self.service = service

    def __call__(self, data: dict[str, np.ndarray], **parameters) -> dict[str, np.ndarray]:
        self.service.plot(data, parameters)

        return data
