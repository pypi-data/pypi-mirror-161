import numpy as np

from omtool.core.datamodel import Snapshot


def barion_filter_action(snapshot: Snapshot) -> Snapshot:
    barion_filter = np.array(snapshot.particles.is_barion, dtype=bool)
    snapshot.particles = snapshot.particles[barion_filter]

    return snapshot
