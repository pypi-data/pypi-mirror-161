from abc import ABC

from omtool.core.datamodel.snapshot import Snapshot


class AbstractModel(ABC):
    def run(self) -> Snapshot:
        raise NotImplementedError
